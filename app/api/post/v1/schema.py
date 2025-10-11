from pydantic import Field

from app.common.schema import CamelBaseModel


class PostRequest(CamelBaseModel):
    mission_id: int = Field(..., description="미션 ID")
    content: str = Field(..., description="게시물 내용")
    image_key: str | None = Field(None, description="이미지 S3 키 (선택사항)")


class PostResponse(CamelBaseModel):
    success: bool
    status_code: int


class PostInfoResponse(CamelBaseModel):
    user_id: int = Field(description="유저 ID")
    post_id: int = Field(description="게시물 ID")
    nickname: str = Field(description="닉네임")
    like: int = Field(description="좋아요 개수")
    image_url: str | None = Field(description="이미지 URL (Presigned URL)")


class PostLikeResponse(CamelBaseModel):
    is_liked: bool = Field(description="좋아요 상태 (True: 좋아요 추가됨, False: 좋아요 취소됨)")
