from fastapi import Depends, HTTPException, status
from ..dependecies.jwt_handler import get_current_user
from ..schema.user_schema import TokenData
from ..model.user_model import RoleEnum


allowed_roles = {role.value for role in RoleEnum}

def role_necessary(allowed_roles: str|list[str]):
    def only_role(user:TokenData=Depends(get_current_user)):
        roles = [allowed_roles] if isinstance(allowed_roles, str) else allowed_roles
        user_role = user.role.value if isinstance(user.role, RoleEnum) else user.role
        if user_role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions."
            )
        return user
    return only_role
