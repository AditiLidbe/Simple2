from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from ..model.appoinment_model import AppointmentStatus
from ..model.chat_model import ChatRole
from ..model.user_model import RoleEnum
from ..repo import appointment_repo, chat_repo
from . import appointemnet_service as appointment_service


def get_or_create_chat_session(db: Session, appointment_id: int, user_id: int):
    session = chat_repo.get_session_by_appointment(db, appointment_id, user_id)
    if session:
        return session
    return chat_repo.create_session(db, appointment_id, user_id)


def get_chat_history(db: Session, appointment_id: int, user_id: int):
    session = chat_repo.get_session_by_appointment(db, appointment_id, user_id)
    if not session:
        return None
    return chat_repo.get_session_with_messages(db, session.id)


def handle_message(db: Session, appointment, user, message: str, requested_datetime=None):
    if user.role != RoleEnum.PATIENT or appointment.patient_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only use the assistant for your own appointment.")

    session = get_or_create_chat_session(db, appointment.id, user.id)
    chat_repo.add_message(db, session.id, ChatRole.PATIENT, message)

    clean_message = message.lower().strip()

    if "what" in clean_message and ("need" in clean_message or "left" in clean_message or "appointment" in clean_message):
        missing_items = appointment_service.get_missing_intake_items(appointment)
        if missing_items:
            reply = f"You still need: {', '.join(missing_items)}."
        else:
            reply = "Your intake looks complete."
    elif "move" in clean_message or "reschedule" in clean_message:
        if appointment.status in [AppointmentStatus.COMPLETED, AppointmentStatus.CANCELLED]:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="This appointment cannot be rescheduled.")
        appointment.date = requested_datetime or appointment_service.next_tuesday_afternoon()
        appointment_repo.update_appointment(db, appointment)
        reply = f"Your appointment has been moved to {appointment.date}."
    else:
        appointment.pre_visit_summary = f"Patient said: {message.strip()}"
        appointment_repo.update_appointment(db, appointment)
        reply = "I saved that note as a pre-visit summary for the clinician."

    chat_repo.add_message(db, session.id, ChatRole.ASSISTANT, reply)
    session = chat_repo.get_session_with_messages(db, session.id)
    return session, reply
