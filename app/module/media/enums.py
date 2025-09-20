from enum import StrEnum


class UploadType(StrEnum):
    PROFILE = "profile"
    CONTENT = "content"

    @classmethod
    def from_file_key(cls, file_key: str) -> "UploadType":
        if file_key.startswith("profile/"):
            return cls.PROFILE
        else:
            return cls.CONTENT


class S3ObjectStatus(StrEnum):
    PENDING = "pending"  # 업로드 직후, 게시물 작성 전
    CONFIRMED = "confirmed"  # 게시물 업로드와 게시물 저장 연결 됨
