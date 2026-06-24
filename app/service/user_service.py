from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestFormStrict
from ..repo.user_repo import get_user_by_email ,create_user
from ..schema.user_schema import UserCreate
from ..utils.hashing import hash 


def create_user(data:UserCreate,db:Session):
    existing_user=get_user_by_email(data.email,db)
    try:
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT,detail="User alredy exists")
        hashed_password=hash(data.password)
    except Exception as e:
        return {"message":"Erro possibly due to existing user"}
    
    return create_user(db,
                       name=data.name,
                       email=data.email,
                       password=hashed_password,
                       role=data.role,
                       )
