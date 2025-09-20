# Workers

백그라운드 작업을 처리하는 Lambda 함수들을 관리하는 디렉토리입니다.

## 디렉토리 구조

```
infra/workers/
├── README.md                    # 이 파일
├── Makefile                    # 배포 자동화 스크립트
├── template.yaml               # SAM 템플릿
├── samconfig.toml             # SAM 배포 설정 (dev/prod)
└── image_orphan_cleaner/      # 이미지 orphan 정리 서비스
    ├── requirements.txt       # Python 의존성
    ├── handler.py            # Lambda 핸들러
    └── service.py            # 비즈니스 로직
```

## 서비스별 설명

### image_orphan_cleaner

S3 버킷에서 orphan 이미지 파일들을 정리하는 서비스입니다.

**기능:**
- 2일 이상 된 파일 중 `confirmed` 태그가 없는 파일들을 삭제
- Race condition 방지를 위한 안전 마진 적용
- 매일 오전 3시(UTC) 자동 실행

**환경변수:**
- `BUCKET_NAME`: 정리할 S3 버킷 이름
- `SAFETY_MARGIN_DAYS`: 안전 마진 (일 단위, 기본값: 2)
- `ENVIRONMENT`: 실행 환경 (dev/prod)
- `PROJECT_NAME`: 프로젝트 이름

## 배포 방법

### Makefile 사용 (권장)

```bash
cd infra/workers

# 개발 환경 배포
make apply-dev

# 프로덕션 환경 배포
make apply-prod

# 사용 가능한 명령어 확인
make help
```

### 직접 SAM 명령어 사용

```bash
cd infra/workers

# 개발 환경
sam build && sam deploy

# 프로덕션 환경
sam build && sam deploy --config-env prod
```

## 로컬 테스트

```bash
cd infra/workers

# Makefile 사용
make local-invoke

# 또는 직접 SAM 명령어
sam build && sam local invoke ImageOrphanCleanupFunction
```

## 모니터링

### CloudWatch Logs
- Log Group: `/aws/lambda/challenge-image-orphan-cleanup-{environment}`
- 보존 기간: 14일

```bash
# 로그 확인
make logs-dev    # 개발 환경
make logs-prod   # 프로덕션 환경
```

### 메트릭
- 삭제된 파일 수
- 건너뛴 파일 수 (confirmed 태그)
- 에러 발생 수
- 실행 시간

### 스택 정보 확인
```bash
make info-dev    # 개발 환경 정보
make info-prod   # 프로덕션 환경 정보
```

## 환경별 차이점

| 설정 | Dev | Prod |
|------|-----|------|
| Safety Margin | 2일 | 3일 |
| Changeset 확인 | 불필요 | 필수 |
| 스케줄 | 매일 3시 | 매일 3시 |

## 주의사항

1. **버킷 이름**: 실제 S3 버킷 이름과 일치해야 함
2. **권한**: Lambda가 S3 버킷에 대한 읽기/쓰기/태그 권한 필요
3. **안전 마진**: 프로덕션에서는 더 보수적인 값 사용
4. **모니터링**: CloudWatch 알람 설정 권장
