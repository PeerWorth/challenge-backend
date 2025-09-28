from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.generic_repository import GenericRepository
from app.model.challenge import Challenge, ChallengeMission, Mission
from app.model.user_challenge import UserChallenge, UserMission
from app.module.challenge.enums import ChallengeStatusType, MissionStatusType


class ChallengeRepository(GenericRepository):
    def __init__(self):
        super().__init__(Challenge)

    async def get_with_missions(
        self, session: AsyncSession, challenge_id: int
    ) -> tuple[Challenge, list[Mission], list[ChallengeMission]]:
        challenge = await self.get_by_id(session, challenge_id)  # type: ignore
        if not challenge:
            raise ValueError(f"챌린지 {challenge_id}가 존재하지 않습니다.")

        # 미션들 조회
        missions_stmt = (
            select(Mission).join(ChallengeMission).where(ChallengeMission.challenge_id == challenge_id)
        )  # type: ignore
        missions_result = await session.execute(missions_stmt)
        missions = list(missions_result.scalars().all())

        # 챌린지-미션 관계 정보 조회
        cm_stmt = (
            select(ChallengeMission)
            .where(ChallengeMission.challenge_id == challenge_id)  # type: ignore
            .order_by(ChallengeMission.step)  # type: ignore
        )
        cm_result = await session.execute(cm_stmt)
        challenge_missions = list(cm_result.scalars().all())

        if not missions or not challenge_missions:
            raise ValueError(f"챌린지 {challenge_id}와 연계된 미션 데이터를 가져오는데 실패하였습니다.")

        return challenge, missions, challenge_missions


class MissionRepository(GenericRepository):
    def __init__(self):
        super().__init__(Mission)

    async def count_participants(
        self, session: AsyncSession, mission_id: int, statuses: list[str] | None = None
    ) -> int:
        """미션 참여 인원 수 계산"""
        if statuses is None:
            statuses = [MissionStatusType.IN_PROGRESS, MissionStatusType.COMPLETED]

        stmt = select(func.count(UserMission.id)).where(
            UserMission.mission_id == mission_id, UserMission.status.in_(statuses)  # type: ignore
        )
        result = await session.execute(stmt)
        return result.scalar() or 0

    async def get_missions_by_challenge(
        self, session: AsyncSession, challenge_id: int
    ) -> list[tuple[Mission, ChallengeMission]]:
        """챌린지에 속한 미션들과 관계 정보 조회"""
        stmt = (
            select(Mission, ChallengeMission)
            .join(ChallengeMission, Mission.id == ChallengeMission.mission_id)
            .where(ChallengeMission.challenge_id == challenge_id)
            .order_by(ChallengeMission.step)
        )
        result = await session.execute(stmt)
        return result.all()


class UserChallengeRepository(GenericRepository):
    def __init__(self):
        super().__init__(UserChallenge)

    async def get_current_challenge(self, session: AsyncSession, user_id: int) -> UserChallenge | None:
        return await self.find_one(session, user_id=user_id, status=ChallengeStatusType.IN_PROGRESS)

    async def get_completed_challenges(self, session: AsyncSession, user_id: int) -> list[UserChallenge]:
        """완료된 챌린지 목록 조회"""
        return await self.find_all(session, user_id=user_id, status=ChallengeStatusType.COMPLETED)


class UserMissionRepository(GenericRepository):
    def __init__(self):
        super().__init__(UserMission)

    async def get_missions_by_user_challenge(self, session: AsyncSession, user_challenge_id: int) -> list[UserMission]:
        """유저 챌린지에 속한 미션들 조회"""
        return await self.find_all(session, user_challenge_id=user_challenge_id)
