from sqlalchemy.orm import Session
from ..model.user_model import UserModel ,RoleEnum
from ..utils.logger import logger

logger.info("Authentication Repo..")


def get_user_by_email(db:Session,email:str):
    return db.query(UserModel).filter(UserModel.email == email).first()

def create_user(name:str,email:str,password:str,role:RoleEnum,db:Session):
    new_user=UserModel(name=name,
                       email=email,
                       password=password,
                       role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

