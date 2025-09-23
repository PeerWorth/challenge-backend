from typing import Any, List, Optional, Type, TypeVar

from sqlalchemy import delete, select
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

T = TypeVar("T", bound=SQLModel)


class GenericRepository:
    def __init__(self, model: Type[T]):
        self.model = model

    async def create(self, session: AsyncSession, **kwargs):
        instance = self.model(**kwargs)
        session.add(instance)
        await session.flush()
        return instance

    async def get_by_id(self, session: AsyncSession, id: Any) -> T | None:
        return await session.get(self.model, id)  # type: ignore

    async def find_one(self, session: AsyncSession, **filters) -> T | None:
        query = select(self.model).filter_by(**filters)
        result = await session.execute(query)
        return result.scalar_one_or_none()  # type: ignore

    async def find_by_field(self, session: AsyncSession, field_name: str, field_value: Any) -> T | None:
        if not hasattr(self.model, field_name):
            raise ValueError(f"모델 {self.model.__name__}에서 필드 '{field_name}'를 찾을 수 없습니다.")

        field = getattr(self.model, field_name)
        query = select(self.model).where(field == field_value)
        result = await session.execute(query)
        return result.scalar_one_or_none()  # type: ignore

    async def find_all(self, session: AsyncSession, **filters) -> List[T]:
        query = select(self.model).filter_by(**filters)
        result = await session.execute(query)
        return list(result.scalars().all())  # type: ignore

    async def update(self, session: AsyncSession, id: Any, **update_data):
        instance = await self.get_by_id(session, id)  # type: ignore
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
        await session.flush()
        await session.refresh(instance)
        return instance

    async def delete(self, session: AsyncSession, id: Any) -> bool:
        instance = await self.get_by_id(session, id)  # type: ignore
        if not instance:
            return False

        await session.delete(instance)
        await session.flush()
        return True

    async def delete_by_field(self, session: AsyncSession, **filters) -> int:
        stmt = delete(self.model).filter_by(**filters)
        result = await session.execute(stmt)
        await session.flush()
        return result.rowcount

    async def upsert(
        self, session: AsyncSession, conflict_keys: List[str], return_instance: bool = False, **data: Any
    ) -> Optional[Any]:
        stmt = insert(self.model).values(**data)

        update_dict = {key: value for key, value in data.items() if key not in conflict_keys}
        if update_dict:
            stmt = stmt.on_duplicate_key_update(**update_dict)

        await session.execute(stmt)
        await session.flush()

        if return_instance:
            filters = {key: data[key] for key in conflict_keys}
            return await self.find_one(session, **filters)

        return None
