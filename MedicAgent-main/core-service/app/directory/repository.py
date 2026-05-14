from typing import Dict, List, Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session, joinedload

from . import models, schemas

class DirectoryRepository:
    """
    Lớp Repository chịu trách nhiệm cho tất cả các tương tác với database
    liên quan đến các thực thể của Directory Service.
    """
    def get_hospital_by_id(self, db: Session, hospital_id: int) -> Optional[models.Hospital]:
        return db.query(models.Hospital).filter(models.Hospital.hospital_id == hospital_id).first()

    def get_all_hospitals(self, db: Session, skip: int = 0, limit: int = 100) -> List[models.Hospital]:
        return db.query(models.Hospital).offset(skip).limit(limit).all()

    def create_hospital(self, db: Session, hospital_in: schemas.HospitalCreate) -> models.Hospital:
        db_hospital = models.Hospital(**hospital_in.dict())
        db.add(db_hospital)
        db.commit()
        db.refresh(db_hospital)
        return db_hospital

    def update_hospital(self, db: Session, db_hospital: models.Hospital, hospital_in: schemas.HospitalUpdate) -> models.Hospital:
        update_data = hospital_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_hospital, key, value)
        db.add(db_hospital)
        db.commit()
        db.refresh(db_hospital)
        return db_hospital

    def delete_hospital(self, db: Session, db_hospital: models.Hospital) -> models.Hospital:
        db.delete(db_hospital)
        db.commit()
        return db_hospital

    # --- SERVICE CATALOG + PRICING ---
    def get_categories_by_hospital(
        self,
        db: Session,
        hospital_id: int,
        include_global: bool = True,
        include_inactive: bool = False,
    ) -> List[models.ServiceCategory]:
        query = db.query(models.ServiceCategory)
        if include_global:
            query = query.filter(
                or_(
                    models.ServiceCategory.hospital_id == hospital_id,
                    models.ServiceCategory.hospital_id.is_(None),
                )
            )
        else:
            query = query.filter(models.ServiceCategory.hospital_id == hospital_id)

        if not include_inactive:
            query = query.filter(models.ServiceCategory.status == 1)

        return query.order_by(models.ServiceCategory.name.asc()).all()

    def get_category_by_id(self, db: Session, category_id: int) -> Optional[models.ServiceCategory]:
        return db.query(models.ServiceCategory).filter(models.ServiceCategory.category_id == category_id).first()

    def create_category(self, db: Session, hospital_id: int, category_in: schemas.ServiceCategoryCreate) -> models.ServiceCategory:
        db_category = models.ServiceCategory(hospital_id=hospital_id, **category_in.dict(exclude_unset=True))
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category

    def update_category(self, db: Session, db_category: models.ServiceCategory, category_in: schemas.ServiceCategoryUpdate) -> models.ServiceCategory:
        update_data = category_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_category, key, value)
        db.add(db_category)
        db.commit()
        db.refresh(db_category)
        return db_category

    def delete_category(self, db: Session, db_category: models.ServiceCategory) -> None:
        db.delete(db_category)
        db.commit()

    def get_services_by_hospital(
        self,
        db: Session,
        hospital_id: int,
        include_inactive: bool = False,
    ) -> List[models.Service]:
        query = db.query(models.Service).options(joinedload(models.Service.categories))
        query = query.filter(models.Service.hospital_id == hospital_id)
        if not include_inactive:
            query = query.filter(models.Service.status == 1)
        return query.order_by(models.Service.name.asc()).all()

    def get_service_by_id(self, db: Session, service_id: int) -> Optional[models.Service]:
        return (
            db.query(models.Service)
            .options(
                joinedload(models.Service.categories),
                joinedload(models.Service.prices),
            )
            .filter(models.Service.service_id == service_id)
            .first()
        )

    def _load_categories_for_service(
        self, db: Session, hospital_id: int, category_ids: Optional[List[int]]
    ) -> List[models.ServiceCategory]:
        if not category_ids:
            return []
        return (
            db.query(models.ServiceCategory)
            .filter(
                models.ServiceCategory.category_id.in_(category_ids),
                or_(
                    models.ServiceCategory.hospital_id == hospital_id,
                    models.ServiceCategory.hospital_id.is_(None),
                ),
            )
            .all()
        )

    def create_service(self, db: Session, hospital_id: int, service_in: schemas.ServiceCreate) -> models.Service:
        categories = self._load_categories_for_service(db, hospital_id, service_in.category_ids)
        db_service = models.Service(
            hospital_id=hospital_id,
            code=service_in.code,
            name=service_in.name,
            description=service_in.description,
            aliases=service_in.aliases,
            status=service_in.status if service_in.status is not None else 1,
            categories=categories,
        )
        db.add(db_service)
        db.commit()
        db.refresh(db_service)
        return db_service

    def update_service(
        self,
        db: Session,
        db_service: models.Service,
        service_in: schemas.ServiceUpdate,
        hospital_id: Optional[int] = None,
    ) -> models.Service:
        update_data = service_in.dict(exclude_unset=True)
        category_ids = update_data.pop("category_ids", None)
        if category_ids is not None:
            db_service.categories = self._load_categories_for_service(
                db, hospital_id or db_service.hospital_id, category_ids
            )

        for key, value in update_data.items():
            setattr(db_service, key, value)

        db.add(db_service)
        db.commit()
        db.refresh(db_service)
        return db_service

    def delete_service(self, db: Session, db_service: models.Service) -> None:
        db.delete(db_service)
        db.commit()

    def get_prices_by_service(
        self,
        db: Session,
        service_id: int,
        include_inactive: bool = False,
    ) -> List[models.ServicePrice]:
        query = db.query(models.ServicePrice).filter(models.ServicePrice.service_id == service_id)
        if not include_inactive:
            query = query.filter(models.ServicePrice.status == 1)
        return query.order_by(models.ServicePrice.effective_from.desc()).all()

    def get_service_price_by_id(self, db: Session, price_id: int) -> Optional[models.ServicePrice]:
        return db.query(models.ServicePrice).filter(models.ServicePrice.price_id == price_id).first()

    def create_service_price(
        self,
        db: Session,
        service_id: int,
        price_in: schemas.ServicePriceCreate,
    ) -> models.ServicePrice:
        db_price = models.ServicePrice(
            service_id=service_id,
            hospital_id=price_in.hospital_id,
            price=price_in.price,
            currency=price_in.currency or "VND",
            payer_type=price_in.payer_type,
            area_tag=price_in.area_tag,
            effective_from=price_in.effective_from,
            effective_to=price_in.effective_to,
            notes=price_in.notes,
            status=price_in.status if price_in.status is not None else 1,
        )
        db.add(db_price)
        db.commit()
        db.refresh(db_price)
        return db_price

    def update_service_price(
        self,
        db: Session,
        db_price: models.ServicePrice,
        price_in: schemas.ServicePriceUpdate,
    ) -> models.ServicePrice:
        update_data = price_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_price, key, value)
        db.add(db_price)
        db.commit()
        db.refresh(db_price)
        return db_price

    # --- Các phương thức cho logic nghiệp vụ ---

    def get_kiosk_info(self, db: Session, kiosk_id: int) -> Optional[models.Kiosk]:
        return db.query(models.Kiosk).options(joinedload(models.Kiosk.hospital)).filter(models.Kiosk.kiosk_id == kiosk_id).first()

    def get_active_departments_by_hospital(self, db: Session, hospital_id: int) -> List[models.Department]:
        return db.query(models.Department).filter(
            models.Department.hospital_id == hospital_id, 
            models.Department.status == 1
        ).all()

    def get_active_rooms_by_department(self, db: Session, department_id: int) -> List[models.ExaminationRoom]:
        return db.query(models.ExaminationRoom).options(
            joinedload(models.ExaminationRoom.service_packages)
        ).filter(
            models.ExaminationRoom.department_id == department_id,
            models.ExaminationRoom.status == 1
        ).all()

    def get_active_service_packages_by_department(self, db: Session, department_id: int) -> List[models.ServicePackage]:
        return db.query(models.ServicePackage).join(
            models.ServicePackage.examination_rooms
        ).filter(
            models.ExaminationRoom.department_id == department_id,
            models.ExaminationRoom.status == 1,
            models.ServicePackage.status == 1
        ).distinct().all()
    
    def get_active_rooms_by_department_and_service(
        self, db: Session, department_id: int, service_package_id: int
    ) -> List[models.ExaminationRoom]:
        return db.query(models.ExaminationRoom).options(
            joinedload(models.ExaminationRoom.service_packages)
        ).join(
            models.ExaminationRoom.service_packages
        ).filter(
            models.ExaminationRoom.department_id == department_id,
            models.ServicePackage.service_package_id == service_package_id,
            models.ExaminationRoom.status == 1,
            models.ServicePackage.status == 1
        ).all()

    # --- CRUD cho ServicePackage (MỚI) ---

    def get_service_package_by_id(self, db: Session, package_id: int) -> Optional[models.ServicePackage]:
        return db.query(models.ServicePackage).filter(models.ServicePackage.service_package_id == package_id).first()

    def get_all_service_packages(self, db: Session, skip: int = 0, limit: int = 100) -> List[models.ServicePackage]:
        return db.query(models.ServicePackage).offset(skip).limit(limit).all()

    def create_service_package(self, db: Session, package_in: schemas.ServicePackageCreate) -> models.ServicePackage:
        db_package = models.ServicePackage(**package_in.dict())
        db.add(db_package)
        db.commit()
        db.refresh(db_package)
        return db_package

    def update_service_package(self, db: Session, db_package: models.ServicePackage, package_in: schemas.ServicePackageUpdate) -> models.ServicePackage:
        update_data = package_in.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_package, key, value)
        db.add(db_package)
        db.commit()
        db.refresh(db_package)
        return db_package

    def delete_service_package(self, db: Session, db_package: models.ServicePackage) -> models.ServicePackage:
        db.delete(db_package)
        db.commit()
        return db_package
    
    def get_room_by_id(self, db: Session, room_id: int) -> Optional[models.ExaminationRoom]:
        return db.query(models.ExaminationRoom).filter(models.ExaminationRoom.room_id == room_id).first()
    
    def get_department_by_id(self, db: Session, department_id: int) -> Optional[models.Department]:
        return db.query(models.Department).filter(models.Department.department_id == department_id).first()
    
    def get_service_package_by_id(self, db: Session, service_package_id: int) -> Optional[models.ServicePackage]:
        return db.query(models.ServicePackage).filter(models.ServicePackage.service_package_id == service_package_id).first()

    def get_active_service_packages_by_hospital(self, db: Session, hospital_id: int) -> List[models.ServicePackage]:
        return db.query(models.ServicePackage).join(
            models.ServicePackage.hospitals
        ).filter(
            models.Hospital.hospital_id == hospital_id,
            models.ServicePackage.status == 1
        ).all()
    
    def get_emergency_department_by_hospital(self, db: Session, hospital_id: int) -> Optional[models.Department]:
        search_term_vn = '%cấp cứu%'
        search_term_en = '%emergency%'
        
        return db.query(models.Department).filter(
            models.Department.hospital_id == hospital_id,
            or_(
                func.lower(models.Department.name).like(search_term_vn),
                func.lower(models.Department.name).like(search_term_en)
            ),
            models.Department.status == 1
        ).first()
    
    def get_departments_by_service_package(
        self, db: Session, hospital_id: int, service_package_id: int
    ) -> List[models.Department]:
        return db.query(models.Department).join(
            models.Department.examination_rooms
        ).join(
            models.ExaminationRoom.service_packages
        ).filter(
            models.Department.hospital_id == hospital_id,
            models.ServicePackage.service_package_id == service_package_id,
            models.Department.status == 1,
            models.ExaminationRoom.status == 1,
            models.ServicePackage.status == 1
        ).distinct().all()

    # --- TRIAGE SYNDROME MAPPINGS ---

    def get_syndrome_mapping_by_id(
        self, db: Session, mapping_id: int
    ) -> Optional[models.SyndromeTriageMapping]:
        return (
            db.query(models.SyndromeTriageMapping)
            .options(joinedload(models.SyndromeTriageMapping.department))
            .filter(models.SyndromeTriageMapping.mapping_id == mapping_id)
            .first()
        )

    def get_syndrome_mappings_by_hospital(
        self, db: Session, hospital_id: int, include_inactive: bool = False
    ) -> List[Dict[str, object]]:
        query = (
            db.query(models.SyndromeTriageMapping)
            .options(joinedload(models.SyndromeTriageMapping.department))
            .filter(models.SyndromeTriageMapping.hospital_id == hospital_id)
            .order_by(
                models.SyndromeTriageMapping.syndrome_id,
                models.SyndromeTriageMapping.priority,
                models.SyndromeTriageMapping.mapping_id,
            )
        )
        if not include_inactive:
            query = query.filter(models.SyndromeTriageMapping.status == 1)

        rows = query.all()

        grouped: Dict[str, Dict[str, object]] = {}
        for row in rows:
            key = row.syndrome_id
            if key not in grouped:
                grouped[key] = {
                    "syndrome_id": row.syndrome_id,
                    "syndrome_name": row.syndrome_name,
                    "triage_units": [],
                }
            entry = grouped[key]
            if not entry.get("syndrome_name") and row.syndrome_name:
                entry["syndrome_name"] = row.syndrome_name

            display_name = row.name_override
            if not display_name and row.department:
                display_name = row.department.name

            entry["triage_units"].append(
                {
                    "mapping_id": row.mapping_id,
                    "triage_unit_id": str(row.triage_unit_id or row.department_id or row.mapping_id),
                    "department_id": row.department_id,
                    "name": display_name,
                    "priority": row.priority,
                    "score_multiplier": row.score_multiplier,
                    "status": row.status,
                }
            )

        return list(grouped.values())

    def create_syndrome_mapping(
        self,
        db: Session,
        hospital_id: int,
        mapping_in: schemas.SyndromeTriageUnitCreate,
    ) -> models.SyndromeTriageMapping:
        data = mapping_in.dict(exclude_unset=True)
        triage_unit_id = data.get("triage_unit_id")
        department_id = data.get("department_id")

        if not triage_unit_id and department_id is not None:
            triage_unit_id = str(department_id)

        db_mapping = models.SyndromeTriageMapping(
            hospital_id=hospital_id,
            syndrome_id=data["syndrome_id"],
            syndrome_name=data.get("syndrome_name"),
            triage_unit_id=triage_unit_id,
            department_id=department_id,
            name_override=data.get("name_override"),
            priority=data.get("priority", 1),
            score_multiplier=data.get("score_multiplier", 1.0),
            status=data.get("status", 1),
        )
        db.add(db_mapping)
        db.commit()
        db.refresh(db_mapping)
        return db_mapping

    def update_syndrome_mapping(
        self,
        db: Session,
        db_mapping: models.SyndromeTriageMapping,
        mapping_in: schemas.SyndromeTriageUnitUpdate,
    ) -> models.SyndromeTriageMapping:
        update_data = mapping_in.dict(exclude_unset=True)

        if "department_id" in update_data:
            new_department = update_data["department_id"]
            if update_data.get("triage_unit_id") is None and new_department is not None:
                update_data["triage_unit_id"] = str(new_department)

        for key, value in update_data.items():
            setattr(db_mapping, key, value)

        db.add(db_mapping)
        db.commit()
        db.refresh(db_mapping)
        return db_mapping

    def delete_syndrome_mapping(
        self, db: Session, db_mapping: models.SyndromeTriageMapping
    ) -> None:
        db.delete(db_mapping)
        db.commit()
    
    def get_general_department_by_hospital(self, db: Session, hospital_id: int) -> Optional[models.Department]:
        #TODO: Cần thay đổi logic phù hợp hơn
        # update db với cờ chỉ khoa/phòng tiếp nhận ban đầu, các bệnh viện có thể đặt tên khác nhau
        """
        Tìm khoa khám bệnh đang hoạt động của bệnh viện.
        """
        search_term_1 = '%khám bệnh%'
        
        return db.query(models.Department).filter(
            models.Department.hospital_id == hospital_id,
            or_(
                func.lower(models.Department.name).like(search_term_1)
            ),
            models.Department.status == 1
        ).first()
    
    def get_zones_by_department_name(self, db: Session, department_name: str, hospital_id:int) -> List[models.Zone]:
        """
        Tìm Khu dựa trên tên Khoa
        """
        search = f"%{department_name}%"
        return db.query(models.Zone).join(
            models.Department
        ).filter(
            models.Department.name.ilike(search),
            models.Department.hospital_id == hospital_id,
            models.Department.status == 1
        ).distinct().all()

    def get_zones_by_room_number(self, db: Session, room_number: str, hospital_id:int) -> List[models.Zone]:
        """
        Tìm Khu dựa trên tên/số Phòng
        Logic: Phòng -> Khoa -> Khu
        """
        search = f"%{room_number}%"
        return db.query(models.Zone).join(
            models.Department
        ).join(
            models.ExaminationRoom
        ).filter(
            models.ExaminationRoom.room_number.ilike(search),
            models.Department.hospital_id == hospital_id,
            models.Department.status == 1,
            models.ExaminationRoom.status == 1
        ).distinct().all()

    def get_room_location_by_name(self, db: Session, room_number: str, hospital_id: int) -> List[models.ExaminationRoom]:
        """
        Lấy vị trí phòng (location_description) theo tên phòng
        """
        search = f"%{room_number}%"
        return db.query(models.ExaminationRoom).options(
            joinedload(models.ExaminationRoom.department).joinedload(models.Department.hospital)
        ).filter(
            models.ExaminationRoom.room_number.ilike(search),
            models.Department.hospital_id == hospital_id,
            models.Department.status == 1,
            models.ExaminationRoom.status == 1
        ).all()

    # --- PRICE LOOKUP HELPERS ---
    def get_service_by_code(self, db: Session, hospital_id: int, code: str) -> Optional[models.Service]:
        return (
            db.query(models.Service)
            .options(joinedload(models.Service.categories))
            .filter(
                models.Service.hospital_id == hospital_id,
                models.Service.code == code,
                models.Service.status == 1,
            )
            .first()
        )

    def search_services_by_keyword(
        self,
        db: Session,
        hospital_id: int,
        keyword: str,
        limit: int = 5,
    ) -> List[models.Service]:
        term = f"%{keyword.lower()}%"
        return (
            db.query(models.Service)
            .outerjoin(models.Service.categories)
            .options(joinedload(models.Service.categories))
            .filter(
                models.Service.hospital_id == hospital_id,
                models.Service.status == 1,
                or_(
                    func.lower(models.Service.name).like(term),
                    func.lower(models.Service.aliases).like(term),
                    func.lower(models.Service.code).like(term),
                    func.lower(models.ServiceCategory.name).like(term),
                ),
            )
            .order_by(models.Service.name.asc())
            .limit(limit)
            .all()
        )

    def get_prices_effective(
        self,
        db: Session,
        service_id: int,
        payer_type: Optional[str] = None,
        area_tag: Optional[str] = None,
        effective_date: Optional[str] = None,
    ) -> List[models.ServicePrice]:
        query = db.query(models.ServicePrice).filter(
            models.ServicePrice.service_id == service_id,
            models.ServicePrice.status == 1,
        )
        if payer_type:
            query = query.filter(models.ServicePrice.payer_type == payer_type)
        if area_tag:
            query = query.filter(models.ServicePrice.area_tag == area_tag)
        if effective_date:
            query = query.filter(
                models.ServicePrice.effective_from <= effective_date,
                or_(
                    models.ServicePrice.effective_to.is_(None),
                    models.ServicePrice.effective_to >= effective_date,
                ),
            )
        return query.order_by(models.ServicePrice.effective_from.desc()).all()

repo = DirectoryRepository()    
