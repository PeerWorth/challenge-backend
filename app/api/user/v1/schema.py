from datetime import date

from pydantic import Field, field_validator

from app.common.schema import CamelBaseModel


class ProfileRequest(CamelBaseModel):
    nickname: str = Field(..., description="사용자 닉네임", examples=["홍길동"])
    birthday: date = Field(..., description="생년월일 (YYYY-MM-DD 형식)", examples=["1996-04-14"])
    gender: bool = Field(..., description="성별 (true: 남성, false: 여성)", examples=[True])
    phone: str = Field(..., description="휴대폰 번호 (하이픈 자동 제거)", examples=["010-1234-5678"])

    @field_validator("phone")
    @classmethod
    def remove_phone_hyphens(cls, v: str) -> str:
        return v.replace("-", "")


class ProfileResponse(CamelBaseModel):
    success: bool
