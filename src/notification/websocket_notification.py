from logging import getLogger
from .notification_strategy import NotificationStrategy

logger = getLogger('fixkg.websocket_notification')


class WebSocketNotification(NotificationStrategy):
    def __init__(self, connection_manager):
        self.connection_manager = connection_manager
        logger.info("WebSocketNotification initialized with connection_manager: %s", str(self.connection_manager))

    async def notify(self, recipient: str, subject: str, message: str) -> bool:
        user_id = int(recipient)
        message_data = {"subject": subject, "message": message}

        logger.info("Attempting to send WebSocket notification to user %d with subject: %s", user_id, subject)

        try:
            await self.connection_manager.send_to_user(user_id, message_data)
            logger.info("WebSocket notification successfully sent to user %d", user_id)
            return True
        except Exception as e:
            logger.error("Failed to send WebSocket notification to user %d: %s", user_id, str(e))
            return False
