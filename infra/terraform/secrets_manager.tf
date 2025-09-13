# Secrets Manager - 민감한 정보 (유료)

# JWT 시크릿
resource "aws_secretsmanager_secret" "jwt_secrets" {
  name        = "${var.project_name}-${var.environment}-jwt"
  description = "JWT secrets for ${var.project_name} ${var.environment} environment"

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Type        = "JWT"
  }
}

# DB 비밀번호 및 완성된 연결 문자열
resource "aws_secretsmanager_secret" "db_credentials" {
  name        = "${var.project_name}-${var.environment}-db"
  description = "Database credentials for ${var.project_name} ${var.environment} environment"

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Type        = "Database"
  }
}

# DB 시크릿 초기값 설정 (비밀번호 포함)
resource "aws_secretsmanager_secret_version" "db_credentials" {
  secret_id = aws_secretsmanager_secret.db_credentials.id
  secret_string = jsonencode({
    password = var.db_password
    mysql_url = "mysql+aiomysql://${aws_db_instance.mysql.username}:${var.db_password}@${aws_db_instance.mysql.endpoint}:${aws_db_instance.mysql.port}/${aws_db_instance.mysql.db_name}"
  })
}

# Lambda 함수가 Secrets Manager에 접근할 수 있도록 IAM 역할 생성
resource "aws_iam_role" "lambda_execution_role" {
  name_prefix = "${var.project_name}-${var.environment}-lambda-"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# Lambda 기본 실행 정책 연결
resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Parameter Store 및 Secrets Manager 접근 정책
resource "aws_iam_policy" "lambda_secrets_policy" {
  name_prefix = "${var.project_name}-${var.environment}-lambda-secrets-"
  description = "Policy for Lambda to access Parameter Store and Secrets Manager"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:GetParametersByPath"
        ]
        Resource = [
          "arn:aws:ssm:${var.aws_region}:*:parameter/${var.project_name}/${var.environment}/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "secretsmanager:GetSecretValue"
        ]
        Resource = [
          aws_secretsmanager_secret.jwt_secrets.arn,
          aws_secretsmanager_secret.db_credentials.arn
        ]
      }
    ]
  })

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }
}

# 정책을 Lambda 역할에 연결
resource "aws_iam_role_policy_attachment" "lambda_secrets_policy" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = aws_iam_policy.lambda_secrets_policy.arn
}
