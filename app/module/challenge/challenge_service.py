from sqlalchemy.ext.asyncio import AsyncSession

from app.api.challenge.v1.schema import ChallengeSummary
from app.model.challenge import Challenge, ChallengeMission, Mission
from app.model.user_challenge import UserChallenge, UserMission
from app.module.challenge.challenge_repository import (
    ChallengeRepository,
    MissionRepository,
    UserChallengeRepository,
    UserMissionRepository,
)
from app.module.challenge.constants import FIRST_CHALLENGE_ID
from app.module.challenge.enums import MissionStatusType
from app.module.challenge.errors import ChallengeNotFoundError
from app.module.challenge.serializers import ChallengeSerializer


class ChallengeService:
    def __init__(self):
        self.challenge_repository = ChallengeRepository()
        self.mission_repository = MissionRepository()
        self.user_challenge_repository = UserChallengeRepository()
        self.user_mission_repository = UserMissionRepository()

    async def get_current_challenge(self, session: AsyncSession, user_id: int) -> ChallengeSummary:
        current_user_challenge: UserChallenge | None = await self.user_challenge_repository.get_current_challenge(
            session, user_id
        )

        if not current_user_challenge:
            current_user_challenge = await self._create_initial_user_challenge(session, user_id)

        challenge_id = current_user_challenge.challenge_id
        challenge = await self.challenge_repository.get_by_id(session, challenge_id)  # type: ignore
        if not challenge:
            raise ChallengeNotFoundError(challenge_id)

        missions: list[Mission] = await self.challenge_repository.get_missions_by_challenge(session, challenge_id)
        challenge_missions: list[ChallengeMission] = await self.challenge_repository.get_challenge_missions(
            session, challenge_id
        )
        user_missions: list[UserMission] = await self.user_mission_repository.get_missions_by_user_challenge(
            session, current_user_challenge.id
        )
        participant_counts = await self._get_participant_counts_for_in_progress_missions(session, user_missions)

        return ChallengeSerializer.to_challenge_summary(
            challenge, missions, challenge_missions, current_user_challenge, user_missions, participant_counts
        )

    async def get_completed_challenges(self, session: AsyncSession, user_id: int) -> list[ChallengeSummary]:
        completed_user_challenges: list[UserChallenge] = await self.user_challenge_repository.get_completed_challenges(
            session, user_id
        )

        if not completed_user_challenges:
            return []

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
            challenge_data = challenges_infos.get(user_challenge.challenge_id)
            if not challenge_data:
                continue

            challenge, missions, challenge_missions = challenge_data
            user_missions = all_user_missions.get(user_challenge.id, [])

            challenge_summary = ChallengeSerializer.to_challenge_summary(
                challenge, missions, challenge_missions, user_challenge, user_missions, None
            )
            result.append(challenge_summary)

        return result

    async def _get_participant_counts_for_in_progress_missions(
        self, session: AsyncSession, user_missions: list[UserMission]
    ) -> dict[int, int]:
        in_progress_missions = [um for um in user_missions if um.status == MissionStatusType.IN_PROGRESS]

        if not in_progress_missions:
            return {}

        participant_counts = {}
        for user_mission in in_progress_missions:
            count = await self.mission_repository.count_participants(session, user_mission.mission_id)
            participant_counts[user_mission.mission_id] = count

        return participant_counts

    async def _create_initial_user_challenge(self, session: AsyncSession, user_id: int) -> UserChallenge:
        challenge_missions = await self.challenge_repository.get_challenge_missions(session, FIRST_CHALLENGE_ID)

        if not challenge_missions:
            raise ChallengeNotFoundError(FIRST_CHALLENGE_ID)

        first_challenge_mission = next((cm for cm in challenge_missions if cm.step == 1), None)
        if not first_challenge_mission:
            raise ChallengeNotFoundError(FIRST_CHALLENGE_ID)

        return await self.user_challenge_repository.create_with_first_mission(
            session, user_id, FIRST_CHALLENGE_ID, first_challenge_mission.mission_id
        )
