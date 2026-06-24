from fastapi import Depends,HTTPException,status
from ..dependecies.jwt_handler import get_current_user
from ..schema.user_schema import TokenData
from ..model.user_model import RoleEnum


allowed_roles={role.value for role in RoleEnum}

def role_necessary(allowed_roles: str):
    def only_role(user:TokenData=Depends(get_current_user)):
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions."
            )
        return user
    return only_role
