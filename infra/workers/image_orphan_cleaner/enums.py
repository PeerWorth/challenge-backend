from enum import StrEnum


class S3ObjectStatus(StrEnum):
    PENDING = "pending"  # 업로드 직후, 게시물 작성 전
    CONFIRMED = "confirmed"  # 게시물 업로드와 게시물 저장 연결 됨
