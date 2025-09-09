.PHONY: help init plan-dev apply-dev plan-prod apply-prod destroy-dev destroy-prod

init:
	@echo "Initializing Terraform..."
	terraform init

plan-dev:
	@echo "Planning development environment..."
	terraform plan -var-file="terraform.dev.tfvars"

apply-dev:
	@echo "Applying development environment..."
	terraform apply -var-file="terraform.dev.tfvars" -auto-approve

plan-prod:
	@echo "Planning production environment..."
	terraform plan -var-file="terraform.prod.tfvars"

apply-prod:
	@echo "Applying production environment..."
	terraform apply -var-file="terraform.prod.tfvars" -auto-approve

destroy-dev:
	@echo "Destroying development environment..."
	terraform destroy -var-file="terraform.dev.tfvars" -auto-approve

destroy-prod:
	@echo "Destroying production environment..."
	terraform destroy -var-file="terraform.prod.tfvars" -auto-approve
