from pydantic import BaseModel, Field, field_validator


class JWTPayload(BaseModel):
    exp: int = Field(description="토큰 만료 시간 (Unix timestamp)")
    social_id: str = Field(description="사용자 social_id")
    user_id: int = Field(description="내부 사용자 ID")

    @field_validator("user_id", mode="before")
    @classmethod
    def convert_user_id(cls, v: str | int) -> int:
        return int(v) if isinstance(v, str) else v
