from email.message import EmailMessage

import aiosmtplib

from src.core import settings
from src.notification import Notifier


class EmailNotifier(Notifier):

    async def notify(self, to_user: str, otp_code: str):
        smtp = settings.smtp
        message = EmailMessage()
        message['From'] = smtp.user_email
        message['To'] = to_user
        message['Subject'] = f'Your One-Time Password — {otp_code}'

        await aiosmtplib.send(
            message,
            hostname=smtp.hostname,
            port=smtp.port,
            start_tls=True,
            username=smtp.user_email,
            password=smtp.password
        )