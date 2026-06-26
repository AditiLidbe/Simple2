from datetime import datetime, timezone, timedelta
from pathlib import Path
import shutil

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ..model.appoinment_model import AppointmentStatus
from ..model.document_model import DocumentModel, DocumentType
from ..model.user_model import RoleEnum
from ..repo import appointment_repo
from ..repo.user_repo import get_user_by_id
from ..service.email_service import send_email


def create_appointment_for_patient(patient_id: int, data, db: Session):
    patient = get_user_by_id(db, patient_id)
    clinician = get_user_by_id(db, data.clinician_id)
    if not patient or patient.role != RoleEnum.PATIENT:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Patient not found.")
    if not clinician or clinician.role != RoleEnum.CLINICIAN:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Selected clinician is not valid.")

    appointment = appointment_repo.create_appointment(
        patient_id=patient_id,
        clinician_id=data.clinician_id,
        date=data.date,
        reason=data.reason,
        status=AppointmentStatus.BOOKED,
        db=db,
    )
    send_email(
        patient.email,
        "Threshold appointment confirmed",
        f"Your appointment is booked for {appointment.date}. Please complete intake before arriving.",
    )
    return appointment


def get_appointment_for_user(appointment_id: int, db: Session):
    appointment = appointment_repo.get_appointment_by_id(db, appointment_id)
    if not appointment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Appointment not found.")
    return appointment


def complete_intake(db: Session, appointment, data, user):
    if user.role != RoleEnum.PATIENT or appointment.patient_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only complete your own intake.")
    if appointment.status in [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This appointment is already finished.")
    appointment.personal_details = data.personal_details
    appointment.medical_history = data.medical_history
    appointment.reason = data.reason
    appointment.intake_status = "COMPLETE"
    return appointment_repo.update_appointment(db, appointment)


def save_document(
    appointment,
    document_type: DocumentType,
    file: UploadFile,
):
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Please upload a valid file.")

    folder = Path("uploads") / str(appointment.id)
    folder.mkdir(parents=True, exist_ok=True)
    safe_name = Path(file.filename).name
    file_path = folder / f"{document_type.value.lower()}_{safe_name}"

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return DocumentModel(
        document_name=safe_name,
        file_path=str(file_path),
        content_type=file.content_type,
        document_type=document_type,
        patient_id=appointment.patient_id,
        appoinment_id=appointment.id,
    )


def can_access_appointment(user, appointment):
    return (
        (user.role == RoleEnum.PATIENT and appointment.patient_id == user.id)
        or (user.role == RoleEnum.CLINICIAN and appointment.clinician_id == user.id)
        or user.role == RoleEnum.FRONT_DESK
    )


def check_in_appointment(db: Session, appointment, user):
    if not (user.role == RoleEnum.PATIENT and appointment.patient_id == user.id) and user.role != RoleEnum.FRONT_DESK:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot check in this appointment.")
    if appointment.status != AppointmentStatus.BOOKED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only booked appointments can be checked in.")
    appointment.status = AppointmentStatus.WAITING
    appointment.checked_in_at = datetime.now(timezone.utc)
    return appointment_repo.update_appointment(db, appointment)


def call_back_appointment(db: Session, appointment, user):
    if user.role != RoleEnum.CLINICIAN or appointment.clinician_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the assigned clinician can call back.")
    if appointment.status != AppointmentStatus.WAITING:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only waiting patients can be called back.")
    appointment.status = AppointmentStatus.CALLED_BACK
    appointment.called_at = datetime.now(timezone.utc)
    return appointment_repo.update_appointment(db, appointment)


def add_summary(db: Session, appointment, data, user):
    if user.role != RoleEnum.CLINICIAN or appointment.clinician_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the assigned clinician can write the summary.")
    if appointment.status not in [AppointmentStatus.CALLED_BACK, AppointmentStatus.WAITING]:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="The patient must be in the visit flow first.")
    appointment.visit_summary = data.summary
    appointment.status = AppointmentStatus.COMPLETED
    return appointment_repo.update_appointment(db, appointment)


class RescheduleError(Exception):
    def __init__(self, reason: str, message: str):
        self.reason = reason
        self.message = message


def reschedule_appointment_service(db: Session, appointment, new_start_time):
    if appointment.status in [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]:
        raise RescheduleError("not_reschedulable", "This appointment cannot be rescheduled.")
    appointment.date = new_start_time
    return appointment_repo.update_appointment(db, appointment)


def queue_items_for_user(db: Session, user):
    appointments = appointment_repo.list_queue(db)
    queue = []

    for appointment in appointments:
        if user.role == RoleEnum.PATIENT and appointment.patient_id != user.id:
            continue
        if user.role == RoleEnum.CLINICIAN and appointment.clinician_id != user.id:
            continue

        queue.append(
            {
                "appointment_id": appointment.id,
                "patient_id": appointment.patient_id,
                "patient_name": appointment.patient.name,
                "clinician_id": appointment.clinician_id,
                "appointment_time": appointment.date,
                "status": appointment.status,
                "position": len(queue) + 1 if appointment.status == AppointmentStatus.WAITING else None,
            }
        )

    return queue

