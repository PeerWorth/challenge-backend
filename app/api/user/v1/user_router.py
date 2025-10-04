from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.user.v1.schema import ProfileRequest, ProfileResponse
from app.database.dependency import get_db_session
from app.module.auth.dependency import verify_access_token
from app.module.auth.schemas import JWTPayload
from app.module.user.user_service import UserService

user_router = APIRouter(prefix="/v1")


@user_router.put(
    "/onboarding",
    summary="회원가입 시 유저 프로필 정보 저장",
    description="JWT 토큰을 통해 인증된 사용자의 프로필 정보를 저장합니다.",
    status_code=status.HTTP_200_OK,
    response_model=ProfileResponse,
)
async def submit_user_profile(
    request_data: ProfileRequest,
    session: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(),
    payload: JWTPayload = Depends(verify_access_token),
):
    await user_service.register_user_profile(
        session=session,
        user_id=payload.user_id,
        request_data=request_data,
    )

    return ProfileResponse(success=True)
