from pydantic import BaseModel , EmailStr
from datetime import datetime
from ..model.appoinment_model import AppointmentStatus

class AppointmentCreate(BaseModel):
    date:datetime
    # status:AppointmentStatus
    
class  AppointmentResponse(BaseModel):
    id:int
    date:datetime
    status:AppointmentStatus
    
   
