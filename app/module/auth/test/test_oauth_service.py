import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import status
from app.module.auth.services.oauth_service import AuthService
from app.module.auth.error import InvalidKakaoTokenException, MissingSocialIDException


class TestAuthService:
    @pytest.fixture
    def auth_service(self):
        return AuthService()

    @pytest.fixture
    def mock_kakao_response_success(self):
        return {
            "sub": "test_social_id_123456",
            "exp": 1234567890,
            "iat": 1234567800,
        }

    @pytest.fixture
    def mock_kakao_response_no_sub(self):
        return {
            "exp": 1234567890,
            "iat": 1234567800,
        }

    @pytest.mark.asyncio
    async def test_verify_kakao_token_success(self, auth_service: AuthService, mock_kakao_response_success):
        # Given
        test_token = "test_id_token_12345"
        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.json.return_value = mock_kakao_response_success

        # When
        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            result = await auth_service.verify_kakao_token(test_token)

        # Then
        assert result == "test_social_id_123456"
        mock_client_instance.post.assert_called_once_with(
            "https://kauth.kakao.com/oauth/tokeninfo",
            data={"id_token": test_token},
            headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
        )

    @pytest.mark.asyncio
    async def test_verify_kakao_token_invalid_token(self, auth_service: AuthService):
        # Given
        test_token = "invalid_token"
        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_401_UNAUTHORIZED

        # When & Then
        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            with pytest.raises(InvalidKakaoTokenException) as exc_info:
                await auth_service.verify_kakao_token(test_token)

            assert "카카오 토큰 검증 실패: 401" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_verify_kakao_token_no_social_id(self, auth_service: AuthService, mock_kakao_response_no_sub):
        # Given
        test_token = "test_token_no_sub"
        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_200_OK
        mock_response.json.return_value = mock_kakao_response_no_sub

        # When & Then
        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            with pytest.raises(MissingSocialIDException):
                await auth_service.verify_kakao_token(test_token)

    @pytest.mark.asyncio
    async def test_verify_kakao_token_server_error(self, auth_service: AuthService):
        # Given
        test_token = "test_token"
        mock_response = MagicMock()
        mock_response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

        # When & Then
        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            mock_client_instance.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_client_instance

            with pytest.raises(InvalidKakaoTokenException) as exc_info:
                await auth_service.verify_kakao_token(test_token)

            assert "카카오 토큰 검증 실패: 500" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_verify_kakao_token_different_tokens(self, auth_service: AuthService, mock_kakao_response_success):
        # Given
        token1 = "token_1"
        token2 = "token_2"
        
        response1 = {**mock_kakao_response_success, "sub": "user_1"}
        response2 = {**mock_kakao_response_success, "sub": "user_2"}
        
        mock_response1 = MagicMock()
        mock_response1.status_code = status.HTTP_200_OK
        mock_response1.json.return_value = response1
        
        mock_response2 = MagicMock()
        mock_response2.status_code = status.HTTP_200_OK
        mock_response2.json.return_value = response2

        # When & Then
        with patch("httpx.AsyncClient") as mock_client:
            mock_client_instance = AsyncMock()
            
            # 첫 번째 토큰 검증
            mock_client_instance.post.return_value = mock_response1
            mock_client.return_value.__aenter__.return_value = mock_client_instance
            result1 = await auth_service.verify_kakao_token(token1)
            
            # 두 번째 토큰 검증
            mock_client_instance.post.return_value = mock_response2
            result2 = await auth_service.verify_kakao_token(token2)

        # Then
        assert result1 == "user_1"
        assert result2 == "user_2"
        assert result1 != result2