from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..schema.user_schema import UserCreate, UserResponse
from ..service.user_service import create_user
from ..utils.logger import logger


router=APIRouter(prefix='/user',tags=["User"])

logger.info("User Router..")

@router.post("/create",response_model=UserResponse)
def lets_create_user(data:UserCreate,db:Session=Depends(get_db)):
    return create_user(data.name,data.email,data.password,data.role,db)
