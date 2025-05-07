from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends
from starlette.websockets import WebSocket, WebSocketDisconnect

from src.users import UserRead
from src.websocket import manager
from src.websocket.utils import get_current_user_from_websocket

router = APIRouter(
    tags=['Websocket notifications']
)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, decoded_token: Annotated[UserRead, Depends(get_current_user_from_websocket)]):
    await manager.connect(int(decoded_token['sub']), websocket)

    try:
        while True:
            await websocket.receive_json()
    except WebSocketDisconnect:
        manager.disconnect(decoded_token['sub'])
