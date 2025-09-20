import json
import os
from typing import Any, Dict

from service import S3CleanupService


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    try:
        bucket_name = os.environ["BUCKET_NAME"]
        safety_margin_days = int(os.environ.get("SAFETY_MARGIN_DAYS", "2"))

        cleanup_service = S3CleanupService(bucket_name=bucket_name, safety_margin_days=safety_margin_days)

        result = cleanup_service.cleanup_orphan_files()

        return {
            "statusCode": 200,
            "body": json.dumps({"message": "Image orphan cleanup completed successfully", "result": result}, indent=2),
        }

    except KeyError as e:
        error_msg = f"Missing required environment variable: {e}"
        return {"statusCode": 500, "body": json.dumps({"error": error_msg})}

    except Exception as e:
        error_msg = f"Image orphan cleanup failed: {str(e)}"
        return {"statusCode": 500, "body": json.dumps({"error": error_msg})}
