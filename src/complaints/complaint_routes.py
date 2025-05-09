from typing import Annotated

from fastapi import APIRouter, Depends, Query, UploadFile

from src import ComplaintStatus
from src.complaints import ComplaintService, ComplaintUpdate, ComplaintCreate, ComplaintQueryModel
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
async def get_all_complaints_route(
        complaint_service: COMPLAINT_SERVICE_DEP,
        query: Annotated[ComplaintQueryModel, Query()]
):
    return await complaint_service.get_all(query_params=query)

@router.get('/statuses')
async def get_complaint_statuses():
    return [status.value for status in ComplaintStatus]

@router.post('/{complaint_id}/upload_images', dependencies=[Depends(get_current_user)])
async def upload_complaint_image(complaint_id: int, file: UploadFile, complaint_service: COMPLAINT_SERVICE_DEP):
    return await complaint_service.upload_complaint_image(file, complaint_id)

@router.post('/')
async def create_complaints(complaint_service: COMPLAINT_SERVICE_DEP, complaint:ComplaintCreate, current_user: CURRENT_USER_DEP):
    return await complaint_service.create_complaint(
        complaint=complaint,
        user_id=current_user.id
    )

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

@router.delete('/{complaint_id}')
async def delete_complaint_by_id(
        complaint_id: int,
        complaint_service: COMPLAINT_SERVICE_DEP,
        current_user: CURRENT_USER_DEP
):
    return await complaint_service.delete_by_id(
        complaint_id = complaint_id,
        user_id=current_user.id
    )