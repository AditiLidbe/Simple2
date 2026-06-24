from fastapi import FastAPI
from app.router import auth_router as AuthRouter
from app.router import user_router as UserRouter
from app.router import appointment_router as AppointmentRouter

app=FastAPI(title="THRESHOLD")
app.include_router(AuthRouter.router)  
app.include_router(UserRouter.router)
app.include_router(AppointmentRouter.router)


