from datetime import date

from app.common.schema import CamelBaseModel


class ProfileRequest(CamelBaseModel):
    nickname: str
    birthday: date
    gender: bool
    phone: str


class ProfileResponse(CamelBaseModel):
    success: bool
