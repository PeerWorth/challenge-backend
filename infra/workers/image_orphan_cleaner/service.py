from datetime import datetime, timedelta

import boto3
from enums import S3ObjectStatus
from schema import S3Object, S3ObjectTags


class S3CleanupService:
    def __init__(self, bucket_name: str, safety_margin_days: int = 2):
        self.s3_client = boto3.client("s3")
        self.bucket_name = bucket_name
        self.safety_margin_days = safety_margin_days

    def cleanup_orphan_files(self) -> None:
        cutoff_time = datetime.now() - timedelta(days=self.safety_margin_days)

        objects = self._list_all_objects()

        for obj in objects:
            if not obj.is_old_enough(cutoff_time):
                continue

            if self._is_confirmed_file(obj.key):
                continue

            self._delete_file(obj.key)

        return

    def _list_all_objects(self) -> list[S3Object]:
        result = []

        paginator = self.s3_client.get_paginator("list_objects_v2")
        pages = paginator.paginate(Bucket=self.bucket_name)

        for page in pages:
            if "Contents" in page:
                s3_objects = [S3Object.from_s3_response(dict(obj_data)) for obj_data in page["Contents"]]
                result.extend(s3_objects)

        return result

    def _is_confirmed_file(self, file_key: str) -> bool:
        try:
            response = self.s3_client.get_object_tagging(Bucket=self.bucket_name, Key=file_key)

            # Pydantic 모델로 변환
            s3_tags = S3ObjectTags.from_s3_response(dict(response))

            # status=confirmed 태그 확인
            return s3_tags.has_status_confirmed(S3ObjectStatus.CONFIRMED)

        except Exception:
            return False

    def _delete_file(self, file_key: str) -> None:
        self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
        return
