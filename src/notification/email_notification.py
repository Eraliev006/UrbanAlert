from logging import getLogger
from email.message import EmailMessage
import aiosmtplib

from src.core import settings
from .notification_strategy import NotificationStrategy

logger = getLogger('fixkg.email_notification')

class EmailNotification(NotificationStrategy):
    def __init__(self):
        self.smtp_host = settings.smtp.hostname
        self.smtp_port = settings.smtp.port
        self.smtp_user = settings.smtp.user_email
        self.smtp_password = settings.smtp.password
        logger.info("EmailNotification initialized with SMTP host: %s, port: %d", self.smtp_host, self.smtp_port)

    async def notify(self, recipient: str, subject: str, message: str) -> bool:
        email = EmailMessage()
        email["From"] = self.smtp_user
        email["To"] = recipient
        email["Subject"] = subject
        email.set_content(message)

        logger.info("Attempting to send email to %s with subject: %s", recipient, subject)

        try:
            await aiosmtplib.send(
                email,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=True,
                username=self.smtp_user,
                password=self.smtp_password
            )
            logger.info("Email successfully sent to %s", recipient)
            return True
        except aiosmtplib.SMTPException as e:
            logger.error("Failed to send email to %s: %s", recipient, str(e))
            return False
