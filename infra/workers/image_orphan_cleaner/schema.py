from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class S3Object(BaseModel):
    key: str = Field(..., description="S3 객체 키 (파일 경로)")
    last_modified: datetime = Field(..., description="마지막 수정 시간")
    etag: str = Field(..., description="객체의 ETag (해시값)")
    size: int = Field(..., description="객체 크기 (바이트)")
    storage_class: str = Field(default="STANDARD", description="스토리지 클래스")
    owner_display_name: Optional[str] = Field(None, description="소유자 표시 이름")
    owner_id: Optional[str] = Field(None, description="소유자 ID")

    @classmethod
    def from_s3_response(cls, s3_object_data: dict[str, Any]) -> "S3Object":
        return cls(
            key=s3_object_data["Key"],
            last_modified=s3_object_data["LastModified"],
            etag=s3_object_data["ETag"].strip('"'),  # ETag에서 따옴표 제거
            size=s3_object_data["Size"],
            storage_class=s3_object_data.get("StorageClass", "STANDARD"),
            owner_display_name=s3_object_data.get("Owner", {}).get("DisplayName"),
            owner_id=s3_object_data.get("Owner", {}).get("ID"),
        )

    def is_old_enough(self, cutoff_time: datetime) -> bool:
        last_modified_naive = self.last_modified.replace(tzinfo=None)
        return last_modified_naive < cutoff_time


class S3Tag(BaseModel):
    key: str = Field(..., description="태그 키")
    value: str = Field(..., description="태그 값")

    @classmethod
    def from_s3_tag(cls, tag_data: dict[str, Any]) -> "S3Tag":
        return cls(key=tag_data["Key"], value=tag_data["Value"])


class S3ObjectTags(BaseModel):
    tags: list[S3Tag] = Field(default_factory=list, description="태그 목록")

    @classmethod
    def from_s3_response(cls, tag_response: dict[str, Any]) -> "S3ObjectTags":
        tag_set = tag_response.get("TagSet", [])
        tags = [S3Tag.from_s3_tag(tag_data) for tag_data in tag_set]
        return cls(tags=tags)

    def get_tag_value(self, key: str) -> Optional[str]:
        for tag in self.tags:
            if tag.key == key:
                return tag.value
        return None

    def has_status_confirmed(self, confirmed_value: str) -> bool:
        status_value = self.get_tag_value("status")
        return status_value == confirmed_value
