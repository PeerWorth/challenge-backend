from sqlalchemy.ext.asyncio import AsyncSession

from app.api.challenge.v1.schema import (
    ChallengeDetail,
    ChallengeSummary,
    MissionInfoResponse,
    MissionPost,
    MissionPostsResponse,
)
from app.model.challenge import Challenge, ChallengeMission, Mission
from app.model.user_challenge import UserChallenge, UserMission
from app.module.challenge.challenge_repository import (
    ChallengeRepository,
    MissionRepository,
    UserChallengeRepository,
    UserMissionRepository,
)
from app.module.challenge.constants import FIRST_MISSION_STEP
from app.module.challenge.enums import ChallengeStatusType, MissionStatusType
from app.module.challenge.errors import (
    ChallengeAlreadyCompletedError,
    ChallengeNotFoundError,
    MissionDataIncompleteError,
    UserChallengeAlreadyInProgressError,
)
from app.module.challenge.schema import CurrentChallengeData
from app.module.challenge.serializers import ChallengeSerializer
from app.module.post.post_service import PostService


class ChallengeService:
    def __init__(self):
        self.challenge_repository = ChallengeRepository()
        self.mission_repository = MissionRepository()
        self.user_challenge_repository = UserChallengeRepository()
        self.user_mission_repository = UserMissionRepository()

        self.post_service = PostService()

    async def get_current_challenge_context(self, session: AsyncSession, user_id: int) -> CurrentChallengeData | None:
        current_user_challenge: UserChallenge | None = await self.user_challenge_repository.get_current_challenge(
            session, user_id
        )

        if not current_user_challenge:
            return None

        challenge_id = current_user_challenge.challenge_id
        challenge = await self.challenge_repository.get_by_id(session, challenge_id)
        if not challenge:
            raise ChallengeNotFoundError(challenge_id)

        user_missions: list[UserMission] = await self.user_mission_repository.get_missions_by_user_challenge(
            session, current_user_challenge.id
        )

        in_progress_mission = next((um for um in user_missions if um.status == MissionStatusType.IN_PROGRESS), None)
        headcount = None
        if in_progress_mission:
            headcount = await self.mission_repository.count_participants(session, in_progress_mission.mission_id)

        missions: list[Mission] = await self.challenge_repository.get_missions_by_challenge(session, challenge_id)
        challenge_missions: list[ChallengeMission] = await self.challenge_repository.get_challenge_missions(
            session, challenge_id
        )

        return CurrentChallengeData(
            challenge=challenge,
            missions=missions,
            challenge_missions=challenge_missions,
            user_challenge=current_user_challenge,
            user_missions=user_missions,
            headcount=headcount,
        )

    async def get_completed_challenges(self, session: AsyncSession, user_id: int) -> list[ChallengeSummary] | None:
        completed_user_challenges: list[UserChallenge] = await self.user_challenge_repository.get_completed_challenges(
            session, user_id
        )

        if not completed_user_challenges:
            return None

        challenge_ids = [uc.challenge_id for uc in completed_user_challenges]
        challenges_infos: dict[int, tuple[Challenge, list[Mission], list[ChallengeMission]]] = (
            await self.challenge_repository.get_multiple_with_missions(session, challenge_ids)
        )

        user_challenge_ids = [uc.id for uc in completed_user_challenges]
        all_user_missions = await self.user_mission_repository.get_missions_by_user_challenges_batch(
            session, user_challenge_ids
        )

        result = []
        for user_challenge in completed_user_challenges:
            challenge_data = challenges_infos.get(user_challenge.challenge_id, None)
            if not challenge_data:
                raise ValueError(f"챌린지 id {user_challenge.challenge_id}의 데이터가 존재하지 않습니다.")

            challenge, missions, challenge_missions = challenge_data
            user_missions = all_user_missions.get(user_challenge.id, None)
            if not user_missions:
                raise ValueError(f"user_challenge id {user_challenge.id}의 데이터가 존재하지 않습니다.")

            challenge_summary = ChallengeSerializer.to_challenge_summary(
                challenge, missions, challenge_missions, user_challenge, user_missions
            )
            result.append(challenge_summary)

        return result

    async def start_new_challenge(self, session: AsyncSession, challenge_id: int, user_id: int) -> None:
        current_user_challenge = await self.user_challenge_repository.get_current_challenge(session, user_id)
        if current_user_challenge:
            raise UserChallengeAlreadyInProgressError(user_id)

        challenge = await self.challenge_repository.get_by_id(session, challenge_id)
        if not challenge:
            raise ChallengeNotFoundError(challenge_id)

        completed_user_challenge = await self.user_challenge_repository.find_one(
            session, user_id=user_id, challenge_id=challenge_id, status=ChallengeStatusType.COMPLETED
        )
        if completed_user_challenge:
            raise ChallengeAlreadyCompletedError(user_id, challenge_id)

        challenge_missions = await self.challenge_repository.get_challenge_missions(session, challenge_id)
        if not challenge_missions:
            raise MissionDataIncompleteError(challenge_id)

        await self.user_challenge_repository.create_with_missions(
            session, user_id, challenge_id, challenge_missions, FIRST_MISSION_STEP
        )

    async def get_all_challenges(self, session: AsyncSession, user_id: int) -> list[ChallengeDetail]:
        challenges: list[Challenge] = await self.challenge_repository.find_all(session)

        if not challenges:
            return []

        challenge_ids = [c.id for c in challenges]
        challenges_with_missions = await self.challenge_repository.get_multiple_with_missions(session, challenge_ids)

        user_challenges: list[UserChallenge] = await self.user_challenge_repository.find_all(session, user_id=user_id)
        user_challenge_status_map = {uc.challenge_id: uc.status for uc in user_challenges}

        result = []
        for challenge in challenges:
            challenge_data = challenges_with_missions.get(challenge.id)
            if not challenge_data:
                continue

            _, missions, _ = challenge_data
            total_points = sum(mission.point for mission in missions)

            status = user_challenge_status_map.get(challenge.id, ChallengeStatusType.NOT_STARTED)

            result.append(
                ChallengeDetail(
                    id=challenge.id,
                    title=challenge.title,
                    description=challenge.description,
                    total_points=total_points,
                    status=status,
                )
            )

        return result

    async def get_mission_info(self, session: AsyncSession, mission_id: int, limit: int) -> MissionInfoResponse:
        mission: Mission | None = await self.mission_repository.get_by_id(session, mission_id)  # type: ignore
        if not mission:
            raise ValueError(f"미션 id {mission_id}가 존재하지 않습니다.")

        headcount = await self.mission_repository.count_participants(session, mission_id)

        mission_posts: list[MissionPost] = await self.post_service.get_mission_posts_paginated(
            session, mission_id, limit
        )

        next_cursor = min(post.post_id for post in mission_posts) if mission_posts else None

        return MissionInfoResponse(
            id=mission.id,
            title=mission.title,
            description=mission.description,
            type=mission.type,
            point=mission.point,
            headcount=headcount,
            posts=mission_posts,
            next_cursor=next_cursor,
        )

    async def get_mission_posts(
        self, session: AsyncSession, mission_id: int, limit: int, cursor: int | None
    ) -> MissionPostsResponse:
        mission_posts = await self.post_service.get_mission_posts_paginated(session, mission_id, limit, cursor)

        next_cursor = min(post.post_id for post in mission_posts) if mission_posts else None

        return MissionPostsResponse(
            posts=mission_posts,
            next_cursor=next_cursor,
        )
