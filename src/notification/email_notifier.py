from email.message import EmailMessage

from src.core import settings
from src.notification import Notifier


class EmailNotifier(Notifier):

    def notify(self, to_user: str, otp_code: str):
        message = EmailMessage()
        message['From'] = settings.smtp.user_email
        message['To'] = to_user
        message['Subject'] = f'Your One-Time Password — {otp_code}'
