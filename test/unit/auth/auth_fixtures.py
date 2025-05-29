from unittest.mock import AsyncMock

import pytest
from fastapi.security import OAuth2PasswordRequestForm

from src.auth import AuthService, VerifyEmailSchema


@pytest.fixture()
def mock_token_service():
    service = AsyncMock()
    return service

@pytest.fixture()
def mock_otp_service():
    service = AsyncMock()
    return service

@pytest.fixture()
def auth_service(mock_user_service, mock_user_repository,mock_otp_service,mock_token_service):
    return AuthService(
        user_service=mock_user_service,
        token_service=mock_token_service,
        otp_service=mock_otp_service,
        user_repo=mock_user_repository,
    )

@pytest.fixture()
def mock_login_form_data():
    return OAuth2PasswordRequestForm(
        username="test_user",
        password="plain_password",
        scope="",
        client_id=None,
        client_secret=None
    )

@pytest.fixture()
def mock_verify_email_schema(mock_user):
    return VerifyEmailSchema(
        email = mock_user.email,
        otp_code = '1111'
    )