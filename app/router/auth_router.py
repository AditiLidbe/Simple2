from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db.base import get_db
from ..schema.user_schema import Login, Token, UserCreate, UserResponse
from ..service import auth_service, user_service
from ..utils.logger import logger

router=APIRouter(prefix='/auth',tags=["Authentication"])

logger.info("Authentication Router..")

@router.post("/login",response_model=Token)
def login(data:Login,db:Session=Depends(get_db)):
    logger.info("login attempted..")
    return auth_service.login_user(data.username,data.password,db)

@router.post("/signup",response_model=UserResponse)
def signup(data:UserCreate,db:Session=Depends(get_db)):
     logger.info("User signing up..")
     return user_service.create_user(data.name,data.email,data.password,data.role,db)
