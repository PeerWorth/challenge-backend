from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.auth.v1.schema import OAuthRequest, OAuthResponse
from app.database.dependency import get_db_session
from app.module.auth.services.jwt_service import JWTService
from app.module.auth.services.oauth_service import AuthService

auth_router = APIRouter(prefix="/v1")


@auth_router.post(
    "/kakao",
    summary="카카오 id token을 확인 후 jwt 토큰을 반환합니다.",
    description="카카오 id 토큰으로 유저 확인 후 jwt를 반환합니다.",
    status_code=status.HTTP_201_CREATED,
    response_model=OAuthResponse,
)
async def sign_up_login(
    request_data: OAuthRequest,
    session: AsyncSession = Depends(get_db_session),
    auth_service: AuthService = Depends(),
    jwt_service: JWTService = Depends(),
) -> OAuthResponse:
    social_id = await auth_service.verify_kakao_token(request_data.id_token)
    user = await auth_service.find_user_by_social_id(session, social_id)

    if not user:
        user = await auth_service.create_user_with_social_id(session, social_id)

    access_token = jwt_service.generate_access_token(social_id, user.id)

    return OAuthResponse(
        access_token=access_token, is_new_user=not bool(user.nickname and user.birth_year and user.gender)
    )
