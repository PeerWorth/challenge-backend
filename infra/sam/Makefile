# SAM 배포를 위한 Makefile
# 불필요한 파일들을 제외하고 깔끔하게 빌드

.PHONY: clean-build build-prod deploy-prod

# 빌드 전 정리
clean-build:
	@echo "Cleaning build directory..."
	rm -rf .aws-sam/build

# 프로덕션 빌드 (의존성은 Layer에서 처리)
build-prod: clean-build
	@echo "Creating temporary build directory with only application code..."
	@rm -rf ../../.tmp_build_src
	@mkdir -p ../../.tmp_build_src
	@cp ../../main.py ../../.tmp_build_src/
	@cp ../../__init__.py ../../.tmp_build_src/
	@cp -r ../../app ../../.tmp_build_src/
	@echo "Temporarily updating CodeUri to use clean source..."
	@sed -i.bak 's|CodeUri: ../../|CodeUri: ../../.tmp_build_src/|' template.yaml
	@echo "Building SAM application..."
	sam build --config-env prod
	@echo "Restoring original template and cleaning up..."
	@mv template.yaml.bak template.yaml
	@rm -rf ../../.tmp_build_src

# 프로덕션 배포
deploy-prod: build-prod
	@echo "Deploying to production..."
	sam deploy --stack-name challenge-backend-prod \
		--region ap-northeast-2 \
		--capabilities CAPABILITY_IAM \
		--parameter-overrides Environment=prod \
		--resolve-s3

# 개발 환경 빌드
build-dev: clean-build
	@echo "Moving requirements.txt temporarily..."
	@if [ -f ../../requirements.txt ]; then \
		mv ../../requirements.txt ../../requirements.txt.backup; \
	fi
	@echo "Building SAM application..."
	sam build --config-env dev
	@echo "Restoring requirements.txt..."
	@if [ -f ../../requirements.txt.backup ]; then \
		mv ../../requirements.txt.backup ../../requirements.txt; \
	fi

# 개발 환경 배포
deploy-dev: build-dev
	@echo "Deploying to development..."
	sam deploy --config-env dev
