from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.user.v1.schema import ProfileRequest, ProfileResponse
from app.database.dependency import get_db_session
from app.module.auth.dependency import verify_access_token
from app.module.user.user_service import UserService

user_router = APIRouter(prefix="/v1")


@user_router.post(
    "/profile",
    summary="회원가입 시 유저 프로필 정보 저장",
    description="JWT 토큰을 통해 인증된 사용자의 프로필 정보를 저장합니다.",
    status_code=status.HTTP_201_CREATED,
    response_model=ProfileResponse,
)
async def submit_user_profile(
    request_data: ProfileRequest,
    session: AsyncSession = Depends(get_db_session),
    user_service: UserService = Depends(),
    current_user_social_id: str = Depends(verify_access_token),
):
    await user_service.update_user_profile(
        session=session,
        social_id=current_user_social_id,
        nickname=request_data.nickname,
        birthday=request_data.birthday,
        gender=request_data.gender,
        phone=request_data.phone,
    )

    return ProfileResponse(success=True)
