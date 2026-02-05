.PHONY: build deploy deploy-frontend deploy-all validate logs logs-api clean delete help

# Default target
help:
	@echo "Virtual Me v2 - SAM Deployment Commands"
	@echo ""
	@echo "  make build           - Build Lambda function with container"
	@echo "  make deploy          - Deploy SAM stack (first time: use 'sam deploy --guided')"
	@echo "  make deploy-frontend - Sync frontend files to S3 and invalidate CloudFront"
	@echo "  make deploy-all      - Build, deploy stack, and deploy frontend"
	@echo "  make validate        - Validate SAM template"
	@echo "  make logs            - Tail Lambda function logs"
	@echo "  make logs-api        - Tail API Gateway logs"
	@echo "  make clean           - Remove build artifacts"
	@echo "  make delete          - Delete the entire SAM stack"
	@echo ""

# Build Lambda function using container for consistent Linux binaries
build:
	sam build --use-container

# Deploy SAM stack (assumes samconfig.toml is configured)
deploy:
	sam deploy

# Deploy with guided prompts (first-time deployment)
deploy-guided:
	sam deploy --guided

# Deploy frontend files to S3
deploy-frontend:
	./scripts/deploy-frontend.sh

# Full deployment: build, deploy stack, deploy frontend
deploy-all: build deploy deploy-frontend

# Validate SAM template
validate:
	sam validate --lint

# Tail Lambda function logs
logs:
	sam logs -n VirtualMeFunction --stack-name virtual-me-v2 --tail

# Tail API Gateway logs
logs-api:
	aws logs tail /aws/apigateway/virtual-me-v2-api-prod --follow

# Remove build artifacts
clean:
	rm -rf .aws-sam

# Delete the entire SAM stack (careful!)
delete:
	@echo "WARNING: This will delete all resources in the virtual-me-v2 stack!"
	@read -p "Are you sure? [y/N] " confirm && [ "$$confirm" = "y" ] || exit 1
	sam delete --stack-name virtual-me-v2

# Show stack outputs
outputs:
	aws cloudformation describe-stacks \
		--stack-name virtual-me-v2 \
		--query 'Stacks[0].Outputs' \
		--output table

# Show stack status
status:
	aws cloudformation describe-stacks \
		--stack-name virtual-me-v2 \
		--query 'Stacks[0].StackStatus' \
		--output text
