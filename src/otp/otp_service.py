import random
import logging

from fastapi import HTTPException
from starlette import status

from src.core.redis_client import RedisClient
from src.notification import NotificationService, EmailNotification

# Логгер для OTPService
logger = logging.getLogger('fixkg.otp_service')


class OTPService:
    def __init__(self, notification_service: NotificationService, redis_client: RedisClient):
        self.notification_service = notification_service
        self.redis_client = redis_client
        self.redis_ttl = 300
        logger.info('OTPService initialized with NotificationService and RedisClient')

    @staticmethod
    def _generate_otp_code(length: int = 6) -> str:
        otp = ''.join([str(random.randint(0, 9)) for _ in range(length)])
        logger.debug(f'Generated OTP code: {otp}')
        return otp

    async def send_and_save_otp(self, email: str) -> bool:
        otp_code = self._generate_otp_code()
        subject = "Your One-Time Password"
        body = f"Hello!\n\nYour OTP code is: {otp_code}\n\nRegards."

        logger.info(f'Sending OTP to email: {email}')
        self.notification_service.set_strategy(EmailNotification())
        success = await self.notification_service.send_notification(email, subject, body)

        if success:
            logger.info(f'Successfully sent OTP to {email}')
            await self.save_otp(email, otp_code)
        else:
            logger.error(f'Failed to send OTP to {email}')

        return success

    async def save_otp(self, email: str, code: str) -> None:
        logger.debug(f'Saving OTP code for {email} in Redis')
        await self.redis_client.set(
            key=f"otp:{email}",
            value=code,
            ex=self.redis_ttl
        )
        logger.info(f'OTP for {email} saved successfully with TTL {self.redis_ttl} seconds')

    async def verify_otp(self, email: str, code: str) -> bool:
        key = f'otp:{email}'
        logger.debug(f'Verifying OTP for {email}')
        stored_code = await self.redis_client.get(key=key)

        if not stored_code:
            logger.warning(f'OTP not found or expired for {email}')
            raise HTTPException(status_code=404, detail="OTP not found or expired")

        if stored_code != code:
            logger.error(f'Incorrect OTP for {email}')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='OTP is incorrect'
            )

        await self.redis_client.delete(key=key)
        logger.info(f'OTP for {email} verified and deleted successfully')
        return True
