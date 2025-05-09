from logging import getLogger

from src.notification import NotificationStrategy

# Логгер для NotificationService
logger = getLogger('fixkg.notification_service')

class NotificationService:
    def __init__(self, strategy: NotificationStrategy = None):
        self._strategy = strategy
        logger.info("NotificationService initialized with strategy: %s", self._strategy.__class__.__name__ if self._strategy else "None")

    def set_strategy(self, strategy: NotificationStrategy):
        self._strategy = strategy
        # Логирование смены стратегии
        logger.info("Notification strategy set to: %s", self._strategy.__class__.__name__)

    async def send_notification(self, recipient: str, subject: str, message: str):
        # Логирование начала отправки уведомления
        logger.info("Attempting to send notification to %s with subject: %s", recipient, subject)

        try:
            await self._strategy.notify(recipient, subject, message)
            logger.info("Notification successfully sent to %s", recipient)
        except Exception as e:
            # Логирование ошибки при отправке
            logger.error("Error sending notification to %s: %s", recipient, str(e))
            raise
