from pydantic import Field

from app.common.schema import CamelBaseModel
from app.module.media.enums import UploadType


class S3UrlRequest(CamelBaseModel):
    upload_type: UploadType = Field(default=UploadType.CONTENT, description="업로드 타입")


class S3UrlResponse(CamelBaseModel):
    upload_url: str = Field(..., description="S3 Presigned Upload URL")
    file_key: str = Field(..., description="업로드될 파일의 S3 키")
    fields: dict = Field(default_factory=dict, description="업로드 시 필요한 추가 필드들")
