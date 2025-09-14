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
        social_id: str,
        **update_data: Any,
    ) -> User:
        user = await self.user_repository.find_by_field(session, "social_id", social_id)

        if not user:
            raise UserNotFoundException()

        protected_fields = {"provider", "social_id", "id"}
        filtered_data = {k: v for k, v in update_data.items() if k not in protected_fields}

        updated_user = await self.user_repository.update_instance(
            session=session,
            instance=user,
            **filtered_data,
        )

        return updated_user

    async def register_user_profile(
        self,
        session: AsyncSession,
        social_id: str,
        request_data: ProfileRequest,
    ) -> User:
        updated_user = await self.update_user_profile(
            session=session,
            social_id=social_id,
            nickname=request_data.nickname,
            birthday=request_data.birthday,
            gender=request_data.gender,
            phone=None,
        )

        await self.upsert_user_consent(
            session=session,
            user_id=updated_user.id,
            event=AgreeTypes.PERSONAL_INFO.value,
            agree=True,
        )

        await self.upsert_user_consent(
            session=session,
            user_id=updated_user.id,
            event=AgreeTypes.TERM_OF_USE.value,
            agree=True,
        )

        await self.upsert_user_consent(
            session=session,
            user_id=updated_user.id,
            event=AgreeTypes.MARKETING.value,
            agree=request_data.agree_marketing,
        )

        return updated_user
