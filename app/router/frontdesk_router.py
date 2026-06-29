import asyncio

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, WebSocket, status
from sqlalchemy.orm import Session

from ..db.base import Session as DbSession, get_db
from ..dependecies.jwt_bearer import verify_access_token
from ..dependecies.role_checker import role_necessary
from ..model.document_model import DocumentType
from ..model.user_model import RoleEnum
from ..repo import appointment_repo
from ..schema.appointment_schema import AppointmentDetail, AppointmentResponse, QueueItem
from ..schema.user_schema import TokenData
from ..service import appointemnet_service as service

router = APIRouter(prefix="/frontdesk", tags=["Front Desk"])


@router.get("/schedule", response_model=list[AppointmentResponse])
def schedule(db: Session = Depends(get_db), user: TokenData = Depends(role_necessary(RoleEnum.FRONT_DESK.value))):
    return appointment_repo.list_schedule(db)


@router.get("/queue", response_model=list[QueueItem])
def queue(db: Session = Depends(get_db), user: TokenData = Depends(role_necessary(RoleEnum.FRONT_DESK.value))):
    return service.queue_items_for_user(db, user)


@router.get("/appointments/{appointment_id}", response_model=AppointmentDetail)
def appointment_detail(appointment_id: int, db: Session = Depends(get_db), user: TokenData = Depends(role_necessary(RoleEnum.FRONT_DESK.value))):
    appointment = service.get_appointment_for_user(appointment_id, db)
    detail = AppointmentDetail.model_validate(appointment, from_attributes=True)
    detail.visit_summary = None
    return detail


@router.post("/appointments/{appointment_id}/check-in", response_model=AppointmentResponse)
def check_in(appointment_id: int, db: Session = Depends(get_db), user: TokenData = Depends(role_necessary(RoleEnum.FRONT_DESK.value))):
    appointment = service.get_appointment_for_user(appointment_id, db)
    return service.check_in_appointment(db, appointment, user)


@router.post("/appointments/{appointment_id}/documents")
def upload_document(
    appointment_id: int,
    document_type: DocumentType,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: TokenData = Depends(role_necessary(RoleEnum.FRONT_DESK.value)),
):
    appointment = service.get_appointment_for_user(appointment_id, db)
    document = service.save_document(appointment, document_type, file)
    document = appointment_repo.add_document(db, document)
    return {"message": "Document uploaded.", "document_id": document.id}


@router.websocket("/queue/ws")
async def queue_websocket(websocket: WebSocket, token: str):
    try:
        user = verify_access_token(token, HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"))
    except HTTPException:
        await websocket.close(code=1008)
        return

    if user.role != RoleEnum.FRONT_DESK:
        await websocket.close(code=1008)
        return

    await websocket.accept()
    db = DbSession()
    try:
        while True:
            payload = service.queue_items_for_user(db, user)
            await websocket.send_json(payload)
            await asyncio.sleep(2)
    except Exception:
        pass
    finally:
        db.close()
