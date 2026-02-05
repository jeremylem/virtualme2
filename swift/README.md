# Virtual Me Swift Lambda

Swift implementation of the Virtual Me chatbot using AWS Lambda Runtime v2.

## Build & Deploy

```bash
cd sam

# Build
make build

# Deploy
make deploy

# Run locally
make run-local

# Test local (in another terminal)
make test-local
```

## Environment Variables

- `KNOWLEDGE_BASE_ID`: Bedrock Knowledge Base ID
- `LLM_MODEL`: Model alias (nova-2-lite, nova-2-pro)
- `LLM_TEMPERATURE`: Temperature for generation (default: 0.1)

## Dependencies

- `swift-aws-lambda-runtime` v2.5.3
- `soto` v7.12.0 (AWS SDK for Swift)
