from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..dependecies.jwt_handler import get_current_user
from ..repo import appointment_repo
from ..model.user_model import RoleEnum
from ..schema.appointment_schema import (
    AssistantRequest,
    AssistantResponse,
    AppointmentCreate,
    AppointmentDetail,
    AppointmentResponse,
    IntakeSubmit,
)
from ..schema.chat_schema import ChatSessionResponse
from ..schema.user_schema import TokenData
from ..service import assistant_service
from ..service import appointemnet_service as service


router = APIRouter(prefix="/patient", tags=["Patient"])


@router.post("/create/{patient_id}", response_model=AppointmentResponse)
def create_appointment(
    patient_id: int,
    data: AppointmentCreate,
    db: Session = Depends(get_db),
    user: TokenData = Depends(get_current_user),
):
    if user.id != patient_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Patients can only book for themselves.")
    appointment = service.create_appointment_for_patient(patient_id, data, db)
    return appointment


@router.get("/mine", response_model=list[AppointmentResponse])
def my_appointments(db: Session = Depends(get_db), user: TokenData = Depends(get_current_user)):
    if user.role != RoleEnum.PATIENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only patients can use this endpoint.")
    return appointment_repo.list_patient_appointments(db, user.id)


@router.get("/detail/{appointment_id}", response_model=AppointmentDetail)
def appointment_detail(appointment_id: int, db: Session = Depends(get_db), user: TokenData = Depends(get_current_user)):
    appointment = service.get_appointment_for_user(appointment_id, db)
    if appointment.patient_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot access this appointment.")
    return AppointmentDetail.model_validate(appointment, from_attributes=True)


@router.post("/{appointment_id}/intake", response_model=AppointmentDetail)
def complete_intake(
    appointment_id: int,
    data: IntakeSubmit,
    db: Session = Depends(get_db),
    user: TokenData = Depends(get_current_user),
):
    appointment = service.get_appointment_for_user(appointment_id, db)
    appointment = service.complete_intake(db, appointment, data, user)
    return AppointmentDetail.model_validate(appointment, from_attributes=True)


@router.post("/{appointment_id}/assistant", response_model=AssistantResponse)
def intake_assistant(
    appointment_id: int,
    data: AssistantRequest,
    db: Session = Depends(get_db),
    user: TokenData = Depends(get_current_user),
):
    appointment = service.get_appointment_for_user(appointment_id, db)
    reply = assistant_service.handle_assistant_message(
        db=db,
        appointment=appointment,
        user=user,
        user_message=data.message,
    )
    appointment = service.get_appointment_for_user(appointment_id, db)
    return AssistantResponse(
        reply=reply,
        appointment=AppointmentDetail.model_validate(appointment, from_attributes=True),
    )


@router.get("/{appointment_id}/assistant/history", response_model=ChatSessionResponse)
def assistant_history(
    appointment_id: int,
    db: Session = Depends(get_db),
    user: TokenData = Depends(get_current_user),
):
    appointment = service.get_appointment_for_user(appointment_id, db)
    if appointment.patient_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot access this chat history.")
    session = assistant_service.get_chat_history(db, appointment_id, appointment.patient_id)
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No assistant chat history found.")
    return session
