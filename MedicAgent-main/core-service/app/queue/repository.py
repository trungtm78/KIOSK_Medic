from typing import Dict, List

from sqlalchemy import func, text
from sqlalchemy.orm import Session

from .models import Registration

class QueueRepository:

    def get_waiting_counts_for_rooms(self, db: Session, room_ids: List[int]) -> Dict[int, int]:
        """
        Đếm số lượng đăng ký đang ở trạng thái 'waiting' trong ngày hôm nay
        cho một danh sách các room_id.
        Trả về một dictionary: {room_id: count}.
        """
        if not room_ids:
            return {}

        counts = db.query(
            Registration.room_id,
            func.count(Registration.registration_id)
        ).filter(
            Registration.room_id.in_(room_ids),
            Registration.status == 'waiting',
            Registration.queue_date == func.curdate()
        ).group_by(
            Registration.room_id
        ).all()
        
        return {room_id: count for room_id, count in counts}


    # Tạo số thứ tự kế tiếp THEO PHÒNG trong khoa, cho ngày hiện tại
    def create_next_number(
        self,
        db: Session,
        *,
        department_id: int,
        room_id: int,
        patient_id: int | None = None,
        service_package_id: int | None = None,
        kiosk_id: int | None = None,
    ) -> Registration:
        """
        Tạo số thứ tự kế tiếp trong ngày
        """
        try:
            # 1) Khóa phạm vi các bản ghi của (department_id, room_id, today)
            db.execute(
                text(
                    """
                    SELECT queue_number
                    FROM REGISTRATIONS
                    WHERE department_id = :dep
                      AND room_id = :room
                      AND queue_date = CURDATE()
                    ORDER BY queue_number DESC
                    LIMIT 1
                    FOR UPDATE
                    """
                ),
                {"dep": department_id, "room": room_id},
            )

            # 2) Lấy max queue_number trong phạm vi trên
            maxq = db.execute(
                text(
                    """
                    SELECT COALESCE(MAX(queue_number), 0) AS maxq
                    FROM REGISTRATIONS
                    WHERE department_id = :dep
                      AND room_id = :room
                      AND queue_date = CURDATE()
                    """
                ),
                {"dep": department_id, "room": room_id},
            ).scalar() or 0

            next_no = int(maxq) + 1

            # 3) Insert bản ghi mới
            reg = Registration(
                patient_id=patient_id,
                department_id=department_id,
                room_id=room_id,
                service_package_id=service_package_id,
                kiosk_id=kiosk_id,
                queue_number=next_no,
                status="waiting",
            )
            db.add(reg)
        
            db.commit()
            db.refresh(reg)

            return reg
        except Exception as e:
            db.rollback()
            raise e
    
    def update_registration_status(
        self, db: Session, registration_id: int, new_status: str
    ) -> Registration | None:
        reg = db.query(Registration).filter(
            Registration.registration_id == registration_id
        ).first()
        if not reg:
            return None
        reg.status = new_status
        db.add(reg)
        db.commit()
        db.refresh(reg)
        return reg
    
    # Gọi số kế tiếp
    def advance_next(self, db: Session, dep_id: int, room_id: int) -> Registration | None:
        with db.begin():
            row = db.execute(text("""
                SELECT registration_id
                FROM REGISTRATIONS
                WHERE department_id=:d AND room_id=:r
                  AND queue_date=CURDATE() AND status='waiting'
                ORDER BY queue_number ASC
                LIMIT 1
                FOR UPDATE
            """), {"d": dep_id, "r": room_id}).first()
            if not row:
                return None
            reg = db.query(Registration).get(row[0])
            reg.status = "in_progress"
            db.add(reg)
            db.flush()
            db.refresh(reg)
            return reg

    def get_current(self, db: Session, dep_id: int, room_id: int):
        return db.query(Registration)\
            .filter(
                Registration.department_id == dep_id,
                Registration.room_id == room_id,
                Registration.queue_date == func.curdate(),
                Registration.status == "in_progress"
            )\
            .order_by(Registration.registration_time.desc())\
            .first()

    # Bỏ qua
    def skip_current(self, db: Session, dep_id: int, room_id: int, reason: str | None = None):
        with db.begin():
            reg = self.get_current(db, dep_id, room_id)
            if not reg:
                return None
            reg.status = "skipped"
            # reg.skipped_reason = reason  # nếu có cột
            db.add(reg)
            db.flush()
            db.refresh(reg)
            return reg

    # Hoàn thành
    def complete_current(self, db: Session, dep_id: int, room_id: int):
        with db.begin():
            reg = self.get_current(db, dep_id, room_id)
            if not reg:
                return None
            reg.status = "completed"
            db.add(reg)
            db.flush()
            db.refresh(reg)
            return reg

    # (nếu router của bạn dùng) danh sách waiting
    def list_waiting(self, db: Session, dep_id: int, room_id: int, limit: int = 10):
        return db.query(Registration)\
            .filter(
                Registration.department_id == dep_id,
                Registration.room_id == room_id,
                Registration.queue_date == func.curdate(),
                Registration.status == "waiting"
            )\
            .order_by(Registration.queue_number.asc())\
            .limit(limit)\
            .all()


queue_repo = QueueRepository()
