import time

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from app.directory.db import get_db
from app.directory.repository import repo as directory_repo
from app.queue.db import get_queue_db
from app.queue.repository import queue_repo
from app.queue.schemas import (
    NextNumberRequest,
    NextNumberResponse,
    RegistrationOut,
    UpdateQueueStatusRequest,
)
from app.servicelogs.servicelogger import logger

router = APIRouter()


@router.post("/queue/next-number/{hospital_id}", response_model=NextNumberResponse, summary="Bốc số và tự động phân phòng")
def create_next_number(
    hospital_id: int,
    body: NextNumberRequest,
    db_queue: Session = Depends(get_queue_db),
    db_directory: Session = Depends(get_db)
):
    """
    Kiosk gọi API này để tạo số thứ tự mới.
    """
    max_retries = 3  
    retry_delay = 0.1 

    hospital = directory_repo.get_hospital_by_id(db_directory, hospital_id)
    if not hospital:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Hospital not found")

    target_department_id: int
    if hospital.allow_specific_department_selection:
        # Cờ = 1: Bệnh viện cho phép chọn khoa, lấy department_id từ request body
        target_department_id = body.department_id
    else:
        # Cờ = 0: Mặc định vào khoa Khám bệnh/Tổng quát
        general_dept = directory_repo.get_general_department_by_hospital(db_directory, hospital_id)
        if not general_dept:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Không tìm thấy khoa Khám bệnh đang hoạt động cho bệnh viện này."
            )
        target_department_id = general_dept.department_id
        
    for attempt in range(max_retries):
        try:
            # === LOGIC PHÂN PHỐI TẢI ===
            eligible_rooms = directory_repo.get_active_rooms_by_department_and_service(
                db=db_directory,
                department_id=target_department_id,
                service_package_id=body.service_package_id
            )
            if not eligible_rooms:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Không tìm thấy phòng khám nào hoạt động cho khoa và gói dịch vụ này."
                )
            best_room_id: int
            if len(eligible_rooms) == 1:
                best_room_id = eligible_rooms[0].room_id
            else:
                eligible_room_ids = [room.room_id for room in eligible_rooms]
                waiting_counts = queue_repo.get_waiting_counts_for_rooms(
                    db=db_queue, 
                    room_ids=eligible_room_ids
                )
                min_wait = float('inf')
                best_room_id = eligible_room_ids[0] # Mặc định chọn phòng đầu tiên
                for room_id in eligible_room_ids:
                    count = waiting_counts.get(room_id, 0)
                    if count < min_wait:
                        min_wait = count
                        best_room_id = room_id
            
            # === TẠO SỐ THỨ TỰ  ===
            reg = queue_repo.create_next_number(
                db=db_queue,
                department_id=target_department_id,
                room_id=best_room_id,
                patient_id=body.patient_id,
                service_package_id=body.service_package_id,
                kiosk_id=body.kiosk_id,
            )

            # === LÀM GIÀU DỮ LIỆU ===
            hospital_name = None
            department_name = None
            room_name = None
            service_package_name = None
            location = None
            hospital_name = None
            
            if reg.department_id:
                department = directory_repo.get_department_by_id(db_directory, reg.department_id)
                if department:
                    department_name = department.name

            if hospital_id:
                hospital = directory_repo.get_hospital_by_id(db_directory, hospital_id)
                if hospital:
                    hospital_name = hospital.name
            
            if reg.room_id:
                room = directory_repo.get_room_by_id(db_directory, reg.room_id)
                if room:
                    room_name = room.room_number
                    location = room.location_description

            if reg.service_package_id:
                service_package = directory_repo.get_service_package_by_id(db_directory, reg.service_package_id)
                if service_package:
                    service_package_name = service_package.name

            if reg.kiosk_id:
                kiosk = directory_repo.get_kiosk_info(db_directory, reg.kiosk_id)
                if kiosk:
                    kiosk_location = kiosk.location

            # === TRẢ VỀ RESPONSE ĐÃ ĐƯỢC LÀM GIÀU ===
            return NextNumberResponse(
                registration_id=reg.registration_id,
                department_id=reg.department_id,
                room_id=reg.room_id,
                queue_date=reg.queue_date,
                queue_number=reg.queue_number,
                status=reg.status,
                registration_time=reg.registration_time,
                hospital_name=hospital_name,
                department_name=department_name,
                room_name=room_name,
                service_package_name=service_package_name,
                location=location,
            )

        except OperationalError as e:
            if "Deadlock found" in str(e):
                logger.warning(f"Deadlock detected on attempt {attempt + 1}. Retrying...")
                if attempt == max_retries - 1:
                    logger.error("Max retries reached for deadlock. Aborting.")
                    raise HTTPException(
                        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                        detail="Hệ thống đang quá tải, vui lòng thử lại sau giây lát. (Deadlock)"
                    )
                time.sleep(retry_delay)
            else:
                logger.error(f"OperationalError occurred: {e}")
                raise e
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise e
  
#Update status queue
@router.patch("/registrations/{registration_id}/status", response_model=RegistrationOut)
def update_queue_status(
    registration_id: int,
    body: UpdateQueueStatusRequest,
    db: Session = Depends(get_queue_db),
):
    reg = queue_repo.update_registration_status(db, registration_id, body.status)
    if not reg:
        raise HTTPException(status_code=404, detail="Registration not found")
    return reg

# Số kế tiếp (dành cho bác sĩ)
@router.post("/rooms/{dep}/{room}/advance", response_model=RegistrationOut)
def advance(dep: int, room: int, db: Session = Depends(get_queue_db)):
    reg = queue_repo.advance_next(db, dep, room)
    if not reg:
        raise HTTPException(404, "No waiting number")
    return reg

# Bỏ qua (dành cho bác sĩ)
@router.post("/rooms/{dep}/{room}/skip-current", response_model=RegistrationOut)
def skip_current(dep: int, room: int, reason: str|None=None, db: Session = Depends(get_queue_db)):
    reg = queue_repo.skip_current(db, dep, room, reason)
    if not reg:
        raise HTTPException(404, "No current in_progress")
    return reg

#Hoàn thành (dành cho bác sĩ)
@router.post("/rooms/{dep}/{room}/complete-current", response_model=RegistrationOut)
def complete_current(dep: int, room: int, db: Session = Depends(get_queue_db)):
    reg = queue_repo.complete_current(db, dep, room)
    if not reg:
        raise HTTPException(404, "No current in_progress")
    return reg

# Truy vấn DB để lấy:
# current: bản ghi có status = "in_progress" hôm nay — tức bệnh nhân đang được gọi / khám.
# waiting: danh sách 10 bệnh nhân tiếp theo (status = "waiting", theo thứ tự nhỏ nhất). 
@router.get("/rooms/{dep}/{room}/now")
def room_now(dep: int, room: int, db: Session = Depends(get_queue_db)):
    current = queue_repo.get_current(db, dep, room)
    waiting = queue_repo.list_waiting(db, dep, room, limit=10)
    return {"current": current, "waiting": waiting}
