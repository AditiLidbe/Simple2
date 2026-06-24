from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestFormStrict
from ..repo import user_repo  
from ..schema.user_schema import UserCreate
from ..utils.hashing import hash 


def create_user(name,email,password,role,db:Session):
    existing_user=user_repo.get_user_by_email(email,db)
    try:
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User alredy exists")
        hashed_password=hash(password)
    except Exception as e:
        return {"message":f"Erro possibly due to existing user,{e}"}
    
    return user_repo.create_user(name=name,
                       email=email,
                       password=hashed_password,
                       role=role,
                       db=db,
                       )
