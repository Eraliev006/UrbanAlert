from typing import Any

from fastapi import WebSocket, HTTPException, Depends

from src.core import get_token_service
from src.tokens import TokenService, TokenType


def get_current_user_from_websocket(websocket: WebSocket, token_service: TokenService = Depends(get_token_service)) -> dict[str, Any]:
    token = websocket.headers.get("Authorization").split()[-1]


    if not token:
        raise HTTPException(status_code=401, detail="Unauthorized")
    decoded_token = token_service.decode_token_with_token_type_checking(token, token_type=TokenType.access)

    if not decoded_token:
        raise HTTPException(status_code=401, detail="Invalid token")

    return decoded_token
