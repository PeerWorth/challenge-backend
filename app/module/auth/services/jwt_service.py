from datetime import datetime, timedelta, timezone
from os import getenv

from dotenv import load_dotenv
from fastapi import HTTPException, status
from jwt import ExpiredSignatureError, InvalidTokenError, decode, encode
from pydantic import ValidationError

from app.module.auth.constant import JWT_ACCESS_TIME_MINUTE
from app.module.auth.error import NoJWTSecretException
from app.module.auth.schemas import JWTPayload

load_dotenv()

_jwt_secret_key = getenv("JWT_SECRET")
_jwt_algorithm = getenv("JWT_ALGORITHM")

if not _jwt_secret_key or not _jwt_algorithm:
    raise NoJWTSecretException()

JWT_SECRET_KEY: str = _jwt_secret_key
JWT_ALGORITHM: str = _jwt_algorithm


class JWTService:
    def generate_access_token(self, social_id: str, user_id: int) -> str:
        expire = datetime.now(timezone.utc) + timedelta(minutes=JWT_ACCESS_TIME_MINUTE)
        payload = {"exp": int(expire.timestamp()), "social_id": social_id, "user_id": str(user_id)}
        return encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

    def decode_token(self, token: str) -> JWTPayload:
        try:
            raw_payload = decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
            return JWTPayload(**raw_payload)
        except ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token이 만료되었습니다.")
        except InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="유효하지 않은 token입니다.")
        except ValidationError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token 형식이 올바르지 않습니다.")
