.PHONY: build-dev build-prod deploy-dev deploy-prod delete-dev delete-prod

build-dev:
	sam build --config-env dev

build-prod:
	sam build --config-env prod

deploy-dev:
	sam build --config-env dev
	sam deploy --config-env dev

deploy-prod:
	sam build --config-env prod
	sam deploy --config-env prod

delete-dev:
	sam delete --config-env dev --no-prompts

delete-prod:
	sam delete --config-env prod --no-prompts
