from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.module.auth.schemas import JWTPayload
from app.module.auth.services.jwt_service import JWTService

security = HTTPBearer()


async def verify_access_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_service: JWTService = Depends(),
) -> JWTPayload:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization 헤더가 필요합니다.")

    token = credentials.credentials
    return jwt_service.decode_token(token)
