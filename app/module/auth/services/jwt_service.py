from datetime import datetime, timedelta, timezone
from os import getenv

import jwt
from dotenv import load_dotenv
from fastapi import HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError

from app.module.auth.constant import JWT_ACCESS_TIME_MINUTE, JWT_REFRESH_TIME_MINUTE
from app.module.auth.error import NoJWTSecretException

load_dotenv()

_jwt_secret_key = getenv("JWT_SECRET")
_jwt_algorithm = getenv("JWT_ALGORITHM")

if not _jwt_secret_key or not _jwt_algorithm:
    raise NoJWTSecretException()

JWT_SECRET_KEY: str = _jwt_secret_key
JWT_ALGORITHM: str = _jwt_algorithm


class JWTService:
    def generate_access_token(self, social_id: str | int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TIME_MINUTE)
        payload = {"exp": expire, "sub": str(social_id)}
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    def generate_refresh_token(self, social_id: str | int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_REFRESH_TIME_MINUTE)
        payload = {"exp": expire, "sub": str(social_id)}
        return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    def decode_token(self, token: str) -> dict:
        try:
            return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token이 만료되었습니다.")
        except InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 token입니다.")
