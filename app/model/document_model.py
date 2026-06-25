from sqlalchemy import Column, String, Integer, ForeignKey, Enum as PYENUM, TIMESTAMP
from ..db.base import Base
from enum import Enum
from sqlalchemy.sql import func
from .appoinment_model import AppointmentModel
from sqlalchemy.orm import relationship
class DocumentType(str,Enum):
    ID="ID"
    INSURANCE="INSURANCE"
    PRIOR_RECORD="PRIOR_RECORD"

class DocumentModel(Base):
    __tablename__="document_model"
    id=Column(Integer,primary_key=True,nullable=False)
    document_name=Column(String,nullable=False)
    file_path=Column(String,nullable=True)
    content_type=Column(String,nullable=True)
    document_type=Column(PYENUM(DocumentType),nullable=False)
    uploaded_at=Column(TIMESTAMP(timezone=True),nullable=False,server_default=func.now())

    #realtionship with patient
    patient_id=Column(Integer,ForeignKey("user_model.id"),nullable=False)
    patient=relationship("UserModel",back_populates="document")

    #realtionship with appoinment 
    appoinment_id=Column(Integer,ForeignKey("appointment_model.id"),nullable=False)
    appoinment=relationship("AppointmentModel",back_populates="document")
