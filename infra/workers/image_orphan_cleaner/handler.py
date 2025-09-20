import os
from typing import Any

from service import S3CleanupService


def lambda_handler(event: dict[str, Any], context: Any) -> None:

    bucket_name = os.environ["BUCKET_NAME"]
    safety_margin_days = int(os.environ.get("SAFETY_MARGIN_DAYS", "2"))

    cleanup_service = S3CleanupService(bucket_name=bucket_name, safety_margin_days=safety_margin_days)

    cleanup_service.cleanup_orphan_files()

    return
