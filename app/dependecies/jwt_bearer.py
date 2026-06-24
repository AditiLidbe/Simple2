from jose import JWTError,jwt 
from ..db.base import setting
from datetime import datetime,timedelta,timezone
from ..schema.user_schema import TokenData
from ..utils.config import setting



def create_access_token(data:dict):
    to_encoded=data.copy()
    expire=datetime.now(timezone.utc)+timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encoded.update({'exp':expire})
    encoded_jwt=jwt.encode(to_encoded,setting.SECRET_KEY,algorithm=setting.ALGORITHM)
    return encoded_jwt


def verify_access_token(token:str,credential_exceptions):
        try:
            payload=jwt.decode(token,setting.SECRET_KEY,algorithms=[setting.ALGORITHM])
            user_id=payload.get("user_id")
            role=payload.get("role","")

            if user_id is None:
                 raise credential_exceptions
            
            token_data=TokenData(id=user_id,role=role)
            
        except JWTError as e:
             raise credential_exceptions
        return token_data

        
              
            
              