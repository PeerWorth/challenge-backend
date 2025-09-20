from datetime import datetime, timedelta
from typing import Any, Dict, List

import boto3
from botocore.exceptions import ClientError


class S3CleanupService:

    def __init__(self, bucket_name: str, safety_margin_days: int = 2):
        self.s3_client = boto3.client("s3")
        self.bucket_name = bucket_name
        self.safety_margin_days = safety_margin_days
        self.confirmed_tag_value = "confirmed"

    def cleanup_orphan_files(self) -> Dict[str, Any]:
        cutoff_time = datetime.now() - timedelta(days=self.safety_margin_days)

        deleted_files = []
        skipped_files = []
        errors = []

        try:

            objects = self._list_all_objects()

            for obj in objects:
                if not self._is_old_enough(obj, cutoff_time):
                    continue

                file_key = obj["Key"]

                if self._is_confirmed_file(file_key):
                    skipped_files.append(file_key)
                    continue

                if self._delete_file(file_key):
                    deleted_files.append(file_key)
                else:
                    error_msg = f"Failed to delete {file_key}"
                    errors.append(error_msg)

        except Exception as e:
            error_msg = f"Cleanup process failed: {str(e)}"
            errors.append(error_msg)

        return {
            "deleted_count": len(deleted_files),
            "skipped_count": len(skipped_files),
            "error_count": len(errors),
            "deleted_files": deleted_files,
            "skipped_files": skipped_files,
            "errors": errors,
            "cutoff_time": cutoff_time.isoformat(),
            "safety_margin_days": self.safety_margin_days,
        }

    def _list_all_objects(self) -> List[Dict[str, Any]]:
        objects = []

        try:
            paginator = self.s3_client.get_paginator("list_objects_v2")
            pages = paginator.paginate(Bucket=self.bucket_name)

            for page in pages:
                if "Contents" in page:
                    objects.extend(page["Contents"])

        except ClientError:
            raise

        return objects

    def _is_old_enough(self, obj: Dict[str, Any], cutoff_time: datetime) -> bool:
        if "LastModified" not in obj:
            return False

        last_modified = obj["LastModified"].replace(tzinfo=None)
        return last_modified < cutoff_time

    def _is_confirmed_file(self, file_key: str) -> bool:
        try:
            response = self.s3_client.get_object_tagging(Bucket=self.bucket_name, Key=file_key)

            if "TagSet" not in response:
                return False

            tags = {tag["Key"]: tag["Value"] for tag in response["TagSet"]}
            return tags.get("status") == self.confirmed_tag_value

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")

            if error_code == "NoSuchKey":
                return False
            elif error_code in ["AccessDenied", "NoSuchTagSet"]:
                return False
            else:
                return False

        except Exception:
            return False

    def _delete_file(self, file_key: str) -> bool:
        try:
            self.s3_client.delete_object(Bucket=self.bucket_name, Key=file_key)
            return True

        except ClientError as e:
            error_code = e.response.get("Error", {}).get("Code", "")

            if error_code == "NoSuchKey":
                return True
            else:
                return False

        except Exception:
            return False
