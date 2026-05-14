# core-service/app/directory/router.py

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.servicelogs.servicelogger import logger

from . import schemas
from .db import get_db
from .repository import repo

router = APIRouter()


@router.get("/kiosks/{kiosk_id}/info", response_model=schemas.KioskInfoResponse, summary="Lấy thông tin cấu hình cho Kiosk")
def get_kiosk_startup_info(kiosk_id: int, db: Session = Depends(get_db)):
    kiosk_info = repo.get_kiosk_info(db, kiosk_id=kiosk_id)
    if not kiosk_info:
        logger.warning(f"Attempted to get info for non-existent kiosk_id: {kiosk_id}")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Kiosk not found")
    return kiosk_info

@router.get("/hospitals/{hospital_id}/departments", response_model=List[schemas.Department], summary="Lấy danh sách khoa của bệnh viện")
def get_hospital_departments(hospital_id: int, db: Session = Depends(get_db)):
    return repo.get_active_departments_by_hospital(db, hospital_id=hospital_id)
@router.get(
    "/hospitals/{hospital_id}/departments/simple", 
    response_model=List[schemas.DepartmentSimple], 
    summary="Lấy danh sách khoa của bệnh viện (chỉ lấy tên)"
)
def get_hospital_departments_simple(hospital_id: int, db: Session = Depends(get_db)):
    return repo.get_active_departments_by_hospital(db, hospital_id=hospital_id)

@router.get("/departments/{department_id}/service-packages", response_model=List[schemas.ServicePackage], summary="Lấy danh sách gói dịch vụ của khoa")
def get_department_service_packages(department_id: int, db: Session = Depends(get_db)):
    packages = repo.get_active_service_packages_by_department(db, department_id=department_id)
    if not packages:
        logger.warning(f"No active service packages found for department_id: {department_id}")
    return packages

@router.get("/departments/{department_id}/rooms", response_model=List[schemas.ExaminationRoom], summary="Lấy danh sách phòng khám của khoa")
def get_department_rooms(department_id: int, db: Session = Depends(get_db)):
    return repo.get_active_rooms_by_department(db, department_id=department_id)
@router.get(
    "/departments/{department_id}/service-packages/{service_package_id}/rooms",
    response_model=List[schemas.ExaminationRoom],
    summary="Lấy phòng khám theo khoa và gói dịch vụ"
)
def get_rooms_by_department_and_service(
    department_id: int, 
    service_package_id: int, 
    db: Session = Depends(get_db)
):
    rooms = repo.get_active_rooms_by_department_and_service(
        db, department_id=department_id, service_package_id=service_package_id
    )
    return rooms

@router.get(
    "/departments/{department_id}", 
    response_model=schemas.DepartmentSimple, 
    summary="Lấy thông tin chi tiết một khoa khám"
)
def get_department_info(department_id: int, db: Session = Depends(get_db)):
    db_department = repo.get_department_by_id(db, department_id=department_id)
    if not db_department:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Department not found"
        )
    return db_department

# === API CRUD QUẢN LÝ BỆNH VIỆN  ===
@router.get(
    "/hospitals/{hospital_id}/service-packages",
    response_model=List[schemas.ServicePackageSimple],
    summary="Lấy các gói dịch vụ có tại bệnh viện"
)
def get_hospital_service_packages(hospital_id: int, db: Session = Depends(get_db)):
    return repo.get_active_service_packages_by_hospital(db, hospital_id=hospital_id)
@router.post("/hospitals", response_model=schemas.Hospital, status_code=status.HTTP_201_CREATED)
def create_hospital(hospital_in: schemas.HospitalCreate, db: Session = Depends(get_db)):
    return repo.create_hospital(db, hospital_in=hospital_in)
