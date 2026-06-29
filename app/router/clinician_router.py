from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..dependecies.role_checker import role_necessary
from ..model.user_model import RoleEnum
from ..repo import appointment_repo
from ..schema.appointment_schema import AppointmentDetail, AppointmentResponse, VisitSummaryCreate
from ..schema.user_schema import TokenData
from ..service import appointemnet_service as service

router = APIRouter(prefix="/clinician", tags=["Clinician"])


@router.get("/schedule", response_model=list[AppointmentResponse])
def schedule(db: Session = Depends(get_db), user: TokenData = Depends(role_necessary(RoleEnum.CLINICIAN.value))):
    return appointment_repo.list_clinician_schedule(db, user.id)


@router.get("/appointments/{appointment_id}", response_model=AppointmentDetail)
def appointment_detail(appointment_id: int, db: Session = Depends(get_db), user: TokenData = Depends(role_necessary(RoleEnum.CLINICIAN.value))):
    appointment = service.get_appointment_for_user(appointment_id, db)
    if appointment.clinician_id != user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view your own patients.")
    return AppointmentDetail.model_validate(appointment, from_attributes=True)


@router.post("/appointments/{appointment_id}/call-back", response_model=AppointmentResponse)
def call_back(appointment_id: int, db: Session = Depends(get_db), user: TokenData = Depends(role_necessary(RoleEnum.CLINICIAN.value))):
    appointment = service.get_appointment_for_user(appointment_id, db)
    return service.call_back_appointment(db, appointment, user)


@router.post("/appointments/{appointment_id}/summary", response_model=AppointmentDetail)
def add_visit_summary(
    appointment_id: int,
    data: VisitSummaryCreate,
    db: Session = Depends(get_db),
    user: TokenData = Depends(role_necessary(RoleEnum.CLINICIAN.value)),
):
    appointment = service.get_appointment_for_user(appointment_id, db)
    appointment = service.add_summary(db, appointment, data, user)
    return AppointmentDetail.model_validate(appointment, from_attributes=True)
