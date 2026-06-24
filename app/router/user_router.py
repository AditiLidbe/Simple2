from fastapi import APIRouter,Depends
from ..service.user_service import create_user
from ..schema.user_schema import UserCreate

