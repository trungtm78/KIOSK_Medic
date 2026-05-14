# core-service/app/directory/models.py

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from .db import Base

examination_room_service_packages = Table('EXAMINATION_ROOM_SERVICE_PACKAGES', Base.metadata,
    Column('room_id', Integer, ForeignKey('EXAMINATION_ROOMS.room_id'), primary_key=True),
    Column('service_package_id', Integer, ForeignKey('SERVICE_PACKAGES.service_package_id'), primary_key=True)
)

hospital_service_packages = Table('HOSPITAL_SERVICE_PACKAGES', Base.metadata,
    Column('hospital_id', Integer, ForeignKey('HOSPITALS.hospital_id'), primary_key=True),
    Column('service_package_id', Integer, ForeignKey('SERVICE_PACKAGES.service_package_id'), primary_key=True)
)

service_category_links = Table(
    "SERVICE_CATEGORY_LINKS",
    Base.metadata,
    Column("service_id", Integer, ForeignKey("SERVICES.service_id"), primary_key=True),
    Column("category_id", Integer, ForeignKey("SERVICE_CATEGORIES.category_id"), primary_key=True),
)


class Hospital(Base):
    __tablename__ = "HOSPITALS"
    hospital_id = Column(Integer, primary_key=True)
    KCB_code = Column(String(50), unique=True, index=True)
    name = Column(String(255), nullable=False)
    address = Column(String(255))
    hotline = Column(String(20))
    email = Column(String(100))
    status = Column(Integer, default=1, comment="1: Active, 0: Inactive")
    allow_specific_department_selection = Column(Boolean, nullable=False, server_default='1')
    departments = relationship("Department", back_populates="hospital", cascade="all, delete-orphan")
    kiosks = relationship("Kiosk", back_populates="hospital", cascade="all, delete-orphan")
    service_packages = relationship("ServicePackage", secondary=hospital_service_packages, back_populates="hospitals")
    services = relationship("Service", back_populates="hospital", cascade="all, delete-orphan")
    syndrome_mappings = relationship(
        "SyndromeTriageMapping",
        back_populates="hospital",
        cascade="all, delete-orphan"
    )

class Zone(Base):
    __tablename__ = "ZONES"
    zone_id = Column(Integer, primary_key=True)
    hospital_id = Column(Integer, ForeignKey("HOSPITALS.hospital_id"), nullable=False)
    name = Column(String(255), nullable=False)

    hospital = relationship("Hospital") 
    departments = relationship("Department", back_populates="zone")


class Department(Base):
    __tablename__ = "DEPARTMENTS"
    department_id = Column(Integer, primary_key=True)
    hospital_id = Column(Integer, ForeignKey("HOSPITALS.hospital_id"), nullable=False)
    name = Column(String(255), nullable=False)
    hint = Column(Text)
    status = Column(Integer, default=1, comment="1: Active, 0: Inactive")
    zone_id = Column(Integer, ForeignKey("ZONES.zone_id"), nullable=True) 

    hospital = relationship("Hospital", back_populates="departments")
    examination_rooms = relationship("ExaminationRoom", back_populates="department", cascade="all, delete-orphan")
    syndrome_mappings = relationship(
        "SyndromeTriageMapping",
        back_populates="department",
        cascade="all, delete-orphan"
    )
    zone = relationship("Zone", back_populates="departments")


class ExaminationRoom(Base):
    __tablename__ = "EXAMINATION_ROOMS"
    room_id = Column(Integer, primary_key=True)
    department_id = Column(Integer, ForeignKey("DEPARTMENTS.department_id"), nullable=False)
    room_number = Column(String(50))
    location_description = Column(Text)
    status = Column(Integer, default=1, comment="1: Active, 0: Inactive")

    department = relationship("Department", back_populates="examination_rooms")
    
    service_packages = relationship(
        "ServicePackage",
        secondary=examination_room_service_packages,
        back_populates="examination_rooms"
    )

class Kiosk(Base):
    __tablename__ = "KIOSKS"
    kiosk_id = Column(Integer, primary_key=True)
    hospital_id = Column(Integer, ForeignKey("HOSPITALS.hospital_id"), nullable=False)
    location = Column(String(255))

    hospital = relationship("Hospital", back_populates="kiosks")

