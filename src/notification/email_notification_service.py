from email.message import EmailMessage
import aiosmtplib

from src.core import settings


class EmailNotificationService:
    def __init__(self):
        self.smtp_host = settings.smtp.smtp_host
        self.smtp_port = settings.smtp.smtp_port
        self.smtp_user = settings.smtp.smtp_user
        self.smtp_password = settings.smtp.smtp_password

    async def send_otp(self, to_email: str, otp_code: str) -> bool:
        message = EmailMessage()
        message["From"] = self.smtp_user
        message["To"] = to_email
        message["Subject"] = f"Your One-Time Password — {otp_code}"
        message.set_content(f"Hello!\n\nYour OTP code is: {otp_code}\n\nRegards.")

        try:
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=True,
                username=self.smtp_user,
                password=self.smtp_password
            )
            return True
        except aiosmtplib.SMTPException as e:
            print(f"Failed to send email: {e}")
            return False

