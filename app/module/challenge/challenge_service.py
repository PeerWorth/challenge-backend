from sqlalchemy.ext.asyncio import AsyncSession

from app.api.challenge.v1.schema import ChallengeSummary, CompletedChallenge, CurrentChallenge, MissionSummary
from app.database.generic_repository import GenericRepository
from app.model.challenge import Challenge, Mission
from app.model.user_challenge import UserChallenge, UserMission
from app.module.challenge.enums import MissionStatusType


class ChallengeService:
    def __init__(self):
        self.challenge_repository = GenericRepository(Challenge)
        self.mission_repository = GenericRepository(Mission)
        self.user_challenge_repository = GenericRepository(UserChallenge)
        self.user_mission_repository = GenericRepository(UserMission)

    async def get_current_challenge(self, session: AsyncSession, user_id: int) -> CurrentChallenge:
        current_user_challenge = await self._get_current_user_challenge(session, user_id)

        if current_user_challenge:
            return await self._build_current_challenge_data(session, current_user_challenge)
        else:
            return await self._build_initial_challenge_data(session)

    async def get_completed_challenges(self, session: AsyncSession, user_id: int) -> list[CompletedChallenge]:
        # TODO: 실제 완료된 챌린지 조회 로직 구현
        return []

    async def _get_current_user_challenge(self, session: AsyncSession, user_id: int) -> UserChallenge | None:
        return await self.user_challenge_repository.find_one(
            session, user_id=user_id, status=MissionStatusType.IN_PROGRESS
        )

    async def _build_current_challenge_data(
        self, session: AsyncSession, user_challenge: UserChallenge
    ) -> CurrentChallenge:
        current_challenge: Challenge | None = await self.challenge_repository.get_by_id(
            session, user_challenge.challenge_id
        )
        if not current_challenge:
            raise ValueError(f"id {user_challenge.challenge_id}인 challenge 데이터가 없습니다.")

        missions = await self.mission_repository.find_all(session, challenge_id=current_challenge.id)

        mission_summaries = self._build_mission_summaries(missions, user_challenge.mission_step)
        current_mission = self._find_current_mission(mission_summaries)

        challenge_summary = ChallengeSummary(
            id=current_challenge.id,
            title=current_challenge.title,
            status=user_challenge.status,
            current_mission_step=user_challenge.mission_step,
            missions=mission_summaries,
        )

        return CurrentChallenge(challenge=challenge_summary, current_mission=current_mission)

    def _build_mission_summaries(self, missions: list[Mission], current_mission_step: int) -> list[MissionSummary]:
        return [
            MissionSummary(
                id=mission.id,
                title=mission.title,
                step=mission.step,
                reward_amount=mission.reward_amount,
                status=MissionStatusType.get_status(mission.step, current_mission_step),
            )
            for mission in missions
        ]

    def _find_current_mission(self, mission_summaries: list[MissionSummary]) -> MissionSummary:
        current_mission = next((m for m in mission_summaries if m.status == MissionStatusType.IN_PROGRESS), None)

        if current_mission is None and mission_summaries:
            return mission_summaries[0]

        if current_mission is None:
            raise ValueError("현재 진행 중인 미션을 찾을 수 없습니다.")

        return current_mission

    async def _build_initial_challenge_data(self, session: AsyncSession) -> CurrentChallenge:
        initial_challenge = await self.challenge_repository.find_one(session, step=0)

        if not initial_challenge:
            raise ValueError("step 0인 초기 챌린지 데이터가 없습니다.")

        missions: list[Mission] = await self.mission_repository.find_all(session, challenge_id=initial_challenge.id)

        if not missions:
            raise ValueError(f"챌린지 ID {initial_challenge.id}에 대한 미션 데이터가 없습니다.")

        mission_summaries = [
            MissionSummary(
                id=mission.id,
                title=mission.title,
                step=mission.step,
                reward_amount=mission.reward_amount,
                status=MissionStatusType.NOT_STARTED,
            )
            for mission in missions
        ]

        current_mission = mission_summaries[0]

        challenge_summary = ChallengeSummary(
            id=initial_challenge.id,
            title=initial_challenge.title,
            status=MissionStatusType.NOT_STARTED,
            current_mission_step=0,
            missions=mission_summaries,
        )

        return CurrentChallenge(challenge=challenge_summary, current_mission=current_mission)
