from src.notification import NotificationStrategy


class NotificationService:
    def __init__(self, strategy: NotificationStrategy = None):
        self._strategy = strategy

    def set_strategy(self, strategy: NotificationStrategy):
        self._strategy = strategy

    async def send_notification(self, recipient: str, subject: str, message: str):
        return await self._strategy.notify(recipient, subject, message)