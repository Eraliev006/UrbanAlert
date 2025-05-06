from starlette.websockets import WebSocket


class ConnectionManager:
    def __init__(self):
        self.active_connection: dict[int, WebSocket] = {}

    async def connect(self, user_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connection[user_id] = websocket

    async def disconnect(self, user_id: int):
         self.active_connection.pop(user_id, None)

    async def send_to_user(self, user_id: int, message:dict):
        ws = self.active_connection.get(user_id)

        if ws:
            await ws.send_json(message)

manager = ConnectionManager()