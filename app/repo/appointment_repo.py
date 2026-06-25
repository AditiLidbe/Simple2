from sqlalchemy.orm import Session
from datetime import datetime
from ..model.appoinment_model import AppointmentModel ,AppointmentStatus
from ..model.document_model import DocumentModel
from ..utils.logger import logger

logger.info("Appointment Repo..")

def create_appointment(patient_id:int,clinician_id:int,date:datetime,reason:str,status:AppointmentStatus,db:Session):
    new_appointment=AppointmentModel(date=date,
                              patient_id=patient_id,
                              clinician_id=clinician_id,
                              reason=reason,
                              status=status)
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment


def get_appointment_by_id(db: Session, appointment_id: int):
    return db.query(AppointmentModel).filter(AppointmentModel.id == appointment_id).first()


def list_patient_appointments(db: Session, patient_id: int):
    return db.query(AppointmentModel).filter(AppointmentModel.patient_id == patient_id).order_by(AppointmentModel.date.desc()).all()


def list_schedule(db: Session):
    return db.query(AppointmentModel).order_by(AppointmentModel.date.asc()).all()


def list_clinician_schedule(db: Session, clinician_id: int):
    return db.query(AppointmentModel).filter(AppointmentModel.clinician_id == clinician_id).order_by(AppointmentModel.date.asc()).all()


def list_queue(db: Session):
    return db.query(AppointmentModel).filter(
        AppointmentModel.status.in_([AppointmentStatus.WAITING, AppointmentStatus.CALLED_BACK])
    ).order_by(AppointmentModel.checked_in_at.asc(), AppointmentModel.created_at.asc()).all()


def get_document(db: Session, appointment_id: int, document_id: int):
    return db.query(DocumentModel).filter(
        DocumentModel.id == document_id,
        DocumentModel.appoinment_id == appointment_id,
    ).first()


def update_appointment(db: Session, appointment: AppointmentModel):
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


def add_document(db: Session, document: DocumentModel):
    db.add(document)
    db.commit()
    db.refresh(document)
    return document
