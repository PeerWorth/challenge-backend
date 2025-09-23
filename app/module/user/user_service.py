from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.user.v1.schema import ProfileRequest
from app.database.generic_repository import GenericRepository
from app.model.user import User, UserConsent
from app.module.user.enums import AgreeTypes
from app.module.user.error import UserNotFoundException


class UserService:
    def __init__(self):
        self.user_repository = GenericRepository(User)
        self.user_consent_repository = GenericRepository(UserConsent)

    async def get_user_id_by_social_id(self, session: AsyncSession, social_id: str) -> User:
        user = await self.user_repository.find_by_field(session, "social_id", social_id)
        if not user:
            raise UserNotFoundException()
        return user  # type: ignore

    async def upsert_user_consent(
        self,
        session: AsyncSession,
        user_id: int,
        event: str,
        agree: bool,
    ) -> None:
        await self.user_consent_repository.upsert(
            session=session,
            conflict_keys=["user_id", "event"],
            return_instance=False,
            user_id=user_id,
            event=event,
            agree=agree,
        )

    async def update_user_profile(
        self,
        session: AsyncSession,
        user_id: int,
        **update_data: Any,
    ) -> None:
        user = await self.user_repository.get_by_id(session, user_id)
        if not user:
            raise UserNotFoundException()

        protected_fields = {"id", "provider", "social_id", "created_at", "updated_at"}

        filtered_data = {k: v for k, v in update_data.items() if k not in protected_fields}

        await self.user_repository.update_instance(
            session=session,
            instance=user,
            **filtered_data,
        )

    async def register_user_profile(
        self,
        session: AsyncSession,
        user_id: int,
        request_data: ProfileRequest,
    ) -> None:
        await self.update_user_profile(
            session=session,
            user_id=user_id,
            nickname=request_data.nickname,
            birthday=request_data.birthday,
            gender=request_data.gender,
        )

        await self.upsert_user_consent(
            session=session,
            user_id=user_id,
            event=AgreeTypes.PERSONAL_INFO.value,
            agree=True,
        )

        await self.upsert_user_consent(
            session=session,
            user_id=user_id,
            event=AgreeTypes.TERM_OF_USE.value,
            agree=True,
        )
