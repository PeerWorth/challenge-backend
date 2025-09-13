from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.module.auth.services.jwt_service import JWTService

security = HTTPBearer()


async def get_current_user_social_id(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    jwt_service: JWTService = Depends(),
) -> str:
    if not credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authorization 헤더가 필요합니다.")

    token = credentials.credentials
    payload = jwt_service.decode_token(token)
    social_id = payload.get("sub")

    if not social_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="토큰에 사용자 정보가 없습니다.")

    return social_id
