from sqlalchemy.ext.asyncio import AsyncSession
from src.auth import AuthService
from src.comments import CommentRepositories
from src.comments.services import CommentService
from src.complaints import ComplaintService
from src.complaints.repositories import ComplaintRepositories
from src.notification import EmailNotification
from src.otp import OTPService
from src.tokens.token_service import TokenService
from src.core import redis_client
from src.users import UserService, UserRepositories


class Services:
    def __init__(self, db: AsyncSession):
        self.token_service = TokenService(redis_client)

        self.user_repository = UserRepositories(db)
        self.user_service = UserService(user_repo=self.user_repository)

        self.complaint_repository = ComplaintRepositories(db)
        self.complaint_service = ComplaintService(self.complaint_repository, self.user_service)

        self.comment_repository = CommentRepositories(db)
        self.comment_service = CommentService(self.comment_repository, self.complaint_service)

        self.email_service = EmailNotification()
        self.otp_service = OTPService(self.email_service, redis_client)

        self.auth_service = AuthService(
            user_service=self.user_service,
            token_service=self.token_service,
            otp_service=self.otp_service
        )
