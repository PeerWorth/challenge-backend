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
