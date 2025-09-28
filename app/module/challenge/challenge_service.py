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
from app.module.challenge.serializers import ChallengeSerializer


class ChallengeService:
    def __init__(self):
        self.challenge_repository = ChallengeRepository()
        self.mission_repository = MissionRepository()
        self.user_challenge_repository = UserChallengeRepository()
        self.user_mission_repository = UserMissionRepository()

    async def get_current_challenge(self, session: AsyncSession, user_id: int) -> tuple[ChallengeSummary, bool]:
        current_user_challenge = await self.user_challenge_repository.get_current_challenge(session, user_id)

        if current_user_challenge:
            return await self._build_challenge_summary_from_user_challenge(session, current_user_challenge), False
        else:
            return await self._build_initial_challenge_summary(session), True

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
        all_user_missions = await self._get_user_missions_batch(session, user_challenge_ids)

        result = []
        for user_challenge in completed_user_challenges:
            challenge_data = challenges_infos.get(user_challenge.challenge_id)
            if not challenge_data:
                continue

            challenge, missions, challenge_missions = challenge_data
            user_missions = all_user_missions.get(user_challenge.id, [])

            challenge_summary = ChallengeSerializer.to_challenge_summary_for_completed(
                challenge, missions, challenge_missions, user_challenge, user_missions
            )
            result.append(challenge_summary)

        return result

    async def _build_challenge_summary_from_user_challenge(
        self, session: AsyncSession, user_challenge: UserChallenge
    ) -> ChallengeSummary:
        challenge, missions, challenge_missions = await self.challenge_repository.get_with_missions(
            session, user_challenge.challenge_id
        )

        user_missions = await self.user_mission_repository.get_missions_by_user_challenge(session, user_challenge.id)

        participant_counts = await self._get_participant_counts_for_in_progress_missions(session, user_missions)

        return ChallengeSerializer.to_challenge_summary_for_current(
            challenge, missions, challenge_missions, user_challenge, user_missions, participant_counts
        )

    async def _build_initial_challenge_summary(self, session: AsyncSession) -> ChallengeSummary:
        """초기 챌린지 요약 정보 구성 (신규 사용자)"""
        challenge, missions, challenge_missions = await self.challenge_repository.get_with_missions(
            session, FIRST_CHALLENGE_ID
        )

        # 첫 번째 미션의 참여자 수만 계산
        first_mission_participant_count = None
        if challenge_missions:
            first_challenge_mission = next((cm for cm in challenge_missions if cm.step == 1), None)
            if first_challenge_mission:
                first_mission = next((m for m in missions if m.id == first_challenge_mission.mission_id), None)
                if first_mission:
                    first_mission_participant_count = await self.mission_repository.count_participants(
                        session, first_mission.id
                    )

        return ChallengeSerializer.to_initial_challenge_summary(
            challenge, missions, challenge_missions, first_mission_participant_count
        )

    async def _get_user_missions_batch(
        self, session: AsyncSession, user_challenge_ids: list[int]
    ) -> dict[int, list[UserMission]]:
        """여러 유저 챌린지의 미션 데이터를 배치로 조회"""
        if not user_challenge_ids:
            return {}

        from sqlalchemy import select

        stmt = select(UserMission).where(UserMission.user_challenge_id.in_(user_challenge_ids))  # type: ignore
        result = await session.execute(stmt)
        all_user_missions = result.scalars().all()

        grouped: dict = {}
        for um in all_user_missions:
            if um.user_challenge_id not in grouped:
                grouped[um.user_challenge_id] = []
            grouped[um.user_challenge_id].append(um)

        return grouped

    async def _get_participant_counts_for_in_progress_missions(
        self, session: AsyncSession, user_missions: list[UserMission]
    ) -> dict[int, int]:
        """진행 중인 미션들의 참여자 수 배치 조회"""
        in_progress_mission_ids = [um.mission_id for um in user_missions if um.status == MissionStatusType.IN_PROGRESS]

        if not in_progress_mission_ids:
            return {}

        participant_counts = {}
        for mission_id in in_progress_mission_ids:
            count = await self.mission_repository.count_participants(session, mission_id)
            participant_counts[mission_id] = count

        return participant_counts
