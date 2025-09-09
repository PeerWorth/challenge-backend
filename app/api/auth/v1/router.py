from fastapi import APIRouter, Depends, status
from app.module.auth.services.oauth_service import AuthService
from app.module.auth.services.jwt_service import JWTService
from app.api.auth.v1.schema import OAuthRequest, OAuthResponse

auth_router = APIRouter(prefix="/v1")



@auth_router.post(
    "/kakao",
    summary="카카오 id token을 확인 후 jwt 토큰을 반환합니다.",
    description="카카오 id 토큰으로 유저 확인 후 jwt를 반환합니다.",
    status_code=status.HTTP_201_CREATED,
    response_model=OAuthResponse
)
async def submit_user_email(
    request_data: OAuthRequest,
    auth_service: AuthService = Depends(),
    jwt_service: JWTService = Depends(),
) -> OAuthResponse:
    social_id = await auth_service.verify_kakao_token(request_data.id_token)

    access_token = jwt_service.generate_access_token(social_id)
    refresh_token = jwt_service.generate_refresh_token(social_id)

    return OAuthResponse(access_token=access_token, refresh_token=refresh_token)

