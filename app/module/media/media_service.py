import os
import uuid
from datetime import datetime
from typing import Any

import boto3
from botocore.exceptions import ClientError
from mypy_boto3_s3 import S3Client

from app.module.media.constants import PRESIGNED_URL_EXPIRE_SEC
from app.module.media.enums import S3ObjectStatus, UploadType


class MediaService:
    def __init__(self):
        self.s3_client: S3Client = boto3.client(
            "s3",
            region_name=os.getenv("CUSTOM_AWS_REGION"),
        )
        bucket_name = os.getenv("S3_BUCKET_NAME")
        if not bucket_name:
            raise ValueError("S3_BUCKET_NAME 환경변수가 설정되지 않았습니다.")
        self.bucket_name = bucket_name
        self.presigned_url_expiration = PRESIGNED_URL_EXPIRE_SEC

    def generate_file_key(
        self,
        upload_type: UploadType,
    ) -> str:
        file_extension = "jpg"

        today = datetime.now()
        date_path = today.strftime("%Y-%m-%d")
        unique_id = uuid.uuid4().hex[:8]
        return f"{upload_type}/{date_path}/{unique_id}.{file_extension}"

    def create_presigned_upload_url(
        self,
        upload_type: UploadType = UploadType.CONTENT,
    ) -> dict[str, Any]:
        try:
            file_key = self.generate_file_key(upload_type)

            response = self.s3_client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=file_key,
                ExpiresIn=self.presigned_url_expiration,
            )

            return {
                "upload_url": response["url"],
                "file_key": file_key,
                "fields": response["fields"],
            }

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", "Unknown error")
            raise Exception(f"S3 presigned URL 생성 실패: {error_code} - {error_message}")
        except Exception as e:
            raise Exception(f"예상치 못한 오류 발생: {str(e)}")

    def mark_file_as_confirmed(
        self,
        file_key: str,
    ) -> None:
        try:
            self.s3_client.put_object_tagging(
                Bucket=self.bucket_name,
                Key=file_key,
                Tagging={"TagSet": [{"Key": "status", "Value": S3ObjectStatus.CONFIRMED}]},
            )
        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "Unknown")
            error_message = e.response.get("Error", {}).get("Message", "Unknown error")
            raise Exception(f"파일 태그 업데이트 실패: {error_code} - {error_message}")
        except Exception as e:
            raise Exception(f"파일 태그 업데이트 중 오류 발생: {str(e)}")
