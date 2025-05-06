import random

from fastapi import HTTPException
from starlette import status

from src.core.redis_client import RedisClient
from src.notification import NotificationService, EmailNotification


class OTPService:
    def __init__(self, notification_service: NotificationService, redis_client: RedisClient):
        self.notification_service = notification_service
        self.redis_client = redis_client
        self.redis_ttl = 300

    @staticmethod
    def _generate_otp_code(length: int = 6) -> str:
        return ''.join([str(random.randint(0, 9)) for _ in range(length)])

    async def send_and_save_otp(self, email: str) -> bool:
        otp_code = self._generate_otp_code()
        subject = "Your One-Time Password"
        body = f"Hello!\n\nYour OTP code is: {otp_code}\n\nRegards."

        self.notification_service.set_strategy(EmailNotification())
        success = await self.notification_service.send_notification(email, subject, body)
        if success:
            await self.save_otp(email, otp_code)

        return success

    async def save_otp(self, email:str, code:str) -> None:
        return await self.redis_client.set(
            key = f"otp:{email}",
            value=code,
            ex=self.redis_ttl
        )

    async def verify_otp(self, email: str, code: str) -> bool:
        key = f'otp:{email}'
        stored_code = await self.redis_client.get(key=key)

        if not stored_code:
            raise HTTPException(status_code=404, detail="OTP not found or expired")

        if stored_code != code:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='OTP is incorrect'
            )

        await self.redis_client.delete(key=key)
        return True