@router.get("/hospitals", response_model=List[schemas.Hospital])
def read_hospitals(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return repo.get_all_hospitals(db, skip=skip, limit=limit)

@router.get("/hospitals/{hospital_id}", response_model=schemas.Hospital)
def read_hospital(hospital_id: int, db: Session = Depends(get_db)):
    db_hospital = repo.get_hospital_by_id(db, hospital_id=hospital_id)
    if not db_hospital:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")
    return db_hospital

# === SERVICE CATALOG + PRICING ===
@router.get(
    "/hospitals/{hospital_id}/service-categories",
    response_model=List[schemas.ServiceCategory],
    summary="Danh mục dịch vụ của bệnh viện",
)
def list_service_categories(
    hospital_id: int,
    include_global: bool = True,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
):
    if not repo.get_hospital_by_id(db, hospital_id=hospital_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")
    return repo.get_categories_by_hospital(
        db,
        hospital_id=hospital_id,
        include_global=include_global,
        include_inactive=include_inactive,
    )


@router.post(
    "/hospitals/{hospital_id}/service-categories",
    response_model=schemas.ServiceCategory,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo danh mục dịch vụ cho bệnh viện",
)
def create_service_category(
    hospital_id: int,
    category_in: schemas.ServiceCategoryCreate,
    db: Session = Depends(get_db),
):
    if not repo.get_hospital_by_id(db, hospital_id=hospital_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")
    return repo.create_category(db, hospital_id=hospital_id, category_in=category_in)


@router.put(
    "/service-categories/{category_id}",
    response_model=schemas.ServiceCategory,
    summary="Cập nhật danh mục dịch vụ",
)
def update_service_category(
    category_id: int,
    category_in: schemas.ServiceCategoryUpdate,
    db: Session = Depends(get_db),
):
    db_category = repo.get_category_by_id(db, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return repo.update_category(db, db_category=db_category, category_in=category_in)


@router.delete(
    "/service-categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa danh mục dịch vụ",
)
def delete_service_category(category_id: int, db: Session = Depends(get_db)):
    db_category = repo.get_category_by_id(db, category_id=category_id)
    if not db_category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    repo.delete_category(db, db_category=db_category)


@router.get(
    "/hospitals/{hospital_id}/services",
    response_model=List[schemas.Service],
    summary="Danh sách dịch vụ của bệnh viện",
)
def list_services(
    hospital_id: int,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
):
    if not repo.get_hospital_by_id(db, hospital_id=hospital_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")
    return repo.get_services_by_hospital(
        db,
        hospital_id=hospital_id,
        include_inactive=include_inactive,
    )


@router.post(
    "/hospitals/{hospital_id}/services",
    response_model=schemas.Service,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo dịch vụ mới cho bệnh viện",
)
def create_service(
    hospital_id: int,
    service_in: schemas.ServiceCreate,
    db: Session = Depends(get_db),
):
    if not repo.get_hospital_by_id(db, hospital_id=hospital_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")
    return repo.create_service(db, hospital_id=hospital_id, service_in=service_in)


@router.get(
    "/services/{service_id}",
    response_model=schemas.Service,
    summary="Thông tin chi tiết dịch vụ",
)
def get_service(service_id: int, db: Session = Depends(get_db)):
    db_service = repo.get_service_by_id(db, service_id=service_id)
    if not db_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return db_service


@router.put(
    "/services/{service_id}",
    response_model=schemas.Service,
    summary="Cập nhật dịch vụ",
)
def update_service(
    service_id: int,
    service_in: schemas.ServiceUpdate,
    db: Session = Depends(get_db),
):
    db_service = repo.get_service_by_id(db, service_id=service_id)
    if not db_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return repo.update_service(
        db,
        db_service=db_service,
        service_in=service_in,
        hospital_id=db_service.hospital_id,
    )


@router.delete(
    "/services/{service_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa dịch vụ",
)
def delete_service(service_id: int, db: Session = Depends(get_db)):
    db_service = repo.get_service_by_id(db, service_id=service_id)
    if not db_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    repo.delete_service(db, db_service=db_service)


@router.get(
    "/services/{service_id}/prices",
    response_model=List[schemas.ServicePrice],
    summary="Danh sách giá của dịch vụ",
)
def list_service_prices(
    service_id: int,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
):
    db_service = repo.get_service_by_id(db, service_id=service_id)
    if not db_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return repo.get_prices_by_service(db, service_id=service_id, include_inactive=include_inactive)


@router.post(
    "/services/{service_id}/prices",
    response_model=schemas.ServicePrice,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo giá cho dịch vụ",
)
def create_service_price(
    service_id: int,
    price_in: schemas.ServicePriceCreate,
    db: Session = Depends(get_db),
):
    db_service = repo.get_service_by_id(db, service_id=service_id)
    if not db_service:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service not found")
    return repo.create_service_price(db, service_id=service_id, price_in=price_in)


@router.put(
    "/service-prices/{price_id}",
    response_model=schemas.ServicePrice,
    summary="Cập nhật bản ghi giá",
)
def update_service_price(
    price_id: int,
    price_in: schemas.ServicePriceUpdate,
    db: Session = Depends(get_db),
):
    db_price = repo.get_service_price_by_id(db, price_id=price_id)
    if not db_price:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Price not found")
    return repo.update_service_price(db, db_price=db_price, price_in=price_in)


@router.put("/hospitals/{hospital_id}", response_model=schemas.Hospital)
def update_hospital(hospital_id: int, hospital_in: schemas.HospitalUpdate, db: Session = Depends(get_db)):
    db_hospital = repo.get_hospital_by_id(db, hospital_id=hospital_id)
    if not db_hospital:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")
    return repo.update_hospital(db, db_hospital=db_hospital, hospital_in=hospital_in)

@router.delete("/hospitals/{hospital_id}", response_model=schemas.Hospital)
def delete_hospital(hospital_id: int, db: Session = Depends(get_db)):
    db_hospital = repo.get_hospital_by_id(db, hospital_id=hospital_id)
    if not db_hospital:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")
    return repo.delete_hospital(db, db_hospital=db_hospital)

# === API CRUD QUẢN LÝ GÓI DỊCH VỤ KHÁM  ===
@router.post("/service-packages", response_model=schemas.ServicePackage, status_code=status.HTTP_201_CREATED)
def create_service_package(package_in: schemas.ServicePackageCreate, db: Session = Depends(get_db)):
    return repo.create_service_package(db, package_in=package_in)

@router.get("/service-packages", response_model=List[schemas.ServicePackage])
def read_service_packages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return repo.get_all_service_packages(db, skip=skip, limit=limit)

@router.get(
    "/service-packages/{package_id}", 
    response_model=schemas.ServicePackage, 
    summary="Lấy thông tin chi tiết một dịch vụ"
)
def get_service_package_info(service_package_id: int, db: Session = Depends(get_db)):
    db_service_package = repo.get_service_package_by_id(db, service_package_id=service_package_id)
    if not db_service_package:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Service package not found"
        )
    return db_service_package

@router.put("/service-packages/{package_id}", response_model=schemas.ServicePackage)
def update_service_package(package_id: int, package_in: schemas.ServicePackageUpdate, db: Session = Depends(get_db)):
    db_package = repo.get_service_package_by_id(db, package_id=package_id)
    if not db_package:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service package not found")
    return repo.update_service_package(db, db_package=db_package, package_in=package_in)

@router.delete("/service-packages/{package_id}", response_model=schemas.ServicePackage)
def delete_service_package(package_id: int, db: Session = Depends(get_db)):
    db_package = repo.get_service_package_by_id(db, package_id=package_id)
    if not db_package:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Service package not found")
    return repo.delete_service_package(db, db_package=db_package)

@router.get(
    "/rooms/{room_id}", 
    response_model=schemas.RoomInfoResponse, 
    summary="Lấy thông tin chi tiết một phòng khám"
)
def get_room_info(room_id: int, db: Session = Depends(get_db)):
    """
    API này trả về thông tin cơ bản (tên, vị trí) của một phòng khám cụ thể
    """
    db_room = repo.get_room_by_id(db, room_id=room_id)
    if not db_room:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Room not found"
        )
    return db_room

@router.get(
    "/hospitals/{hospital_id}/emergency-department",
    response_model=schemas.EmergencyDepartment, 
    summary="Tìm khoa cấp cứu của bệnh viện"
)
def get_emergency_department(hospital_id: int, db: Session = Depends(get_db)):
    emergency_dept = repo.get_emergency_department_by_hospital(db, hospital_id=hospital_id)

    if not emergency_dept:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy khoa cấp cứu đang hoạt động cho bệnh viện này."
        )

    return emergency_dept


@router.get(
    "/hospitals/{hospital_id}/service-packages/{service_package_id}/departments",
    response_model=List[schemas.DepartmentSimple],
    summary="Lấy danh sách khoa theo gói dịch vụ"
)
def get_departments_for_service_package(
    hospital_id: int,
    service_package_id: int,
    db: Session = Depends(get_db)
):
    departments = repo.get_departments_by_service_package(
        db=db,
        hospital_id=hospital_id,
        service_package_id=service_package_id
    )
    
    return departments


def _find_syndrome_bundle(
    bundles: List[dict],
    syndrome_id: str,
) -> Optional[dict]:
    for bundle in bundles:
        if bundle.get("syndrome_id") == syndrome_id:
            return bundle
    return None


@router.get(
    "/hospitals/{hospital_id}/triage/syndrome-mappings",
    response_model=List[schemas.SyndromeMappingResponse],
    summary="Lấy mapping giữa hội chứng triage và khoa khám"
)
def get_syndrome_triage_mappings(
    hospital_id: int,
    include_inactive: bool = False,
    db: Session = Depends(get_db),
):
    return repo.get_syndrome_mappings_by_hospital(
        db,
        hospital_id=hospital_id,
        include_inactive=include_inactive,
    )


@router.post(
    "/hospitals/{hospital_id}/triage/syndrome-mappings",
    response_model=schemas.SyndromeMappingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Tạo mapping hội chứng triage -> khoa"
)
def create_syndrome_triage_mapping(
    hospital_id: int,
    mapping_in: schemas.SyndromeTriageUnitCreate,
    db: Session = Depends(get_db),
):
    new_mapping = repo.create_syndrome_mapping(
        db=db,
        hospital_id=hospital_id,
        mapping_in=mapping_in,
    )
    bundles = repo.get_syndrome_mappings_by_hospital(
        db,
        hospital_id=hospital_id,
        include_inactive=True,
    )
    bundle = _find_syndrome_bundle(bundles, new_mapping.syndrome_id)
    if bundle:
        return bundle
    return {
        "syndrome_id": new_mapping.syndrome_id,
        "syndrome_name": new_mapping.syndrome_name,
        "triage_units": [],
    }


@router.put(
    "/triage/syndrome-mappings/{mapping_id}",
    response_model=schemas.SyndromeMappingResponse,
    summary="Cập nhật mapping hội chứng triage -> khoa"
)
def update_syndrome_triage_mapping(
    mapping_id: int,
    mapping_in: schemas.SyndromeTriageUnitUpdate,
    db: Session = Depends(get_db),
):
    db_mapping = repo.get_syndrome_mapping_by_id(db, mapping_id=mapping_id)
    if not db_mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Syndrome mapping not found",
        )

    updated = repo.update_syndrome_mapping(
        db=db,
        db_mapping=db_mapping,
        mapping_in=mapping_in,
    )
    bundles = repo.get_syndrome_mappings_by_hospital(
        db,
        hospital_id=updated.hospital_id,
        include_inactive=True,
    )
    bundle = _find_syndrome_bundle(bundles, updated.syndrome_id)
    if bundle:
        return bundle
    return {
        "syndrome_id": updated.syndrome_id,
        "syndrome_name": updated.syndrome_name,
        "triage_units": [],
    }


@router.delete(
    "/triage/syndrome-mappings/{mapping_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Xóa mapping hội chứng triage -> khoa"
)
def delete_syndrome_triage_mapping(
    mapping_id: int,
    db: Session = Depends(get_db),
):
    db_mapping = repo.get_syndrome_mapping_by_id(db, mapping_id=mapping_id)
    if not db_mapping:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Syndrome mapping not found",
        )

    repo.delete_syndrome_mapping(db=db, db_mapping=db_mapping)


@router.get(
    "/search/zones/by-department",
    response_model=List[schemas.Zone],
    summary="Tìm Khu theo tên Khoa"
)
def search_zones_by_department_name(
    name: str, 
    hospital_id: int,
    db: Session = Depends(get_db)
):
    """
    Nhập tên khoa (ví dụ: 'Nội', 'Ngoại') để tìm xem khoa đó thuộc Khu nào.
    """
    zones = repo.get_zones_by_department_name(db, department_name=name, hospital_id=hospital_id)
    if not zones:
        return []
    return zones


@router.get(
    "/search/zones/by-room",
    response_model=List[schemas.Zone],
    summary="Tìm Khu theo tên/số Phòng"
)
def search_zones_by_room_name(
    name: str, 
    hospital_id: int,
    db: Session = Depends(get_db)
):
    """
    Nhập tên phòng (ví dụ: '101', 'P.202') để tìm xem phòng đó thuộc Khu nào.
    """
    zones = repo.get_zones_by_room_number(db, room_number=name, hospital_id=hospital_id)
    return zones


@router.get(
    "/search/rooms/location",
    response_model=List[schemas.RoomLocationResponse],
    summary="Tìm vị trí mô tả của phòng theo tên phòng"
)
def search_room_location(
    name: str, 
    hospital_id: int,
    db: Session = Depends(get_db)
):
    """
    Lấy mô tả vị trí (location_description) của phòng.
    Kết quả trả về kèm tên Khoa và Tên Bệnh viện để phân biệt nếu trùng tên phòng.
    """
    rooms = repo.get_room_location_by_name(db, room_number=name, hospital_id=hospital_id)
    
    results = []
    for r in rooms:
        results.append({
            "room_id": r.room_id,
            "room_number": r.room_number,
            "location_description": r.location_description,
            "department_name": r.department.name if r.department else None,
            "hospital_name": r.department.hospital.name if (r.department and r.department.hospital) else None,
            "zone_name": r.department.zone.name if (r.department and r.department.zone) else None
        })
    return results