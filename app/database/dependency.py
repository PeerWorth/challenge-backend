from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.config import get_async_session_maker


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    session_maker = get_async_session_maker()
    async with session_maker() as session:
        session: AsyncSession
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()