from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime, date
from typing import Optional, Literal

class NextNumberRequest(BaseModel):
    patient_id: Optional[int] = None
    department_id: int
    service_package_id: int
    kiosk_id: Optional[int] = None

class NextNumberResponse(BaseModel):
    registration_id: int
    department_id: int
    room_id: int
    queue_date: date
    queue_number: int
    status: str = "waiting"
    registration_time: datetime
    
    # Dữ liệu được làm giàu
    hospital_name: Optional[str] = None
    department_name: Optional[str] = None
    room_name: Optional[str] = None
    service_package_name: Optional[str] = None
    location: Optional[str] = None
    
AllowedStatus = Literal["waiting", "in_progress", "skipped", "completed", "cancelled"]

class UpdateQueueStatusRequest(BaseModel):
    status: AllowedStatus

class RegistrationOut(BaseModel):
    registration_id: int
    department_id: int
    room_id: int
    queue_date: date
    queue_number: int
    status: str
    registration_time: datetime

    class Config:
        from_attributes = True