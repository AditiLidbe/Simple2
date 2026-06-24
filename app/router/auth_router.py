from fastapi import APIRouter,Depends
from ..db.base import Base ,get_db
from sqlalchemy.orm import Session
from ..model.user_model import RoleEnum
# from fastapi.security import OAuth2PasswordRequestFormStrict

from ..service import auth_service,user_service
from ..schema.user_schema import UserCreate,Token, UserResponse, Login
from ..utils.logger import logger

router=APIRouter(prefix='/auth',tags=["Authentication"])

logger.info("Authentication Router..")

@router.post("/login",response_model=Token)
def login(data:Login,db:Session=Depends(get_db)):
    logger.info("login attempted..")
    return auth_service.login_user(data.username,data.password,db)

@router.post("/signup",response_model=UserResponse)
def signup(name:str,email:str,password:str,role:RoleEnum,db:Session=Depends(get_db)):
     logger.info("User signing up..")
     return user_service.create_user(name,email,password,role,db)

