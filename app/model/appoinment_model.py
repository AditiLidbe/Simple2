from sqlalchemy import Column, String, Integer, ForeignKey, Enum as PYENUM,TIMESTAMP,DATE
from ..db.base import Base
from datetime import  timezone 
from enum import Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

class AppointmentStatus(str,Enum):
    BOOKED="BOOKED"
    WAITING="WAITING"
    COMPLETED="COMPLETED"
    CANCELLED="CANCELLED"

class AppointmentModel(Base):
    __tablename__="appointment_model"
    id=Column(Integer,primary_key=True,nullable=False)
    date=Column(DATE,nullable=False)
    created_at=Column(TIMESTAMP(timezone=True),nullable=False,server_default=func.now())
    status=Column(PYENUM(AppointmentStatus),nullable=False,server_default=AppointmentStatus.WAITING)

    #realtionship with documents
    document=relationship("DocumentModel",back_populates="appoinment")

    #realtionship with clinician
    clinician_id=Column(Integer,ForeignKey("user_model.id"),nullable=False)
    clinician=relationship("UserModel",back_populates="user_c")

    #realtionship with patient
    patient_id=Column(Integer,ForeignKey("user_model.id"),nullable=False)
    patient=relationship("UserModel",back_populates="user_p")