class ServicePackage(Base):
    __tablename__ = "SERVICE_PACKAGES"
    service_package_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    is_bhyt_applicable = Column(Boolean, nullable=False, default=False)
    status = Column(Integer, default=1, comment="1: Active, 0: Inactive")
    hint = Column(Text)
    
    examination_rooms = relationship(
        "ExaminationRoom",
        secondary=examination_room_service_packages,
        back_populates="service_packages"
    )
    hospitals = relationship(
        "Hospital",
        secondary=hospital_service_packages,
        back_populates="service_packages"
    )

class ServiceCategory(Base):
    __tablename__ = "SERVICE_CATEGORIES"
    __table_args__ = (
        UniqueConstraint("hospital_id", "name", name="uq_service_categories_hospital_name"),
    )
    category_id = Column(Integer, primary_key=True)
    hospital_id = Column(Integer, ForeignKey("HOSPITALS.hospital_id"), nullable=True, index=True)
    name = Column(String(255), nullable=False)
    category_type = Column(String(100), nullable=True, comment="Ví dụ: chuyên khoa, loại dịch vụ")
    description = Column(Text)
    status = Column(Integer, default=1, comment="1: Active, 0: Inactive")

    hospital = relationship("Hospital")
    services = relationship("Service", secondary=service_category_links, back_populates="categories")


class Service(Base):
    __tablename__ = "SERVICES"
    __table_args__ = (
        UniqueConstraint("hospital_id", "code", name="uq_services_hospital_code"),
    )
    service_id = Column(Integer, primary_key=True)
    hospital_id = Column(Integer, ForeignKey("HOSPITALS.hospital_id"), nullable=False, index=True)
    code = Column(String(100), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    aliases = Column(Text, comment="Các tên gọi khác, phục vụ search", nullable=True)
    status = Column(Integer, default=1, comment="1: Active, 0: Inactive")

    hospital = relationship("Hospital", back_populates="services")
    categories = relationship("ServiceCategory", secondary=service_category_links, back_populates="services")
    prices = relationship("ServicePrice", back_populates="service", cascade="all, delete-orphan")


class ServicePrice(Base):
    __tablename__ = "SERVICE_PRICES"
    __table_args__ = (
        UniqueConstraint(
            "service_id",
            "hospital_id",
            "payer_type",
            "area_tag",
            "effective_from",
            "effective_to",
            name="uq_service_price_period_payer_area",
        ),
    )

    price_id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey("SERVICES.service_id"), nullable=False, index=True)
    hospital_id = Column(Integer, ForeignKey("HOSPITALS.hospital_id"), nullable=True, index=True)

    price = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="VND", nullable=False)
    payer_type = Column(String(50), nullable=True, comment="BHYT, tu_chi_tra, doanh_nghiep...")
    area_tag = Column(String(100), nullable=True, comment="Khu vực/tầng/khu VIP nếu có")
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=True)
    notes = Column(Text)
    status = Column(Integer, default=1, comment="1: Active, 0: Inactive")

    service = relationship("Service", back_populates="prices")
    hospital = relationship("Hospital")


class SyndromeTriageMapping(Base):
    __tablename__ = "SYNDROME_TRIAGE_MAPPINGS"

    mapping_id = Column(Integer, primary_key=True)
    hospital_id = Column(Integer, ForeignKey("HOSPITALS.hospital_id"), nullable=False, index=True)
    syndrome_id = Column(String(100), nullable=False, index=True)
    syndrome_name = Column(String(255))
    triage_unit_id = Column(String(100))
    department_id = Column(Integer, ForeignKey("DEPARTMENTS.department_id"))
    name_override = Column(String(255))
    priority = Column(Integer, default=1, comment="Số thứ tự ưu tiên khi có nhiều khoa")
    score_multiplier = Column(Float, default=1.0, comment="Điều chỉnh điểm đề xuất của hội chứng")
    status = Column(Integer, default=1, comment="1: Active, 0: Inactive")

    hospital = relationship("Hospital", back_populates="syndrome_mappings")
    department = relationship("Department", back_populates="syndrome_mappings")
