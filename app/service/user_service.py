from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestFormStrict
from ..repo import user_repo  
from ..schema.user_schema import UserCreate
from ..utils.hashing import hash 


def create_user(name,email,password,role,db:Session):
    existing_user=user_repo.get_user_by_email(db,email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User already exists")
    hashed_password=hash(password)
    
    return user_repo.create_user(name=name,
                       email=email,
                       password=hashed_password,
                       role=role,
                       db=db,
                       )
