# 배포 가이드

## 🏗️ 인프라 아키텍처

```
1. Terraform (수동) → AWS Parameter Store + Secrets Manager (환경변수 저장)
2. GitHub Actions → SAM Lambda 함수 배포 (환경변수 자동 주입)
```

## 📋 필요한 GitHub Secrets

Repository → Settings → Secrets and variables → Actions에서 다음 시크릿을 설정하세요:

| Secret Key | 설명 | 예시값 |
|------------|------|--------|
| `AWS_ACCESS_KEY_ID` | AWS 액세스 키 | `AKIA...` |
| `AWS_SECRET_ACCESS_KEY` | AWS 시크릿 키 | `abcd1234...` |

## 🚀 배포 프로세스

### 1단계: 수동 인프라 설정 (관리자만, 인프라 변경 시에만)

```bash
# 1. Terraform으로 인프라 생성 (Parameter Store + Secrets Manager)
cd infra/terraform
terraform init
terraform plan -var-file="terraform.prod.tfvars"
terraform apply -var-file="terraform.prod.tfvars"

# 2. JWT 시크릿 수동 설정 (최초 1회만)
aws secretsmanager put-secret-value \
  --region ap-northeast-2 \
  --secret-id "challenge-prod-jwt" \
  --secret-string '{"JWT_SECRET":"your-super-secret-jwt-key"}'
```

### 2단계: 자동 애플리케이션 배포 (GitHub Actions)

main 브랜치로 PR 병합 시 자동으로 실행됩니다:

1. ✅ **SAM 빌드 및 배포**: Lambda 함수 배포 (환경변수 자동 주입)

## 📊 환경변수 관리 구조

### Parameter Store (무료 - 일반 설정)
```
/challenge/prod/app/environment → "prod"
/challenge/prod/app/region → "ap-northeast-2"
/challenge/prod/app/project_name → "challenge"
/challenge/prod/app/jwt_algorithm → "HS256"

/challenge/prod/db/host → "challenge-prod-mysql.xxx.ap-northeast-2.rds.amazonaws.com"
/challenge/prod/db/port → "3306"
/challenge/prod/db/database → "challenge"
/challenge/prod/db/username → "root"
```

### Secrets Manager (유료 - 민감 정보)
```
challenge-prod-jwt → {"JWT_SECRET": "your-secret"}
challenge-prod-db → {
  "password": "your-db-password",
  "mysql_url": "mysql+aiomysql://root:password@host:3306/challenge"
}
```

## 🔄 환경변수 추가 방법

### 1. 일반 설정값 추가 (무료)

**Terraform** (`infra/terraform/parameter_store.tf`):
```terraform
resource "aws_ssm_parameter" "app_config" {
  for_each = {
    "environment"    = var.environment
    "region"        = var.aws_region
    "new_setting"   = "new_value"  # 👈 새로운 설정 추가
  }
  # ...
}
```

**SAM Template** (`infra/sam/template.yaml`):
```yaml
Environment:
  Variables:
    NEW_SETTING: !Sub "{{resolve:ssm:/${ProjectName}/${Environment}/app/new_setting}}"
```

### 2. 민감 정보 추가 (유료)

**수동으로 Secrets Manager에 추가**:
```bash
aws secretsmanager put-secret-value \
  --secret-id "challenge-prod-jwt" \
  --secret-string '{"JWT_SECRET":"old-value", "NEW_SECRET":"new-value"}'
```

**SAM Template**:
```yaml
Environment:
  Variables:
    NEW_SECRET: !Sub "{{resolve:secretsmanager:${ProjectName}-${Environment}-jwt:SecretString:NEW_SECRET}}"
```

## 🔄 역할 분리

### 🏗️ **인프라 관리자 (Terraform)**
- Parameter Store, Secrets Manager 생성/관리
- RDS, VPC 등 인프라 변경
- **실행 빈도**: 인프라 변경 시에만 (드물게)

### 👨‍💻 **개발자 (GitHub Actions)**
- 애플리케이션 코드 배포
- Lambda 함수 업데이트
- **실행 빈도**: 매 PR 병합 시 (자주)

## 🧪 로컬 개발

로컬에서는 `.env` 파일 사용:
```bash
# .env
ENVIRONMENT=dev
JWT_SECRET=local-jwt-secret
JWT_ALGORITHM=HS256
DEV_MYSQL_URL=mysql+aiomysql://root:password@localhost:3306/challenge
```

## 🐛 트러블슈팅

### JWT 에러: NoJWTSecretException
```bash
# JWT 시크릿이 설정되지 않은 경우
aws secretsmanager put-secret-value \
  --secret-id "challenge-prod-jwt" \
  --secret-string '{"JWT_SECRET":"your-jwt-secret"}'
```

### 데이터베이스 연결 에러
```bash
# DB 시크릿 확인
aws secretsmanager get-secret-value \
  --secret-id "challenge-prod-db" \
  --region ap-northeast-2
```

### Parameter Store 값 확인
```bash
# Parameter 값 확인
aws ssm get-parameter \
  --name "/challenge/prod/app/environment" \
  --region ap-northeast-2
```

## 💰 비용 예상

- **Parameter Store**: 무료 (Standard 티어)
- **Secrets Manager**: 약 $0.80/월 (JWT + DB 시크릿 2개)
- **Lambda**: 사용량에 따라 (일반적으로 매우 저렴)

## ✅ 장점

1. **역할 분리**: 인프라와 애플리케이션 배포 분리
2. **빠른 배포**: GitHub Actions는 SAM만 실행 (빠름)
3. **안전성**: 인프라 변경은 신중하게 수동으로
4. **비용 효율**: Parameter Store 활용으로 비용 절감

## 🔐 보안 고려사항

1. ✅ **민감 정보는 Secrets Manager**: 자동 암호화
2. ✅ **GitHub Secrets 최소화**: AWS 자격증명만 필요
3. ✅ **VPC 보안**: RDS는 VPC 내부에서만 접근 가능
