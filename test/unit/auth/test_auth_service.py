from unittest import mock
from unittest.mock import patch, AsyncMock

import pytest

from src.auth import LoginUserOutput, PasswordIsIncorrect
from src.tokens import TokenType
from src.users import UserWithUsernameNotFound, UserNotVerifyEmail


class TestAuthService:

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('src.auth.services.hash_password')
    async def test_register_user(self,mock_hash_password, mock_user_service, mock_otp_service, auth_service, mock_user, mock_user_create):
        mock_user_service.create_user.return_value = mock_user
        mock_otp_service.send_and_save_otp.return_value = None
        mock_hash_password.return_value = 'hash_password'

        await auth_service.register_user(mock_user_create)

        mock_user_service.create_user.assert_called_once()

        called_user = mock_user_service.create_user.call_args[0][0]
        assert called_user.password == 'hash_password'
        assert called_user.password != mock_user_create.password

        mock_otp_service.send_and_save_otp.assert_called_once_with(email=mock_user_create.email)

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('src.auth.services.verify_password')
    async def test_login_user_successful(
            self,
            mock_verify_password,
            mock_user_repository,
            mock_token_service,
            auth_service,
            mock_login_form_data,
            mock_user,
    ):
        mock_user_repository.get_by_username.return_value = mock_user
        mock_user.is_verified = True
        mock_verify_password.return_value = True

        auth_service._generate_and_save_tokens = AsyncMock(
            return_value=LoginUserOutput(access_token='token', refresh_token="token", token_type='bearer')
        )

        result = await auth_service.login_user(mock_login_form_data)

        mock_user_repository.get_by_username.assert_called_once_with(mock_login_form_data.username)
        mock_verify_password.assert_called_once()
        auth_service._generate_and_save_tokens.assert_called_once_with(mock_user)
        assert isinstance(result, LoginUserOutput)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_login_user_user_not_found(self, mock_user_repository, auth_service, mock_login_form_data):
        mock_user_repository.get_by_username.return_value = None

        with pytest.raises(UserWithUsernameNotFound):
            await auth_service.login_user(mock_login_form_data)\

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_login_user_user_not_verified(self, mock_user_repository, auth_service, mock_login_form_data,
                                                mock_user):
        mock_user_repository.get_by_username.return_value = mock_user

        with pytest.raises(UserNotVerifyEmail):
            await auth_service.login_user(mock_login_form_data)

    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('src.auth.services.verify_password')
    async def test_login_user_wrong_password(self, mock_verify_password, mock_user_repository, auth_service, mock_login_form_data, mock_user):
        mock_user_repository.get_by_username.return_value = mock_user
        mock_verify_password.return_value = False
        mock_user.is_verified = True

        with pytest.raises(PasswordIsIncorrect):
            await auth_service.login_user(mock_login_form_data)

    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_verify_user_by_otp(
            self,
            mock_verify_email_schema,
            auth_service,
            mock_user,
            mock_otp_service,
            mock_user_repository
    ):
        mock_user_repository.get_by_email.return_value = mock_user

        mock_otp_service.verify_otp.return_value = True

        verified = mock_user.model_copy(update={'is_verified': True})
        mock_user_repository.set_verified.return_value = verified
        result = await auth_service.verify_user_by_otp_code(mock_verify_email_schema)


        mock_user_repository.get_by_email.assert_called_once_with(mock_verify_email_schema.email)
        assert result.is_verified


    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_refresh_token_success(
        self,
        mock_token_service,
        mock_user_service,
        auth_service,
        mock_user
    ):
        fake_refresh_token = "fake_refresh_token"
        fake_user_id = 123
        fake_payload = {"sub": str(fake_user_id)}

        mock_token_service.decode_token_with_token_type_checking = mock.MagicMock(return_value=fake_payload)

        mock_token_service.verify_refresh_token = AsyncMock()
        mock_token_service.delete_refresh_token = AsyncMock()
        mock_user_service.get_user_by_id.return_value=mock_user

        auth_service._generate_and_save_tokens = AsyncMock(return_value=LoginUserOutput(
            access_token='new_access',
            refresh_token='new_refresh',
            token_type='bearer'
        ))

        result = await auth_service.refresh_token(fake_refresh_token)

        mock_token_service.decode_token_with_token_type_checking.assert_called_once_with(fake_refresh_token, TokenType.refresh)
        mock_token_service.verify_refresh_token.assert_awaited_once_with(fake_user_id, fake_refresh_token)
        mock_token_service.delete_refresh_token.assert_awaited_once_with(fake_user_id)
        mock_user_service.get_user_by_id.assert_awaited_once_with(fake_user_id)
        auth_service._generate_and_save_tokens.assert_awaited_once_with(mock_user)

        assert result.access_token == 'new_access'
        assert result.refresh_token == 'new_refresh'
        assert result.token_type == 'bearer'
