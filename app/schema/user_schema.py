from pydantic import BaseModel , EmailStr
from datetime import datetime
from ..model.user_model import RoleEnum

class UserCreate(BaseModel):
    name:int
    email:EmailStr
    password:str
    created_at:datetime


class Token(BaseModel):
    access_token:str
    token_type:str


class TokenData(BaseModel):
    id:int
    role:RoleEnum
