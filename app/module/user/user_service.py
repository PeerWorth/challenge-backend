from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.generic_repository import GenericRepository
from app.model.user import User


class UserService:
    def __init__(self):
        self.user_repository = GenericRepository(User)

    async def update_user_profile(
        self, session: AsyncSession, social_id: str, nickname: str, birthday: date, gender: bool, phone: str
    ) -> User:
        user = await self.user_repository.find_by_field(session, "social_id", social_id)

        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="사용자를 찾을 수 없습니다.")

        updated_user = await self.user_repository.update_instance(
            session=session, instance=user, nickname=nickname, birthday=birthday, gender=gender, phone=phone
        )

        return updated_user
