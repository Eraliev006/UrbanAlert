from unittest.mock import AsyncMock, patch

import pytest

from src.auth import VerifyEmailSchema
from test.unit.user.fixtures import mock_user


class TestAuth:
    @pytest.mark.asyncio
    @patch('src.auth.services.OTPService.send_and_save_otp', new_callable=AsyncMock)
    async def test_register_successful(self, mock_otp_service, async_client, mock_user_create, redis_connection):
        result = await async_client.post('/auth/register-user', json=mock_user_create.model_dump())

        mock_otp_service.assert_awaited_once()
        assert 'id' in result.json()
        assert result.json()['id'] is not None


    @pytest.mark.asyncio
    @patch('src.auth.services.OTPService.send_and_save_otp', new_callable=AsyncMock)
    async def test_register_failed_already_exists(self, mock_otp_service, async_client, mock_user_create, redis_connection):
        await async_client.post('/auth/register-user', json=mock_user_create.model_dump())

        error = await async_client.post('/auth/register-user', json=mock_user_create.model_dump())

        assert error.status_code == 409
        assert error.json()['detail']


    @pytest.mark.unit
    async def test_verify_user_by_otp_code(self, async_client, mock_verify_email_schema, mock_user_create, redis_connection):
        response = await async_client.post('/auth/register-user', json=mock_user_create.model_dump())
        assert response.status_code == 201

        from src.core import redis_client
        otp_key = f"otp:{mock_user_create.email}"
        otp_code = await redis_client.get(otp_key)

        assert otp_code is not None, "OTP is not in Redis"

        verify_payload = VerifyEmailSchema(
            email = mock_user_create.email,
            otp_code = otp_code
        )

        verify_response = await async_client.post('/auth/verify-code', json=verify_payload.model_dump())

        assert verify_response.status_code == 200
        data = verify_response.json()
        assert data["email"] == mock_user_create.email
        assert data["is_verified"] is True

    @pytest.mark.asyncio
    @patch("src.auth.services.verify_password")
    async def test_login_user(self,mock_verify_password, async_client, mock_user, redis_connection):
        user_fake = mock_user
        user_fake.is_verified = True
        with patch("src.auth.services.UserRepositories.get_by_username", new_callable=AsyncMock) as mock_get:
            mock_get.return_value = user_fake

            mock_verify_password.return_value = True

            login_data = {'username': mock_user.username, 'password': mock_user.password}
            response = await async_client.post("/auth/login-user", data=login_data)

            assert response.status_code == 200
            json_data = response.json()
            assert "access_token" in json_data
            assert json_data["token_type"] == "bearer"