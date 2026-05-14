from datetime import date

from sqlalchemy import BigInteger, Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.sql import func

from .db import QueueBase

class Registration(QueueBase):
    __tablename__ = "REGISTRATIONS"
    registration_id = Column(BigInteger, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, nullable=True)
    department_id = Column(Integer, nullable=True)
    room_id = Column(Integer, nullable=True)
    service_package_id = Column(Integer, nullable=True)
    kiosk_id = Column(Integer, nullable=True)
    queue_number = Column(Integer, nullable=True)
    registration_time = Column(DateTime, server_default=func.current_timestamp())
    queue_date = Column(Date, default=date.today, nullable=False)
    status = Column(String(20), server_default="waiting")
