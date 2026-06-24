from sqlalchemy.orm import Session
from datetime import datetime
from ..model.appoinment_model import AppointmentModel ,AppointmentStatus
from ..utils.logger import logger

logger.info("Appointment Repo..")

def create_appointment(date:datetime,status:AppointmentStatus,db:Session):
    new_appointment=AppointmentModel(date=date,
                              status=status)
    db.add(new_appointment)
    db.commit()
    db.refresh(new_appointment)
    return new_appointment



