from fastapi.security import OAuth2PasswordBearer

from fastapi import Depends,HTTPException,status
from .jwt_bearer import verify_access_token

oauth2_schemes=OAuth2PasswordBearer(tokenUrl='/auth/login')

def get_current_user(token:str=Depends(oauth2_schemes)):
    credential_exceptions=HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                        detail="not able to verify",
                                        headers={'WWW-Authenticate':'Bearer'},
                                        )
    return verify_access_token(token,credential_exceptions)


