from email.message import EmailMessage

import aiosmtplib

from src.core import settings
from .notification_strategy import NotificationStrategy


class EmailNotification(NotificationStrategy):
    def __init__(self):
        self.smtp_host = settings.smtp.smtp_host
        self.smtp_port = settings.smtp.smtp_port
        self.smtp_user = settings.smtp.smtp_user
        self.smtp_password = settings.smtp.smtp_password

    async def notify(self, recipient: str, subject: str, message: str) -> bool:
        email = EmailMessage()
        email["From"] = self.smtp_user
        email["To"] = recipient
        email["Subject"] = subject
        email.set_content(message)

        try:
            await aiosmtplib.send(
                email,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=True,
                username=self.smtp_user,
                password=self.smtp_password
            )
            return True
        except aiosmtplib.SMTPException as e:
            return False