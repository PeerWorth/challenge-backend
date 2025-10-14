import asyncio
import os
import sys

from sqlalchemy import select

from app.data.badge.constants import BADGES_DATA
from app.database.config import get_async_session_maker
from app.model.badge import Badge


async def seed_badges():
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        result = await session.execute(select(Badge))
        existing_names = {badge.name for badge in result.scalars().all()}

        for badge_data in BADGES_DATA:
            if badge_data["name"] in existing_names:
                continue

            badge = Badge(
                category=badge_data["category"],
                name=badge_data["name"],
                description=badge_data["description"],
            )
            session.add(badge)

        await session.commit()


if __name__ == "__main__":
    if not os.getenv("ENVIRONMENT"):
        print("⚠️  ENVIRONMENT 환경변수를 설정해주세요 (dev/prod)")
        sys.exit(1)

    asyncio.run(seed_badges())
