from fastapi import Depends

from src.core.database import Services
from src.users import UserService


def get_services():
    return Services()


def get_user_service(service: Services = Depends(get_services)) -> UserService:
    return service.user