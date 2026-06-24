from sqlalchemy import Column, String, Integer, ForeignKey, Enum as PYENUM,TIMESTAMP
from ..db.base import Base
from datetime import  timezone 
from enum import Enum
from sqlalchemy.sql import func
from .appoinment_model import AppointmentModel
from sqlalchemy.orm import relationship
class DocumentType(str,Enum):
    RECORD="RECORD"
    INUSRANCE="INSURANCE"

class DocumentModel(Base):
    __tablename__="document_model"
    id=Column(Integer,primary_key=True,nullable=False)
    document_name=Column(String,nullable=False)
    document_type=Column(PYENUM(DocumentType),nullable=False)
    uploaded_at=Column(TIMESTAMP(timezone=True),nullable=False,server_default=func.now())

    #realtionship with patient
    patient_id=Column(Integer,ForeignKey("user_model.id"),nullable=False)
    patient=relationship("UserModel",back_populates="document")

    #realtionship with appoinment 
    appoinment_id=Column(Integer,ForeignKey("appointment_model.id"),nullable=False)
    appoinment=relationship("AppointmentModel",back_populates="document")


