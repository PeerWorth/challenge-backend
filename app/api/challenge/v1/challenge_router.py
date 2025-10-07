from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.challenge.v1.schema import (
    ChallengeInfoResponse,
    ChallengeListResponse,
    MissionInfoResponse,
    NewChallengeRequest,
    NewChallengeResponse,
)
from app.database.dependency import get_db_session
from app.module.auth.dependency import verify_access_token
from app.module.auth.schemas import JWTPayload
from app.module.challenge.challenge_service import ChallengeService

challenge_router = APIRouter(prefix="/v1")


@challenge_router.get(
    "/summary",
    summary="유저의 홈 화면 정보를 반환합니다.",
    description="홈 화면 이동 시 처음 표시 될 정보를 반환합니다.",
    status_code=status.HTTP_200_OK,
    response_model=ChallengeInfoResponse,
)
async def get_user_challenge_summary(
    payload: JWTPayload = Depends(verify_access_token),
    session: AsyncSession = Depends(get_db_session),
    challenge_service: ChallengeService = Depends(),
) -> ChallengeInfoResponse:
    current_challenge = await challenge_service.get_current_challenge(session, payload.user_id)
    completed_challenges = await challenge_service.get_completed_challenges(session, payload.user_id)

    return ChallengeInfoResponse(current_challenge=current_challenge, completed_challenges=completed_challenges)


@challenge_router.get(
    "/",
    summary="챌린지 목록을 반환합니다.",
    description="유저가 선택할 수 있는 모든 챌린지 정보를 반환합니다.",
    status_code=status.HTTP_200_OK,
    response_model=ChallengeListResponse,
)
async def get_challenges(
    payload: JWTPayload = Depends(verify_access_token),
    session: AsyncSession = Depends(get_db_session),
    challenge_service: ChallengeService = Depends(),
) -> ChallengeListResponse:
    challenges = await challenge_service.get_all_challenges(session, payload.user_id)
    return ChallengeListResponse(challenges=challenges)


@challenge_router.post(
    "/enrollments",
    summary="챌린지 수행 요청",
    description="다음 수행 할 챌린지를 요청합니다.",
    status_code=status.HTTP_201_CREATED,
    response_model=NewChallengeResponse,
)
async def create_enrollment(
    request_data: NewChallengeRequest,
    payload: JWTPayload = Depends(verify_access_token),
    session: AsyncSession = Depends(get_db_session),
    challenge_service: ChallengeService = Depends(),
) -> NewChallengeResponse:
    challenge_id = request_data.challenge_id

    await challenge_service.start_new_challenge(session, challenge_id, payload.user_id)

    return NewChallengeResponse(status_code=status.HTTP_201_CREATED)


@challenge_router.get(
    "/missions/{mission_id}",
    summary="미션 상세 정보 조회",
    description="특정 미션의 상세 정보와 유저의 미션 수행 상태를 반환합니다.",
    status_code=status.HTTP_200_OK,
    response_model=MissionInfoResponse,
)
async def get_mission_info(
    mission_id: int,
    payload: JWTPayload = Depends(verify_access_token),
    session: AsyncSession = Depends(get_db_session),
    challenge_service: ChallengeService = Depends(),
) -> MissionInfoResponse:
    return await challenge_service.get_mission_info(session, mission_id)
