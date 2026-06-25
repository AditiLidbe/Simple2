from sqlalchemy import Column, String, Integer, ForeignKey, Enum as PYENUM, TIMESTAMP, DateTime, Text, JSON
from ..db.base import Base
from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class AppointmentStatus(str,Enum):
    BOOKED="BOOKED"
    WAITING="WAITING"
    CALLED_BACK="CALLED_BACK"
    COMPLETED="COMPLETED"
    CANCELLED="CANCELLED"

class AppointmentModel(Base):
    __tablename__="appointment_model"
    id=Column(Integer,primary_key=True,nullable=False)
    date=Column(DateTime(timezone=True),nullable=False)
    created_at=Column(TIMESTAMP(timezone=True),nullable=False,server_default=func.now())
    status=Column(PYENUM(AppointmentStatus),nullable=False,server_default=AppointmentStatus.BOOKED)
    reason=Column(Text,nullable=True)
    intake_status=Column(String,nullable=False,server_default="NOT_STARTED")
    personal_details=Column(JSON,nullable=True)
    medical_history=Column(JSON,nullable=True)
    pre_visit_summary=Column(Text,nullable=True)
    visit_summary=Column(Text,nullable=True)
    checked_in_at=Column(TIMESTAMP(timezone=True),nullable=True)
    called_at=Column(TIMESTAMP(timezone=True),nullable=True)

    #realtionship with documents
    document=relationship("DocumentModel",back_populates="appoinment")

    #realtionship with clinician
    clinician_id=Column(Integer,ForeignKey("user_model.id"),nullable=False)
    clinician = relationship("UserModel", foreign_keys=[clinician_id], back_populates="appointments_as_clinician")

    #realtionship with patient
    patient_id=Column(Integer,ForeignKey("user_model.id"),nullable=False)
    patient = relationship("UserModel", foreign_keys=[patient_id], back_populates="appointments_as_patient")
