from pydantic import Field

from app.common.schema import CamelBaseModel
from app.module.user.enums import GenderTypes


class ProfileRequest(CamelBaseModel):
    nickname: str = Field(..., description="사용자 닉네임", examples=["홍길동"])
    birthday: int = Field(..., description="생년월일 (YYYY 형식)", examples=["1996"])
    gender: GenderTypes = Field(..., description="성별 (남성: man, 여성: woman)", examples=["man"])


class ProfileResponse(CamelBaseModel):
    success: bool
