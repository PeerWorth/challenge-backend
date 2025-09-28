from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import jwt
import pytest
from fastapi import HTTPException, status

import app.module.auth.services.jwt_service as jwt_module
from app.module.auth.constant import JWT_ACCESS_TIME_MINUTE
from app.module.auth.services.jwt_service import JWTService


class TestJWTService:
    @pytest.fixture
    def jwt_service(self) -> JWTService:
        with patch.dict("os.environ", {"JWT_SECRET": "test_secret_key", "JWT_ALGORITHM": "HS256"}):
            jwt_module.JWT_SECRET_KEY = "test_secret_key"
            jwt_module.JWT_ALGORITHM = "HS256"

            return JWTService()

    @pytest.fixture
    def mock_current_time(self) -> datetime:
        """현재 시간 고정"""
        return datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

    def test_generate_access_token_with_string_id(self, jwt_service: JWTService, mock_current_time: datetime):
        # Given
        social_id = "user_123456"
        user_id = 1

        with patch("app.module.auth.services.jwt_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = mock_current_time
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            # When
            token = jwt_service.generate_access_token(social_id, user_id)

            # Then
            decoded = jwt.decode(token, "test_secret_key", algorithms=["HS256"], options={"verify_exp": False})
            assert decoded["social_id"] == "user_123456"
            assert decoded["user_id"] == "1"

            expected_exp = mock_current_time + timedelta(minutes=JWT_ACCESS_TIME_MINUTE)
            assert decoded["exp"] == int(expected_exp.timestamp())

    def test_generate_access_token_with_int_id(self, jwt_service: JWTService, mock_current_time):
        # Given
        social_id = "123456"
        user_id = 2

        with patch("app.module.auth.services.jwt_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = mock_current_time
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)

            # When
            token = jwt_service.generate_access_token(social_id, user_id)

            # Then
            decoded = jwt.decode(token, "test_secret_key", algorithms=["HS256"], options={"verify_exp": False})
            assert decoded["social_id"] == "123456"
            assert decoded["user_id"] == "2"

    def test_decode_valid_token(self, jwt_service: JWTService):
        # Given
        payload = {
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
            "social_id": "test_social_id",
            "user_id": "123",
        }
        token = jwt.encode(payload, "test_secret_key", algorithm="HS256")

        # When
        decoded = jwt_service.decode_token(token)

        # Then
        assert decoded.social_id == "test_social_id"
        assert decoded.user_id == "123"

    def test_decode_expired_token(self, jwt_service: JWTService):
        # Given
        payload = {
            "exp": int((datetime.now(timezone.utc) - timedelta(hours=1)).timestamp()),
            "social_id": "test_social_id",
            "user_id": "123",
        }
        token = jwt.encode(payload, "test_secret_key", algorithm="HS256")

        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            jwt_service.decode_token(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "token이 만료되었습니다."

    def test_decode_invalid_token(self, jwt_service: JWTService):
        # Given
        invalid_token = "invalid_token_blabla"

        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            jwt_service.decode_token(invalid_token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "유효하지 않은 token입니다."

    def test_decode_token_with_wrong_secret(self, jwt_service: JWTService):
        # Given
        payload = {
            "exp": int((datetime.now(timezone.utc) + timedelta(hours=1)).timestamp()),
            "social_id": "test_social_id",
            "user_id": "123",
        }
        token = jwt.encode(payload, "wrong_secret_key", algorithm="HS256")

        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            jwt_service.decode_token(token)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "유효하지 않은 token입니다."

    def test_different_users_get_different_tokens(self, jwt_service: JWTService):
        # Given
        social_id1 = "user_001"
        social_id2 = "user_002"
        user_id1 = 1
        user_id2 = 2

        # When
        token1 = jwt_service.generate_access_token(social_id1, user_id1)
        token2 = jwt_service.generate_access_token(social_id2, user_id2)

        # Then
        assert token1 != token2

        decoded1 = jwt.decode(token1, "test_secret_key", algorithms=["HS256"])
        decoded2 = jwt.decode(token2, "test_secret_key", algorithms=["HS256"])

        assert decoded1["social_id"] == "user_001"
        assert decoded2["social_id"] == "user_002"
        assert decoded1["user_id"] == "1"
        assert decoded2["user_id"] == "2"
