from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.generic_repository import GenericRepository
from app.model.challenge import Challenge, ChallengeMission, Mission
from app.model.user_challenge import UserChallenge, UserMission
from app.module.challenge.enums import ChallengeStatusType, MissionStatusType
from app.module.challenge.errors import ChallengeNotFoundError, MissionDataIncompleteError


class ChallengeRepository(GenericRepository):
    def __init__(self):
        super().__init__(Challenge)

    async def get_missions_by_challenge(self, session: AsyncSession, challenge_id: int) -> list[Mission]:
        missions_stmt = (
            select(Mission).join(ChallengeMission).where(ChallengeMission.challenge_id == challenge_id)  # type: ignore
        )
        missions_result = await session.execute(missions_stmt)
        missions = list(missions_result.scalars().all())

        if not missions:
            raise MissionDataIncompleteError(challenge_id)

        return missions

    async def get_challenge_missions(self, session: AsyncSession, challenge_id: int) -> list[ChallengeMission]:
        cm_stmt = (
            select(ChallengeMission)
            .where(ChallengeMission.challenge_id == challenge_id)  # type: ignore
            .order_by(ChallengeMission.step)  # type: ignore
        )
        cm_result = await session.execute(cm_stmt)
        challenge_missions = list(cm_result.scalars().all())

        if not challenge_missions:
            raise MissionDataIncompleteError(challenge_id)

        return challenge_missions

    async def get_with_missions(
        self, session: AsyncSession, challenge_id: int
    ) -> tuple[Challenge, list[Mission], list[ChallengeMission]]:
        challenge = await self.get_by_id(session, challenge_id)  # type: ignore
        if not challenge:
            raise ChallengeNotFoundError(challenge_id)

        missions = await self.get_missions_by_challenge(session, challenge_id)
        challenge_missions = await self.get_challenge_missions(session, challenge_id)

        return challenge, missions, challenge_missions

    async def get_multiple_with_missions(
        self, session: AsyncSession, challenge_ids: list[int]
    ) -> dict[int, tuple[Challenge, list[Mission], list[ChallengeMission]]]:
        challenges_stmt = select(Challenge).where(Challenge.id.in_(challenge_ids))  # type: ignore
        challenges_result = await session.execute(challenges_stmt)
        challenges = {c.id: c for c in challenges_result.scalars().all()}

        missions_stmt = (
            select(Mission, ChallengeMission)
            .join(ChallengeMission)
            .where(ChallengeMission.challenge_id.in_(challenge_ids))  # type: ignore
            .order_by(ChallengeMission.challenge_id, ChallengeMission.step)  # type: ignore
        )
        missions_result = await session.execute(missions_stmt)

        missions_by_challenge: dict[int, list[Mission]] = {}
        challenge_missions_by_challenge: dict[int, list[ChallengeMission]] = {}

        for mission, challenge_mission in missions_result.all():
            challenge_id = challenge_mission.challenge_id

            if challenge_id not in missions_by_challenge:
                missions_by_challenge[challenge_id] = []
                challenge_missions_by_challenge[challenge_id] = []

            missions_by_challenge[challenge_id].append(mission)
            challenge_missions_by_challenge[challenge_id].append(challenge_mission)

        result = {}
        for challenge_id in challenge_ids:
            if challenge_id in challenges:
                challenge = challenges[challenge_id]
                missions = missions_by_challenge.get(challenge_id, [])
                challenge_missions = challenge_missions_by_challenge.get(challenge_id, [])
                result[challenge_id] = (challenge, missions, challenge_missions)

        return result


class MissionRepository(GenericRepository):
    def __init__(self):
        super().__init__(Mission)

    async def count_participants(
        self, session: AsyncSession, mission_id: int, statuses: list[str] | None = None
    ) -> int:
        if statuses is None:
            statuses = [MissionStatusType.IN_PROGRESS, MissionStatusType.COMPLETED]

        stmt = select(func.count(UserMission.id)).where(  # type: ignore
            UserMission.mission_id == mission_id, UserMission.status.in_(statuses)  # type: ignore
        )
        result = await session.execute(stmt)
        return result.scalar() or 0


class UserChallengeRepository(GenericRepository):
    def __init__(self):
        super().__init__(UserChallenge)

    async def get_current_challenge(self, session: AsyncSession, user_id: int) -> UserChallenge | None:
        return await self.find_one(session, user_id=user_id, status=ChallengeStatusType.IN_PROGRESS)

    async def get_completed_challenges(self, session: AsyncSession, user_id: int) -> list[UserChallenge]:
        return await self.find_all(session, user_id=user_id, status=ChallengeStatusType.COMPLETED)

    async def create_with_first_mission(
        self, session: AsyncSession, user_id: int, challenge_id: int, first_mission_id: int
    ) -> UserChallenge:
        user_challenge = await self.create(
            session,
            user_id=user_id,
            challenge_id=challenge_id,
            status=ChallengeStatusType.IN_PROGRESS,
            mission_step=1,
        )

        user_mission_repo = UserMissionRepository()
        await user_mission_repo.create(
            session,
            user_challenge_id=user_challenge.id,
            mission_id=first_mission_id,
            status=MissionStatusType.IN_PROGRESS,
            point=0,
        )

        await session.commit()
        await session.refresh(user_challenge)

        return user_challenge


class UserMissionRepository(GenericRepository):
    def __init__(self):
        super().__init__(UserMission)

    async def get_missions_by_user_challenge(self, session: AsyncSession, user_challenge_id: int) -> list[UserMission]:
        return await self.find_all(session, user_challenge_id=user_challenge_id)

    async def get_missions_by_user_challenges_batch(
        self, session: AsyncSession, user_challenge_ids: list[int]
    ) -> dict[int, list[UserMission]]:
        """여러 유저 챌린지의 미션 데이터를 배치로 조회"""
        if not user_challenge_ids:
            return {}

        stmt = select(UserMission).where(UserMission.user_challenge_id.in_(user_challenge_ids))  # type: ignore
        result = await session.execute(stmt)
        all_user_missions = result.scalars().all()

        grouped: dict[int, list[UserMission]] = {}
        for um in all_user_missions:
            if um.user_challenge_id not in grouped:
                grouped[um.user_challenge_id] = []
            grouped[um.user_challenge_id].append(um)

        return grouped
