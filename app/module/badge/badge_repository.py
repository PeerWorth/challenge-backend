from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.generic_repository import GenericRepository
from app.model.badge import Badge, UserBadge


class BadgeRepository(GenericRepository):
    def __init__(self):
        super().__init__(Badge)

    async def get_badge_by_name(self, session: AsyncSession, name: str) -> Badge | None:
        stmt = select(Badge).where(Badge.name == name)  # type: ignore
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_badge(self, session: AsyncSession, user_id: int, badge_id: int) -> UserBadge | None:
        stmt = select(UserBadge).where(UserBadge.user_id == user_id, UserBadge.badge_id == badge_id)  # type: ignore
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user_badge(self, session: AsyncSession, user_id: int, badge_id: int) -> None:
        user_badge = UserBadge(user_id=user_id, badge_id=badge_id)
        session.add(user_badge)
        await session.flush()
