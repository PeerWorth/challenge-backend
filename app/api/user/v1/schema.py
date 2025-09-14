from datetime import date

from pydantic import Field

from app.common.schema import CamelBaseModel


class ProfileRequest(CamelBaseModel):
    nickname: str = Field(..., description="사용자 닉네임", examples=["홍길동"])
    birthday: date = Field(..., description="생년월일 (YYYY-MM-DD 형식)", examples=["1996-04-14"])
    gender: bool = Field(..., description="성별 (true: 남성, false: 여성)", examples=[True])
    agree_marketing: bool = Field(
        ..., description="마케팅 정보 수신 동의 (선택, true/false 모두 허용)", examples=[True]
    )


class ProfileResponse(CamelBaseModel):
    success: bool
