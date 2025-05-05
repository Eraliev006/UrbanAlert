from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from .database_helper import database_helper
from .base_services import Services

from src.users import UserService
from src.auth import AuthService
from src.complaints import ComplaintService
from src.tokens import TokenService
from ..comments.services import CommentService


def get_service(db: AsyncSession = Depends(database_helper.session_getter)) -> Services:
    return Services(db)

def get_user_service(service: Services = Depends(get_service)) -> UserService:
    return service.user_service

def get_auth_service(service: Services = Depends(get_service)) -> AuthService:
    return service.auth_service

def get_token_service(service: Services = Depends(get_service)) -> TokenService:
    return service.token_service

def get_complaint_service(service: Services = Depends(get_service)) -> ComplaintService:
    return service.complaint_service

def get_comment_service(service: Services = Depends(get_service)) -> CommentService:
    return service.comment_service