import httpx
from dotenv import load_dotenv
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.generic_repository import GenericRepository
from app.model.user import User
from app.module.auth.enums import OAuthProvider
from app.module.auth.error import InvalidKakaoTokenException, MissingSocialIDException

load_dotenv()

KAKAO_TOKEN_INFO_URL = "https://kauth.kakao.com/oauth/tokeninfo"


class AuthService:
    def __init__(self):
        self.user_repository = GenericRepository(User)

    async def create_user_with_social_id(self, session: AsyncSession, social_id: str) -> User:
        return await self.user_repository.create(  # type: ignore
            session,
            provider=OAuthProvider.KAKAO,
            social_id=social_id,
            nickname=None,
            birthday=None,
            gender=None,
            phone=None,
        )

    async def find_user_by_social_id(self, session: AsyncSession, social_id: str) -> User | None:
        return await self.user_repository.find_one(
            session, provider=OAuthProvider.KAKAO, social_id=social_id
        )  # type: ignore

    async def verify_kakao_token(self, id_token: str) -> str:
        data = {"id_token": id_token}
        headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}

        async with httpx.AsyncClient() as client:
            response = await client.post(KAKAO_TOKEN_INFO_URL, data=data, headers=headers)

            if response.status_code is not status.HTTP_200_OK:
                raise InvalidKakaoTokenException(f"카카오 토큰 검증 실패: {response.status_code}")

            token_info = response.json()

            social_id = token_info.get("sub")

            if not social_id:
                raise MissingSocialIDException()

            return social_id
