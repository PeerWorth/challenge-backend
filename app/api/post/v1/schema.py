from pydantic import Field

from app.common.schema import CamelBaseModel


class PostRequest(CamelBaseModel):
    mission_id: int = Field(..., description="미션 ID")
    content: str = Field(..., description="게시물 내용")
    image_key: str | None = Field(None, description="이미지 S3 키 (선택사항)")


class PostResponse(CamelBaseModel):
    success: bool
    status_code: str
