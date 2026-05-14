from decimal import Decimal
from datetime import date
from typing import List, Optional

from pydantic import BaseModel, EmailStr

# --- Schemas dùng cho Response (đọc dữ liệu) ---
class ServicePackageSimple(BaseModel):
    service_package_id: int
    name: str
    is_bhyt_applicable: bool
    hint: Optional[str] = None
    class Config: from_attributes = True

class ServicePackage(BaseModel):
    service_package_id: int
    name: str
    is_bhyt_applicable: bool
    hint: Optional[str] = None
    status: int
    class Config: from_attributes = True

class ExaminationRoom(BaseModel):
    room_id: int
    room_number: Optional[str]
    location_description: Optional[str]
    status: int
    service_packages: List[ServicePackage] = []
    class Config: from_attributes = True

class Department(BaseModel):
    department_id: int
    name: str
    status: int
    hint: Optional[str] = None
    examination_rooms: List[ExaminationRoom] = []
    class Config: from_attributes = True



class Kiosk(BaseModel):
    kiosk_id: int
    location: Optional[str]
    hospital_id: int
    class Config: from_attributes = True

class Hospital(BaseModel):
    hospital_id: int
    KCB_code: Optional[str]
    name: str
    address: Optional[str]
    hotline: Optional[str]
    email: Optional[EmailStr]
    status: int
    allow_specific_department_selection:  bool
    departments: List[Department] = []
    kiosks: List[Kiosk] = []
    service_packages: List[ServicePackageSimple] = []
    
    class Config: from_attributes = True

class DepartmentSimple(BaseModel):
    department_id: int
    name: str
    hint: Optional[str] = None
    class Config: from_attributes = True
    
# --- Schemas dùng cho Request (tạo/cập nhật dữ liệu) ---

class HospitalCreate(BaseModel):
    name: str
    KCB_code: Optional[str] = None
    address: Optional[str] = None
    hotline: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[int] = 1
    allow_specific_department_selection:  Optional[bool] = 1

class HospitalUpdate(BaseModel):
    name: Optional[str] = None
    KCB_code: Optional[str] = None
    address: Optional[str] = None
    hotline: Optional[str] = None
    email: Optional[EmailStr] = None
    status: Optional[int] = None
    allow_specific_department_selection:  Optional[bool] = None


# CRUD cho ServicePackage
class ServicePackageCreate(BaseModel):
    name: str
    is_bhyt_applicable: bool
    status: Optional[int] = 1

class ServicePackageUpdate(BaseModel):
    name: Optional[str] = None
    is_bhyt_applicable: Optional[bool] = None
    status: Optional[int] = None


# CRUD cho Room
class RoomInfoResponse(BaseModel):
    room_id: int
    room_number: Optional[str]
    location_description: Optional[str]

    class Config:
        from_attributes = True
# --- Schemas cho logic nghiệp vụ đặc thù ---

class HospitalInfoForKiosk(BaseModel):
    hospital_id: int
    name: str
    address: Optional[str]
    class Config: from_attributes = True

class KioskInfoResponse(Kiosk):
    hospital: HospitalInfoForKiosk
    class Config: from_attributes = True




class ServicePackageName(BaseModel):
    name: str
    class Config: from_attributes = True
class EmergencyRoom(BaseModel):
    room_id: int
    room_number: Optional[str]
    location_description: Optional[str]
    service_packages: List[ServicePackageName] = []
    class Config: from_attributes = True
class EmergencyDepartment(BaseModel):
    department_id: int
    name: str
    examination_rooms: List[EmergencyRoom] = []
    class Config: from_attributes = True


class SyndromeTriagedUnit(BaseModel):
    mapping_id: int
    triage_unit_id: Optional[str] = None
    department_id: Optional[int] = None
    name: Optional[str] = None
    priority: Optional[int] = 1
    score_multiplier: Optional[float] = 1.0
    status: int = 1

    class Config:
        from_attributes = True


class SyndromeMappingResponse(BaseModel):
    syndrome_id: str
    syndrome_name: Optional[str] = None
    triage_units: List[SyndromeTriagedUnit] = []


class SyndromeTriageUnitCreate(BaseModel):
    syndrome_id: str
    syndrome_name: Optional[str] = None
    triage_unit_id: Optional[str] = None
    department_id: Optional[int] = None
    name_override: Optional[str] = None
    priority: Optional[int] = 1
    score_multiplier: Optional[float] = 1.0
    status: Optional[int] = 1


class SyndromeTriageUnitUpdate(BaseModel):
    syndrome_name: Optional[str] = None
    triage_unit_id: Optional[str] = None
    department_id: Optional[int] = None
    name_override: Optional[str] = None
    priority: Optional[int] = None
    score_multiplier: Optional[float] = None
    status: Optional[int] = None


# === SERVICE CATALOG + PRICING ===

class ServiceCategoryBase(BaseModel):
    name: str
    category_type: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = 1

class ServiceCategoryCreate(ServiceCategoryBase):
    pass

class ServiceCategoryUpdate(BaseModel):
    name: Optional[str] = None
    category_type: Optional[str] = None
    description: Optional[str] = None
    status: Optional[int] = None

class ServiceCategory(ServiceCategoryBase):
    category_id: int
    hospital_id: Optional[int] = None

    class Config:
        from_attributes = True

class ServiceBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    aliases: Optional[str] = None
    status: Optional[int] = 1

class ServiceCreate(ServiceBase):
    category_ids: Optional[List[int]] = None


class ServiceUpdate(BaseModel):
    code: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    aliases: Optional[str] = None
    status: Optional[int] = None
    category_ids: Optional[List[int]] = None

class Service(ServiceBase):
    service_id: int
    hospital_id: int
    status: int
    categories: List[ServiceCategory] = []

    class Config:
        from_attributes = True

class ServicePriceBase(BaseModel):
    price: Decimal
    currency: Optional[str] = "VND"
    payer_type: Optional[str] = None
    area_tag: Optional[str] = None
    effective_from: date
    effective_to: Optional[date] = None
    notes: Optional[str] = None
    status: Optional[int] = 1
    hospital_id: Optional[int] = None


class ServicePriceCreate(ServicePriceBase):
    pass


class ServicePriceUpdate(BaseModel):
    price: Optional[Decimal] = None
    currency: Optional[str] = None
    payer_type: Optional[str] = None
    area_tag: Optional[str] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    notes: Optional[str] = None
    status: Optional[int] = None
    hospital_id: Optional[int] = None


class ServicePrice(ServicePriceBase):
    price_id: int
    service_id: int

    class Config:
        from_attributes = True
class Zone(BaseModel):
    zone_id: int
    name: str
    hospital_id: int
    class Config: from_attributes = True

class RoomLocationResponse(BaseModel):
    room_id: int
    room_number: Optional[str]
    location_description: Optional[str]
    department_name: Optional[str]
    hospital_name: Optional[str]
    zone_name: Optional[str]
    class Config: from_attributes = True
