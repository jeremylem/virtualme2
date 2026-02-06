.PHONY: build deploy deploy-frontend deploy-all validate logs logs-api clean delete help upload-kb start-ingestion ingest ingestion-status run-local test-local cold-start-metrics memory-metrics

# Default target
help:
	@echo "Virtual Me v2 - SAM Deployment Commands"
	@echo ""
	@echo "  make build           - Build Swift Lambda function"
	@echo "  make run-local       - Run Lambda locally (swift run)"
	@echo "  make test-local      - Test local Lambda with sample request"
	@echo "  make deploy          - Deploy SAM stack"
	@echo "  make deploy-frontend - Sync frontend files to S3 and invalidate CloudFront"
	@echo "  make deploy-all      - Build, deploy stack, and deploy frontend"
	@echo "  make validate        - Validate SAM template"
	@echo "  make logs            - Tail Lambda function logs"
	@echo "  make logs-api        - Tail API Gateway logs"
	@echo "  make cold-start-metrics - Show cold start statistics"
	@echo "  make memory-metrics  - Show memory usage statistics"
	@echo "  make clean           - Remove build artifacts"
	@echo "  make delete          - Delete the entire SAM stack"
	@echo ""
	@echo "Knowledge Base:"
	@echo "  make upload-kb       - Upload knowledge base files to S3"
	@echo "  make start-ingestion - Start Bedrock KB ingestion job"
	@echo "  make ingest          - Upload KB and trigger ingestion"
	@echo "  make ingestion-status - Check ingestion job status"
	@echo ""

# Build Swift Lambda using AWS Lambda Swift plugin
build:
	cd ../swift && swift package --disable-sandbox plugin archive --allow-network-connections all

# Run Lambda locally for development
run-local:
	cd ../swift && LOCAL_LAMBDA_SERVER_INVOCATION_PORT=7001 KNOWLEDGE_BASE_ID=RPXCA7UUQN LLM_MODEL=nova-2-lite LLM_TEMPERATURE=0.1 swift run

# Test local Lambda with sample request (run-local must be running)
test-local:
	./scripts/test-local.sh

# Deploy SAM stack (requires sam build for nested stacks)
deploy:
	sam build && sam deploy

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
	aws logs tail /aws/apigateway/virtual-me-v2-api --follow

# Remove build artifacts
clean:
	rm -rf .aws-sam ../swift/.build

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

# Upload knowledge base files to S3
upload-kb:
	@KB_BUCKET=$$(aws cloudformation describe-stacks --stack-name virtual-me-v2 --query 'Stacks[0].Outputs[?OutputKey==`KnowledgeBaseBucketName`].OutputValue' --output text) && \
	echo "Uploading to s3://$$KB_BUCKET/knowledge_base/" && \
	aws s3 sync ../knowledge_base/ s3://$$KB_BUCKET/knowledge_base/

# Start Bedrock Knowledge Base ingestion job
start-ingestion:
	@KB_ID=$$(aws cloudformation describe-stacks --stack-name virtual-me-v2 --query 'Stacks[0].Outputs[?OutputKey==`KnowledgeBaseId`].OutputValue' --output text) && \
	DS_COMPOSITE=$$(aws cloudformation describe-stacks --stack-name virtual-me-v2 --query 'Stacks[0].Outputs[?OutputKey==`DataSourceId`].OutputValue' --output text) && \
	DS_ID=$${DS_COMPOSITE##*|} && \
	echo "Starting ingestion for KB: $$KB_ID, DataSource: $$DS_ID" && \
	aws bedrock-agent start-ingestion-job --knowledge-base-id $$KB_ID --data-source-id $$DS_ID

# Upload KB and trigger ingestion
ingest: upload-kb start-ingestion

# Check ingestion job status
ingestion-status:
	@KB_ID=$$(aws cloudformation describe-stacks --stack-name virtual-me-v2 --query 'Stacks[0].Outputs[?OutputKey==`KnowledgeBaseId`].OutputValue' --output text) && \
	DS_COMPOSITE=$$(aws cloudformation describe-stacks --stack-name virtual-me-v2 --query 'Stacks[0].Outputs[?OutputKey==`DataSourceId`].OutputValue' --output text) && \
	DS_ID=$${DS_COMPOSITE##*|} && \
	aws bedrock-agent list-ingestion-jobs --knowledge-base-id $$KB_ID --data-source-id $$DS_ID --query 'ingestionJobSummaries[0]' --output table

# Show cold start metrics from CloudWatch Logs
cold-start-metrics:
	@echo "Fetching cold start metrics from last 7 days..."
	@QUERY_ID=$$(aws logs start-query \
		--log-group-name /aws/lambda/virtual-me-v2 \
		--start-time $$(date -u -v-7d +%s) \
		--end-time $$(date -u +%s) \
		--query-string 'fields @initDuration, @duration, @memorySize | filter @type = "REPORT" and ispresent(@initDuration) | stats avg(@initDuration) as avgColdStart, max(@initDuration) as maxColdStart, min(@initDuration) as minColdStart, pct(@initDuration, 50) as p50ColdStart, pct(@initDuration, 99) as p99ColdStart, count() as totalColdStarts' \
		--query 'queryId' --output text) && \
	sleep 3 && \
	aws logs get-query-results --query-id $$QUERY_ID --output table

# Show memory usage metrics from CloudWatch Logs
memory-metrics:
	@echo "Fetching memory usage from last 7 days..."
	@QUERY_ID=$$(aws logs start-query \
		--log-group-name /aws/lambda/virtual-me-v2 \
		--start-time $$(date -u -v-7d +%s) \
		--end-time $$(date -u +%s) \
		--query-string 'fields @timestamp, @memorySize, @maxMemoryUsed | filter @type = "REPORT" | stats avg(@maxMemoryUsed) as avgMemoryUsed, max(@maxMemoryUsed) as maxMemoryUsed, min(@maxMemoryUsed) as minMemoryUsed, avg(@memorySize) as allocatedMemory' \
		--query 'queryId' --output text) && \
	sleep 3 && \
	aws logs get-query-results --query-id $$QUERY_ID --output table
