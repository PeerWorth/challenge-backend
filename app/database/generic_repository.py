from typing import Any, List, Type

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta


class GenericRepository:
    def __init__(self, model: Type[DeclarativeMeta]):
        self.model = model

    async def create(self, session: AsyncSession, **kwargs):
        instance = self.model(**kwargs)
        session.add(instance)
        await session.flush()
        return instance

    async def get_by_id(self, session: AsyncSession, id: Any):
        return await session.get(self.model, id)

    async def find_one(self, session: AsyncSession, **filters):
        query = select(self.model).filter_by(**filters)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def find_all(self, session: AsyncSession, **filters) -> List:
        query = select(self.model).filter_by(**filters)
        result = await session.execute(query)
        return list(result.scalars().all())

    async def update(self, session: AsyncSession, id: Any, **update_data):
        instance = await self.get_by_id(session, id)
        if not instance:
            return None

        for key, value in update_data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        await session.flush()
        return instance

    async def delete(self, session: AsyncSession, id: Any) -> bool:
        instance = await self.get_by_id(session, id)
        if not instance:
            return False

        await session.delete(instance)
        await session.flush()
        return True
