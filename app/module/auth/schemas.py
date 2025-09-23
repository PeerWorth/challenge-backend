from pydantic import BaseModel, Field


class JWTPayload(BaseModel):
    exp: int = Field(description="토큰 만료 시간 (Unix timestamp)")
    social_id: str = Field(description="Subject - 사용자 social_id")
    user_id: str = Field(description="내부 사용자 ID")

    @property
    def user_id_int(self) -> int:
        return int(self.user_id)
