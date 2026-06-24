from fastapi import APIRouter,Depends
from ..db.base import Base ,get_db
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestFormStrict
from ..service import auth_service,user_service
from ..model.user_model import RoleEnum
from ..schema.user_schema import UserCreate,Token, UserResponse
from ..dependecies.role_checker import role_necessary
from ..utils.logger import logger


router=APIRouter(prefix='/user',tags=["User"])

logger.info("User Router..")

@router.post("/create",response_model=UserResponse)
def create_user(data:UserCreate,db:Session=Depends(get_db),user=Depends(role_necessary("PATIENT"))):
    return create_user(data,db)

