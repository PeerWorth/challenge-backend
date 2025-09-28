from sqlalchemy.ext.asyncio import AsyncSession

from app.api.challenge.v1.schema import ChallengeSummary, MissionSummary
from app.module.challenge.challenge_repository import (
    ChallengeRepository,
    MissionRepository,
    UserChallengeRepository,
    UserMissionRepository,
)
from app.module.challenge.constants import FIRST_CHALLENGE_ID
from app.module.challenge.enums import ChallengeStatusType, MissionStatusType


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
        completed_user_challenges = await self.user_challenge_repository.get_completed_challenges(session, user_id)

        result = []
        for user_challenge in completed_user_challenges:
            challenge_summary = await self._build_challenge_summary_from_user_challenge(session, user_challenge)
            if challenge_summary:
                result.append(challenge_summary)

        return result

    async def _build_challenge_summary_from_user_challenge(
        self, session: AsyncSession, user_challenge
    ) -> ChallengeSummary:
        """UserChallenge로부터 ChallengeSummary 구성"""
        # 챌린지와 관련 데이터 조회
        challenge, missions, challenge_missions = await self.challenge_repository.get_with_missions(
            session, user_challenge.challenge_id
        )

        # get_with_missions에서 이미 데이터 존재 여부를 검증하므로 여기서는 불필요

        # 유저의 미션 진행 상태 조회
        user_missions = await self.user_mission_repository.get_missions_by_user_challenge(session, user_challenge.id)
        user_mission_dict = {um.mission_id: um for um in user_missions}

        # 미션 요약 정보 구성
        mission_summaries = []
        total_points = 0
        current_mission = None

        for cm in challenge_missions:
            # 해당 미션 찾기
            mission = next((m for m in missions if m.id == cm.mission_id), None)
            if not mission:
                continue

            # 유저의 미션 상태 확인
            user_mission = user_mission_dict.get(mission.id)
            mission_status = user_mission.status if user_mission else MissionStatusType.NOT_STARTED

            # 현재 진행 중인 미션 스텝 업데이트
            if mission_status == MissionStatusType.IN_PROGRESS:
                current_mission = cm.step

            # 참여 인원 계산
            participant_count = await self.mission_repository.count_participants(session, mission.id)

            mission_summaries.append(
                MissionSummary(
                    id=mission.id,
                    title=mission.title,
                    description=mission.description,
                    step=cm.step,
                    point=mission.point,
                    status=mission_status,
                    participant=participant_count,
                )
            )
            total_points += mission.point

        return ChallengeSummary(
            id=challenge.id,
            title=challenge.title,
            description=challenge.description,
            status=user_challenge.status,
            current_mission_step=current_mission,
            missions=mission_summaries,
            total_points=total_points,
        )

    async def _build_initial_challenge_summary(self, session: AsyncSession) -> ChallengeSummary:
        challenge, missions, challenge_missions = await self.challenge_repository.get_with_missions(
            session, FIRST_CHALLENGE_ID
        )

        mission_summaries: list[MissionSummary] = []
        total_points = 0

        for cm in challenge_missions:
            mission = next((m for m in missions if m.id == cm.mission_id), None)
            if not mission:
                continue

            participant_count = None
            if cm.step == 1:
                participant_count = await self.mission_repository.count_participants(session, mission.id)

            mission_summaries.append(
                MissionSummary(
                    id=mission.id,
                    title=mission.title,
                    description=mission.description,
                    step=cm.step,
                    point=mission.point,
                    status=MissionStatusType.NOT_STARTED,
                    participant=participant_count,
                )
            )
            total_points += mission.point

        return ChallengeSummary(
            id=challenge.id,
            title=challenge.title,
            description=challenge.description,
            status=ChallengeStatusType.NOT_STARTED,
            current_mission_step=mission_summaries[0].step,
            missions=mission_summaries,
            total_points=total_points,
        )
