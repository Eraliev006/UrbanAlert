from .notification_strategy import NotificationStrategy

class WebSocketNotification(NotificationStrategy):
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager

    async def notify(self, recipient: str, subject: str, message: str) -> bool:
        user_id = int(recipient)
        message_data = {"subject": subject, "message": message}
        await self.connection_manager.send_to_user(user_id, message_data)
        return True