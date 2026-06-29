from fastapi import FastAPI
from app.db.base import Base, engine
from app.model import appoinment_model, document_model, user_model, chat_model
from app.router import auth_router as AuthRouter
from app.router import user_router as UserRouter
from app.router import appointment_router as AppointmentRouter
from app.router import frontdesk_router as FrontDeskRouter
from app.router import clinician_router as ClinicianRouter

app=FastAPI(title="THRESHOLD")
Base.metadata.create_all(bind=engine)
app.include_router(AuthRouter.router)  
app.include_router(UserRouter.router)
app.include_router(AppointmentRouter.router)
app.include_router(FrontDeskRouter.router)
app.include_router(ClinicianRouter.router)
