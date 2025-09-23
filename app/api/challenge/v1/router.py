from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.challenge.v1.schema import HomePageResponse
from app.database.dependency import get_db_session
from app.module.auth.dependency import verify_access_token
from app.module.auth.schemas import JWTPayload
from app.module.challenge.challenge_service import ChallengeService

challenge_router = APIRouter(prefix="/v1")


@challenge_router.get(
    "/",
    summary="유저의 홈 화면 정보를 반환합니다.",
    description="홈 화면 이동 시 처음 표시 될 정보를 반환합니다.",
    status_code=status.HTTP_200_OK,
    response_model=HomePageResponse,
)
async def get_home_page_info(
    payload: JWTPayload = Depends(verify_access_token),
    session: AsyncSession = Depends(get_db_session),
    challenge_service: ChallengeService = Depends(),
) -> HomePageResponse:
    # payload.sub (social_id) 또는 payload.user_id_int 사용 가능

    return  # type: ignore
