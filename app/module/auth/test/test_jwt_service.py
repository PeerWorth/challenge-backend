import pytest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from fastapi import HTTPException, status
import jwt
from app.module.auth.constant import JWT_ACCESS_TIME_MINUTE, JWT_REFRESH_TIME_MINUTE
from app.module.auth.services.jwt_service import JWTService
import app.module.auth.services.jwt_service as jwt_module


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
        
        with patch("app.module.auth.services.jwt_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = mock_current_time
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            # When
            token = jwt_service.generate_access_token(social_id)
            
            # Then
            decoded = jwt.decode(token, "test_secret_key", algorithms=["HS256"], options={"verify_exp": False})
            assert decoded["sub"] == "user_123456"
            
            expected_exp = mock_current_time + timedelta(minutes=JWT_ACCESS_TIME_MINUTE)
            assert decoded["exp"] == int(expected_exp.timestamp())

    def test_generate_access_token_with_int_id(self, jwt_service: JWTService, mock_current_time):
        # Given
        social_id = 123456
        
        with patch("app.module.auth.services.jwt_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = mock_current_time
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            # When
            token = jwt_service.generate_access_token(social_id)
            
            # Then
            decoded = jwt.decode(token, "test_secret_key", algorithms=["HS256"], options={"verify_exp": False})
            assert decoded["sub"] == "123456"

    def test_generate_refresh_token_with_string_id(self, jwt_service: JWTService, mock_current_time):
        # Given
        social_id = "user_789012"
        
        with patch("app.module.auth.services.jwt_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = mock_current_time
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            # When
            token = jwt_service.generate_refresh_token(social_id)
            
            # Then
            decoded = jwt.decode(token, "test_secret_key", algorithms=["HS256"], options={"verify_exp": False})
            assert decoded["sub"] == "user_789012"
            
            # 만료 시간 검증 (7일)
            expected_exp = mock_current_time + timedelta(minutes=JWT_REFRESH_TIME_MINUTE)
            assert decoded["exp"] == int(expected_exp.timestamp())

    def test_generate_refresh_token_with_int_id(self, jwt_service: JWTService, mock_current_time):
        # Given
        social_id = 789012
        
        with patch("app.module.auth.services.jwt_service.datetime") as mock_datetime:
            mock_datetime.now.return_value = mock_current_time
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            # When
            token = jwt_service.generate_refresh_token(social_id)
            
            # Then
            decoded = jwt.decode(token, "test_secret_key", algorithms=["HS256"], options={"verify_exp": False})
            assert decoded["sub"] == "789012"

    def test_decode_valid_token(self, jwt_service: JWTService):
        # Given
        payload = {
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "sub": "test_user_id",
            "custom_data": "test_value"
        }
        token = jwt.encode(payload, "test_secret_key", algorithm="HS256")
        
        # When
        decoded = jwt_service.decode_token(token)
        
        # Then
        assert decoded["sub"] == "test_user_id"
        assert decoded["custom_data"] == "test_value"

    def test_decode_expired_token(self, jwt_service: JWTService):
        # Given
        payload = {
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),  # 1시간 전 만료
            "sub": "test_user_id"
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
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
            "sub": "test_user_id"
        }
        
        token = jwt.encode(payload, "wrong_secret_key", algorithm="HS256")
        
        # When & Then
        with pytest.raises(HTTPException) as exc_info:
            jwt_service.decode_token(token)
        
        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc_info.value.detail == "유효하지 않은 token입니다."

    def test_different_users_get_different_tokens(self, jwt_service: JWTService):
        # Given
        user1_id = "user_001"
        user2_id = "user_002"
        
        # When
        token1 = jwt_service.generate_access_token(user1_id)
        token2 = jwt_service.generate_access_token(user2_id)
        
        # Then
        assert token1 != token2
        
        decoded1 = jwt.decode(token1, "test_secret_key", algorithms=["HS256"])
        decoded2 = jwt.decode(token2, "test_secret_key", algorithms=["HS256"])
        
        assert decoded1["sub"] == "user_001"
        assert decoded2["sub"] == "user_002"

    def test_access_and_refresh_tokens_are_different(self, jwt_service: JWTService):
        # Given
        social_id = "test_user"
        
        # When
        access_token = jwt_service.generate_access_token(social_id)
        refresh_token = jwt_service.generate_refresh_token(social_id)
        
        # Then
        assert access_token != refresh_token
        
        access_decoded = jwt.decode(access_token, "test_secret_key", algorithms=["HS256"])
        refresh_decoded = jwt.decode(refresh_token, "test_secret_key", algorithms=["HS256"])
        
        assert access_decoded["sub"] == refresh_decoded["sub"]
        assert access_decoded["exp"] != refresh_decoded["exp"]

    def test_token_independence(self, jwt_service: JWTService):
        # Given
        user1 = "user_1"
        user2 = "user_2"
        
        # When - 여러 토큰 생성
        token1_access = jwt_service.generate_access_token(user1)
        token1_refresh = jwt_service.generate_refresh_token(user1)
        token2_access = jwt_service.generate_access_token(user2)
        token2_refresh = jwt_service.generate_refresh_token(user2)
        
        # Then - 모든 토큰이 서로 다름
        tokens = [token1_access, token1_refresh, token2_access, token2_refresh]
        assert len(set(tokens)) == 4 
        
        assert jwt_service.decode_token(token1_access)["sub"] == "user_1"
        assert jwt_service.decode_token(token1_refresh)["sub"] == "user_1"
        assert jwt_service.decode_token(token2_access)["sub"] == "user_2"
        assert jwt_service.decode_token(token2_refresh)["sub"] == "user_2"