from sqlalchemy.ext.asyncio import AsyncSession

from app.module.badge.badge_repository import BadgeRepository
from app.module.badge.enums import BadgeNames


class BadgeService:
    def __init__(self):
        self.badge_repository = BadgeRepository()

    async def initial_badge(self, session: AsyncSession, user_id: int):
        badge = await self.badge_repository.get_badge_by_name(session, BadgeNames.FIRST_STEP)
        if not badge:
            return

        existing_user_badge = await self.badge_repository.get_user_badge(session, user_id, badge.id)
        if existing_user_badge:
            return

        await self.badge_repository.create_user_badge(session, user_id, badge.id)
