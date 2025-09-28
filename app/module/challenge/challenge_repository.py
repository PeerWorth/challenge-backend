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

    async def get_with_missions(
        self, session: AsyncSession, challenge_id: int
    ) -> tuple[Challenge, list[Mission], list[ChallengeMission]]:
        challenge = await self.get_by_id(session, challenge_id)  # type: ignore
        if not challenge:
            raise ChallengeNotFoundError(challenge_id)

        missions_stmt = (
            select(Mission).join(ChallengeMission).where(ChallengeMission.challenge_id == challenge_id)  # type: ignore
        )  # type: ignore
        missions_result = await session.execute(missions_stmt)
        missions = list(missions_result.scalars().all())

        cm_stmt = (
            select(ChallengeMission)
            .where(ChallengeMission.challenge_id == challenge_id)  # type: ignore
            .order_by(ChallengeMission.step)  # type: ignore
        )
        cm_result = await session.execute(cm_stmt)
        challenge_missions = list(cm_result.scalars().all())

        if not missions or not challenge_missions:
            raise MissionDataIncompleteError(challenge_id)

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


class UserMissionRepository(GenericRepository):
    def __init__(self):
        super().__init__(UserMission)

    async def get_missions_by_user_challenge(self, session: AsyncSession, user_challenge_id: int) -> list[UserMission]:
        return await self.find_all(session, user_challenge_id=user_challenge_id)
