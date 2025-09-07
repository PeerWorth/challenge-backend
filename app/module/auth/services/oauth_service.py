import httpx
from os import getenv
from dotenv import load_dotenv
from fastapi import status
from app.module.auth.error import InvalidKakaoTokenException, MissingSocialIDException, NoKakaoURLException


load_dotenv()

_kakao_token_info_url = getenv("KAKAO_TOKEN_INFO_URL")

if not _kakao_token_info_url:
    raise NoKakaoURLException()

KAKAO_TOKEN_INFO_URL: str = _kakao_token_info_url

class AuthService:
    def __init__(self):
        pass
    
    async def verify_kakao_token(self, id_token: str) -> str:
        data = {"id_token": id_token}
        headers = {"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"}

        async with httpx.AsyncClient() as client:            
            response = await client.post(KAKAO_TOKEN_INFO_URL, data=data, headers=headers)
            if response.status_code is not status.HTTP_200_OK:
                raise InvalidKakaoTokenException()

            id_info: dict = response.json()
            social_id = id_info.get("sub", None)

            if social_id is None:
                raise MissingSocialIDException

            return social_id
