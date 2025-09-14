from typing import Any, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeMeta

T = TypeVar("T", bound=DeclarativeMeta)


class GenericRepository:
    def __init__(self, model: Type[T]):
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

    async def find_by_field(self, session: AsyncSession, field_name: str, field_value: Any):
        if not hasattr(self.model, field_name):
            raise ValueError(f"모델 {self.model.__name__}에서 필드 '{field_name}'를 찾을 수 없습니다.")

        field = getattr(self.model, field_name)
        query = select(self.model).where(field == field_value)
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

    async def update_instance(self, session: AsyncSession, instance, **update_data):
        for key, value in update_data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)

        session.add(instance)
        await session.commit()
        await session.refresh(instance)
        return instance

    async def delete(self, session: AsyncSession, id: Any) -> bool:
        instance = await self.get_by_id(session, id)
        if not instance:
            return False

        await session.delete(instance)
        await session.flush()
        return True

    async def upsert(self, session: AsyncSession, conflict_keys: List[str], **data: Any) -> Optional[Any]:
        stmt = insert(self.model).values(**data)

        update_dict = {key: value for key, value in data.items() if key not in conflict_keys}
        if update_dict:
            stmt = stmt.on_duplicate_key_update(**update_dict)

        await session.execute(stmt)
        await session.flush()

        filters = {key: data[key] for key in conflict_keys}
        return await self.find_one(session, **filters)
