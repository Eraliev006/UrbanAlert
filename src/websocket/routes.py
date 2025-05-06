from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from starlette.websockets import WebSocket, WebSocketDisconnect

from src.core import get_current_user
from src.users import UserRead
from src.websocket import manager

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, current_user: Annotated[UserRead, Depends(get_current_user)]):
    await manager.connect(current_user.id, websocket)

    try:
        while True:
            await websocket.receive_json()
    except WebSocketDisconnect:
        manager.disconnect(current_user.id)
