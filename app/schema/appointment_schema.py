from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any
from ..model.appoinment_model import AppointmentStatus
from ..model.document_model import DocumentType

class AppointmentCreate(BaseModel):
    date:datetime
    clinician_id:int
    reason:str=Field(min_length=3)
    
class  AppointmentResponse(BaseModel):
    id:int
    date:datetime
    status:AppointmentStatus
    patient_id:int
    clinician_id:int
    reason:str|None=None
    intake_status:str

    class Config:
        from_attributes=True

class IntakeSubmit(BaseModel):
    personal_details:dict[str, Any]
    medical_history:dict[str, Any]
    reason:str=Field(min_length=3)

class VisitSummaryCreate(BaseModel):
    summary:str=Field(min_length=5)

class DocumentResponse(BaseModel):
    id:int
    document_name:str
    document_type:DocumentType
    content_type:str|None=None

    class Config:
        from_attributes=True

class AppointmentDetail(AppointmentResponse):
    personal_details:dict[str, Any]|None=None
    medical_history:dict[str, Any]|None=None
    pre_visit_summary:str|None=None
    visit_summary:str|None=None
    documents:list[DocumentResponse]=[]

    class Config:
        from_attributes=True

class QueueItem(BaseModel):
    appointment_id:int
    patient_id:int
    patient_name:str
    clinician_id:int
    appointment_time:datetime
    status:AppointmentStatus
    position:int|None=None

    class Config:
        from_attributes=True
   
