.PHONY: build deploy-dev deploy-prod apply-dev apply-prod

AWS_REGION = ap-northeast-2
STACK_NAME_DEV = challenge-workers
STACK_NAME_PROD = challenge-workers-prod


build:
	sam build

deploy-dev: build
	sam deploy

deploy-prod: build
	sam deploy --config-env prod

apply-dev: deploy-dev

apply-prod: deploy-prod
