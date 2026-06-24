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
    email=Column(String,nullable=False)
    password=Column(String,nullable=False)
    role=Column(PYENUM(RoleEnum),nullable=False)

  
    #relationship with document
    document=relationship("DocumentModel",back_populates="patient")

    
    #relationship with appointment as clinician 
    user_c=relationship("AppointmentModel",back_populates="clinician")

    #relationship with appointment as patient
    user_p=relationship("AppointmentModel",back_populates="patient")
