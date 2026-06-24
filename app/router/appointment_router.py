from fastapi import APIRouter,Depends
from ..db.base import Base ,get_db
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestFormStrict
from ..service.appointemnet_service import create_appointment_for_patient
from ..model.user_model import RoleEnum
from ..schema.appointment_schema import AppointmentCreate,AppointmentResponse
from ..dependecies.role_checker import role_necessary
from ..utils.logger import logger


router=APIRouter(prefix='/appointment',tags=["Appointment"])

logger.info("Appointment Router..")


# user=Depends(role_necessary("PATIENT")
@router.post("/create/{patient_id}",response_model=AppointmentResponse)
def create_appointment(patient_id:int,data:AppointmentCreate,db:Session=Depends(get_db)):
    return create_appointment_for_patient(patient_id,data,db)


