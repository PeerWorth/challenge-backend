# Parameter Store - 일반 설정값 (무료)
resource "aws_ssm_parameter" "app_config" {
  for_each = {
    "environment"    = var.environment
    "region"        = var.aws_region
    "project_name"  = var.project_name
    "jwt_algorithm" = "HS256"
  }

  name  = "/${var.project_name}/${var.environment}/app/${each.key}"
  type  = "String"
  value = each.value

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Type        = "Configuration"
  }
}

# RDS 연결 정보 - 민감하지 않은 정보만
resource "aws_ssm_parameter" "db_config" {
  for_each = {
    "host"     = aws_db_instance.mysql.endpoint
    "port"     = tostring(aws_db_instance.mysql.port)
    "database" = aws_db_instance.mysql.db_name
    "username" = aws_db_instance.mysql.username
  }

  name  = "/${var.project_name}/${var.environment}/db/${each.key}"
  type  = "String"
  value = each.value

  tags = {
    Environment = var.environment
    Project     = var.project_name
    Type        = "Database"
  }
}
