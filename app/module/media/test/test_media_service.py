import os
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from botocore.exceptions import ClientError

from app.module.media.enums import UploadType
from app.module.media.media_service import MediaService


class TestMediaService:
    @patch.dict(os.environ, {"S3_BUCKET_NAME": "test-bucket", "CUSTOM_AWS_REGION": "us-east-1"})
    @patch("boto3.client")
    def test_init_success(self, mock_boto3_client):
        # given
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client

        # when
        service = MediaService()

        # then
        assert service.bucket_name == "test-bucket"
        assert service.s3_client == mock_s3_client
        mock_boto3_client.assert_called_once_with("s3", region_name="us-east-1")

    @patch.dict(os.environ, {}, clear=True)
    def test_init_missing_bucket_name(self):
        # given
        # when & then
        with pytest.raises(ValueError, match="S3_BUCKET_NAME 환경변수가 설정되지 않았습니다."):
            MediaService()

    @patch.dict(os.environ, {"S3_BUCKET_NAME": "test-bucket", "CUSTOM_AWS_REGION": "us-east-1"})
    @patch("boto3.client")
    @patch("uuid.uuid4")
    @patch("app.module.media.media_service.datetime")
    def test_generate_file_key_content_type(self, mock_datetime, mock_uuid, mock_boto3_client):
        # given
        mock_boto3_client.return_value = Mock()
        mock_datetime.now.return_value = datetime(2025, 9, 16, 10, 30, 0)
        mock_uuid.return_value.hex = "abcd1234ef567890"
        service = MediaService()

        # when
        result = service.generate_file_key(UploadType.CONTENT)

        # then
        assert result == "content/2025-09-16/abcd1234.jpg"

    @patch.dict(os.environ, {"S3_BUCKET_NAME": "test-bucket", "CUSTOM_AWS_REGION": "us-east-1"})
    @patch("boto3.client")
    @patch("uuid.uuid4")
    @patch("app.module.media.media_service.datetime")
    def test_generate_file_key_profile_type(self, mock_datetime, mock_uuid, mock_boto3_client):
        # given
        mock_boto3_client.return_value = Mock()
        mock_datetime.now.return_value = datetime(2023, 12, 25, 15, 45, 30)
        mock_uuid.return_value.hex = "xyz987654321abcd"
        service = MediaService()

        # when
        result = service.generate_file_key(UploadType.PROFILE)

        # then
        assert result == "profile/2023-12-25/xyz98765.jpg"

    @patch.dict(os.environ, {"S3_BUCKET_NAME": "test-bucket", "CUSTOM_AWS_REGION": "us-east-1"})
    @patch("boto3.client")
    def test_create_presigned_upload_url_success(self, mock_boto3_client):
        # given
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client
        mock_s3_client.generate_presigned_post.return_value = {
            "url": "https://test-bucket.s3.amazonaws.com/",
            "fields": {
                "key": "content/2025-09-16/abcd1234.jpg",
                "policy": "encoded_policy",
            },
        }
        service = MediaService()

        # when
        result = service.create_presigned_upload_url(UploadType.CONTENT)

        # then
        assert result["upload_url"] == "https://test-bucket.s3.amazonaws.com/"
        assert result["fields"]["key"] == "content/2025-09-16/abcd1234.jpg"
        assert result["fields"]["policy"] == "encoded_policy"
        mock_s3_client.generate_presigned_post.assert_called_once()

    @patch.dict(os.environ, {"S3_BUCKET_NAME": "test-bucket", "CUSTOM_AWS_REGION": "us-east-1"})
    @patch("boto3.client")
    def test_create_presigned_upload_url_default_upload_type(self, mock_boto3_client):
        # given
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client
        mock_s3_client.generate_presigned_post.return_value = {
            "url": "https://test-bucket.s3.amazonaws.com/",
            "fields": {"key": "content/2025-09-16/abcd1234.jpg"},
        }
        service = MediaService()

        # when
        result = service.create_presigned_upload_url()

        # then
        assert result["upload_url"] == "https://test-bucket.s3.amazonaws.com/"
        mock_s3_client.generate_presigned_post.assert_called_once()

    @patch.dict(os.environ, {"S3_BUCKET_NAME": "test-bucket", "CUSTOM_AWS_REGION": "us-east-1"})
    @patch("boto3.client")
    def test_create_presigned_upload_url_client_error(self, mock_boto3_client):
        # given
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client
        error_response = {
            "Error": {"Code": "AccessDenied", "Message": "Access denied"},
            "ResponseMetadata": {"HTTPStatusCode": 403},
        }
        mock_s3_client.generate_presigned_post.side_effect = ClientError(error_response, "GeneratePresignedPost")
        service = MediaService()

        # when & then
        with pytest.raises(Exception, match="S3 presigned URL 생성 실패: AccessDenied - Access denied"):
            service.create_presigned_upload_url(UploadType.CONTENT)

    @patch.dict(os.environ, {"S3_BUCKET_NAME": "test-bucket", "CUSTOM_AWS_REGION": "us-east-1"})
    @patch("boto3.client")
    def test_create_presigned_upload_url_client_error_missing_fields(self, mock_boto3_client):
        # given
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client
        error_response = {"ResponseMetadata": {"HTTPStatusCode": 500}}
        mock_s3_client.generate_presigned_post.side_effect = ClientError(error_response, "GeneratePresignedPost")
        service = MediaService()

        # when & then
        with pytest.raises(Exception, match="S3 presigned URL 생성 실패: Unknown - Unknown error"):
            service.create_presigned_upload_url(UploadType.PROFILE)

    @patch.dict(os.environ, {"S3_BUCKET_NAME": "test-bucket", "CUSTOM_AWS_REGION": "us-east-1"})
    @patch("boto3.client")
    def test_create_presigned_upload_url_generic_exception(self, mock_boto3_client):
        # given
        mock_s3_client = Mock()
        mock_boto3_client.return_value = mock_s3_client
        mock_s3_client.generate_presigned_post.side_effect = ValueError("Invalid parameter")
        service = MediaService()

        # when & then
        with pytest.raises(Exception, match="예상치 못한 오류 발생: Invalid parameter"):
            service.create_presigned_upload_url(UploadType.CONTENT)
