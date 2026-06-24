from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestFormStrict
from ..repo import appointment_repo
from ..schema.appointment_schema import AppointmentStatus




def create_appointment_for_patient(patient_id,data,db:Session):
    return appointment_repo.create_appointment(date=data.date,
                                               status=AppointmentStatus.WAITING,
                                               db=db,
                                               )
