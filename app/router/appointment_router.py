import asyncio

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, WebSocket, status
from sqlalchemy.orm import Session

from ..db.base import Session as DbSession
from ..db.base import get_db
from ..dependecies.jwt_bearer import verify_access_token
from ..dependecies.jwt_handler import get_current_user
from ..dependecies.role_checker import role_necessary
from ..model.appoinment_model import AppointmentStatus
from ..model.document_model import DocumentType
from ..model.user_model import RoleEnum
from ..repo import appointment_repo
from ..schema.appointment_schema import (
    AppointmentCreate,
    AppointmentDetail,
    AppointmentResponse,
    IntakeSubmit,
    QueueItem,
    VisitSummaryCreate,
)
from ..schema.user_schema import TokenData
from ..service import appointemnet_service as service


router = APIRouter(prefix="/appointment", tags=["Appointment"])


@router.post("/create/{patient_id}", response_model=AppointmentResponse)
def create_appointment(
    patient_id: int,
    data: AppointmentCreate,
    db: Session = Depends(get_db),
    user: TokenData = Depends(get_current_user),
):
    if user.role == RoleEnum.PATIENT and user.id != patient_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Patients can only book for themselves.")
    if user.role == RoleEnum.CLINICIAN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Clinicians cannot book patient appointments.")
    return service.create_appointment_for_patient(patient_id, data, db)


@router.get("/mine", response_model=list[AppointmentResponse])
def my_appointments(db: Session = Depends(get_db), user: TokenData = Depends(get_current_user)):
    if user.role != RoleEnum.PATIENT:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only patients can use this endpoint.")
    return appointment_repo.list_patient_appointments(db, user.id)


@router.get("/schedule", response_model=list[AppointmentResponse])
def schedule(
    db: Session = Depends(get_db),
    user: TokenData = Depends(role_necessary([RoleEnum.FRONT_DESK.value, RoleEnum.CLINICIAN.value])),
):
    if user.role == RoleEnum.FRONT_DESK:
        return appointment_repo.list_schedule(db)
    if user.role == RoleEnum.CLINICIAN:
        return appointment_repo.list_clinician_schedule(db, user.id)
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Patients cannot see the full schedule.")


@router.get("/detail/{appointment_id}", response_model=AppointmentDetail)
def appointment_detail(appointment_id: int, db: Session = Depends(get_db), user: TokenData = Depends(get_current_user)):
    appointment = service.get_appointment_for_user(appointment_id, db)
    if not service.can_access_appointment(user, appointment):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot access this appointment.")
    if user.role == RoleEnum.FRONT_DESK:
        detail = AppointmentDetail.model_validate(appointment, from_attributes=True)
        detail.visit_summary = None
        return detail
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


@router.post("/{appointment_id}/documents")
def upload_document(
    appointment_id: int,
    document_type: DocumentType,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: TokenData = Depends(get_current_user),
):
    appointment = service.get_appointment_for_user(appointment_id, db)
    if not service.can_access_appointment(user, appointment):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot upload this document.")
    document = service.save_document(appointment, document_type, file)
    document = appointment_repo.add_document(db, document)
    return {"message": "Document uploaded.", "document_id": document.id}


@router.get("/{appointment_id}/documents/{document_id}")
def download_document(
    appointment_id: int,
    document_id: int,
    db: Session = Depends(get_db),
    user: TokenData = Depends(get_current_user),
):
    appointment = service.get_appointment_for_user(appointment_id, db)
    if not service.can_access_appointment(user, appointment):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You cannot access this document.")
    document = appointment_repo.get_document(db, appointment_id, document_id)
    if not document:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found.")
    return {"document_name": document.document_name, "file_path": document.file_path}


@router.post("/{appointment_id}/check-in", response_model=AppointmentResponse)
def check_in(appointment_id: int, db: Session = Depends(get_db), user: TokenData = Depends(get_current_user)):
    appointment = service.get_appointment_for_user(appointment_id, db)
    appointment = service.check_in_appointment(db, appointment, user)
    return appointment


@router.post("/{appointment_id}/call-back", response_model=AppointmentResponse)
def call_back(appointment_id: int, db: Session = Depends(get_db), user: TokenData = Depends(role_necessary(RoleEnum.CLINICIAN.value))):
    appointment = service.get_appointment_for_user(appointment_id, db)
    appointment = service.call_back_appointment(db, appointment, user)
    return appointment


@router.post("/{appointment_id}/summary", response_model=AppointmentDetail)
def add_visit_summary(
    appointment_id: int,
    data: VisitSummaryCreate,
    db: Session = Depends(get_db),
    user: TokenData = Depends(role_necessary(RoleEnum.CLINICIAN.value)),
):
    appointment = service.get_appointment_for_user(appointment_id, db)
    appointment = service.add_summary(db, appointment, data, user)
    return AppointmentDetail.model_validate(appointment, from_attributes=True)


@router.get("/queue/live", response_model=list[QueueItem])
def live_queue(db: Session = Depends(get_db), user: TokenData = Depends(get_current_user)):
    return service.queue_items_for_user(db, user)


@router.websocket("/queue/ws")
async def queue_websocket(websocket: WebSocket, token: str):
    await websocket.accept()
    try:
        user = verify_access_token(token, HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"))
    except HTTPException:
        await websocket.close(code=1008)
        return

    db = DbSession()
    try:
        while True:
            payload = service.queue_items_for_user(db, user)
            await websocket.send_json(payload)
            await asyncio.sleep(2)
    finally:
        db.close()
