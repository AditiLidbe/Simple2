from fastapi import HTTPException,status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestFormStrict
from ..repo.user_repo import get_user_by_email
from ..utils.hashing import verify
from ..dependecies.jwt_bearer import create_access_token
from ..schema.user_schema import Login

def login_user(email,password, db: Session):
    user = get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password ",
        )
    
    if not password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password is not set for this account",
        )

    if not verify(password,user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not a valid password",
        )

    access_token = create_access_token(data={"user_id": user.id,
                                             "role":user.role})
    return {"access_token": access_token, "token_type": "bearer"}



