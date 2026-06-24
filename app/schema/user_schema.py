from pydantic import BaseModel , EmailStr
from datetime import datetime
from ..model.user_model import RoleEnum

class UserCreate(BaseModel):
    name:str
    email:EmailStr
    password:str
    role:RoleEnum

class UserResponse(BaseModel):
    id:int
    name:str
    email:EmailStr
    
    role:RoleEnum

class Login(BaseModel):
    username:str
    password:str

class Token(BaseModel):
    access_token:str
    token_type:str


class TokenData(BaseModel):
    id:int
    role:RoleEnum
