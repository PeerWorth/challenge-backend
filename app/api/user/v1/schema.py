from pydantic import Field

from app.common.schema import CamelBaseModel


class ProfileRequest(CamelBaseModel):
    nickname: str = Field(..., description="사용자 닉네임", examples=["홍길동"])
    birthday: int = Field(..., description="생년월일 (YYYY 형식)", examples=["1996"])
    gender: bool = Field(..., description="성별 (true: 남성, false: 여성)", examples=[True])


class ProfileResponse(CamelBaseModel):
    success: bool
