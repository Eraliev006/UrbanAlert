from typing import Annotated

from fastapi import APIRouter, Depends

from src.complaints import ComplaintService, ComplaintUpdate
from src.core import get_current_user
from src.core.dependencies import get_complaint_service
from src.users import UserRead

router = APIRouter(
    tags=['Complaints'],
    prefix='/complaints',
    dependencies=[Depends(get_current_user)]
)

COMPLAINT_SERVICE_DEP = Annotated[ComplaintService, Depends(get_complaint_service)]
CURRENT_USER_DEP = Annotated[UserRead, Depends(get_current_user)]


@router.get('/')
async def get_all_complaints_route(complaint_service: COMPLAINT_SERVICE_DEP):
    return await complaint_service.get_all()

@router.get('/{complaint_id}')
async def get_complaint_by_id_route(
        complaint_id: int,
        complaint_service: COMPLAINT_SERVICE_DEP
):
    return await complaint_service.get_by_id(complaint_id)


@router.patch('/{complaint_id}')
async def update_complaint_by_id(
        complaint_id: int,
        complaint_update_data: ComplaintUpdate,
        complaint_service: COMPLAINT_SERVICE_DEP,
        current_user: CURRENT_USER_DEP
):
    return await complaint_service.update_complaint(
        complaint_id = complaint_id,
        new_data = complaint_update_data,
        user_id=current_user.id
    )
