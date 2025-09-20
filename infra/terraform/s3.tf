# S3 버킷 설정
resource "aws_s3_bucket" "media" {
  bucket = "${var.project_name}-backend-media-${var.environment}"

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Purpose     = "Media Storage"
  }
}

# S3 버킷 버전 관리
resource "aws_s3_bucket_versioning" "media" {
  bucket = aws_s3_bucket.media.id

  versioning_configuration {
    status = "Enabled"
  }
}

# S3 버킷 CORS 설정 (브라우저에서 직접 업로드용)
resource "aws_s3_bucket_cors_configuration" "media" {
  bucket = aws_s3_bucket.media.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["PUT", "POST", "GET"]
    allowed_origins = ["*"]
    expose_headers  = ["ETag"]
    max_age_seconds = 3000
  }
}

# S3 버킷 퍼블릭 액세스 차단
resource "aws_s3_bucket_public_access_block" "media" {
  bucket = aws_s3_bucket.media.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# S3 버킷 암호화
resource "aws_s3_bucket_server_side_encryption_configuration" "media" {
  bucket = aws_s3_bucket.media.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S3 버킷 Lifecycle 정책 (미완성 업로드만 정리)
resource "aws_s3_bucket_lifecycle_configuration" "media" {
  bucket = aws_s3_bucket.media.id

  rule {
    id     = "cleanup-incomplete-uploads"
    status = "Enabled"

    abort_incomplete_multipart_upload {
      days_after_initiation = 1  # 미완성 멀티파트 업로드 1일 후 정리
    }
  }
}

# Lambda 함수용 IAM 정책
resource "aws_iam_policy" "lambda_s3_access" {
  name        = "${var.project_name}-lambda-s3-access-${var.environment}"
  description = "Lambda function S3 access policy for media bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.media.arn,
          "${aws_s3_bucket.media.arn}/*"
        ]
      }
    ]
  })
}

# Parameter Store에 S3 버킷 이름 저장
resource "aws_ssm_parameter" "s3_bucket_name" {
  name  = "/${var.environment}/${var.project_name}/s3/media-bucket-name"
  type  = "String"
  value = aws_s3_bucket.media.id

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}
