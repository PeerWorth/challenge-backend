import os
import uuid
from datetime import datetime
from typing import Any, Dict

import boto3
from botocore.exceptions import ClientError

from app.module.media.enums import UploadType


class MediaService:
    def __init__(self):
        self.s3_client = boto3.client(
            "s3",
            region_name=os.getenv("AWS_REGION"),
        )
        self.bucket_name = os.getenv("S3_BUCKET_NAME")
        self.presigned_url_expiration = 3600

    def generate_file_key(
        self,
        user_id: str,
        upload_type: UploadType,
    ) -> str:
        file_extension = "jpg"

        today = datetime.now()
        date_path = today.strftime("%Y/%m/%d")
        unique_id = uuid.uuid4().hex[:8]
        return f"{upload_type}/{user_id}/{date_path}/{unique_id}.{file_extension}"

    def create_presigned_upload_url(
        self,
        user_id: str,
        upload_type: UploadType = UploadType.CONTENT,
    ) -> Dict[str, Any]:
        try:
            file_key = self.generate_file_key(user_id, upload_type)

            response = self.s3_client.generate_presigned_post(
                Bucket=self.bucket_name,
                Key=file_key,
                ExpiresIn=self.presigned_url_expiration,
            )

            return {
                "upload_url": response["url"],
                "fields": response["fields"],
            }

        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            error_message = e.response["Error"]["Message"]
            raise Exception(f"S3 presigned URL 생성 실패: {error_code} - {error_message}")
        except Exception as e:
            raise Exception(f"예상치 못한 오류 발생: {str(e)}")
