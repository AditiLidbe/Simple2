from sqlalchemy import Column, String, Integer, ForeignKey, Enum as PYENUM
from ..db.base import Base
from sqlalchemy.orm import relationship

from enum import Enum

class RoleEnum(str,Enum):
    PATIENT="PATIENT"
    FRONT_DESK="FRONT_DESK"
    CLINICIAN="CLINICIAN"

class UserModel(Base):
    __tablename__="user_model"
    id=Column(Integer,primary_key=True,nullable=False)
    name=Column(String,nullable=False)
    email=Column(String,nullable=False,unique=True,index=True)
    password=Column(String,nullable=False)
    role=Column(PYENUM(RoleEnum),nullable=False)

  
    #relationship with document
    document=relationship("DocumentModel",back_populates="patient")

    
    #relationship with appointment as clinician 
    appointments_as_clinician = relationship("AppointmentModel", foreign_keys="[AppointmentModel.clinician_id]", back_populates="clinician")

    
    # Relationship with AppointmentModel as PATIENT
    appointments_as_patient = relationship("AppointmentModel", foreign_keys="[AppointmentModel.patient_id]", back_populates="patient")

