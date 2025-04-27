from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .database_helper import database_helper
from .database import Services

from src.users import UserService
from ..auth import AuthService



def get_service(db: AsyncSession = Depends(database_helper.session_getter)) -> Services:
    return Services(db)

def get_user_service(service: Services = Depends(get_service)) -> UserService:
    return service.user

def get_auth_service(service: Services = Depends(get_service)) -> AuthService:
    return service.auth_service