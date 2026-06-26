from sqlalchemy.orm import Session

from ..model.chat_model import ChatMessageModel, ChatSessionModel


def get_session_by_appointment(db: Session, appointment_id: int, patient_id: int):
    return (
        db.query(ChatSessionModel)
        .filter(ChatSessionModel.appointment_id == appointment_id, ChatSessionModel.patient_id == patient_id)
        .first()
    )


def create_session(db: Session, appointment_id: int, patient_id: int):
    session = ChatSessionModel(appointment_id=appointment_id, patient_id=patient_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def add_message(db: Session, session_id: int, sender, message: str):
    chat_message = ChatMessageModel(session_id=session_id, sender=sender, message=message)
    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)
    return chat_message


def get_session_with_messages(db: Session, session_id: int):
    return db.query(ChatSessionModel).filter(ChatSessionModel.id == session_id).first()
