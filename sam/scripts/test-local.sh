#!/bin/bash
# Test local Lambda with sample API Gateway V2 request

QUESTION="${1:-What is your expertise?}"

curl -s -X POST http://127.0.0.1:7000/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "version": "2.0",
    "routeKey": "POST /chat",
    "rawPath": "/chat",
    "rawQueryString": "",
    "headers": {"content-type": "application/json"},
    "requestContext": {
      "accountId": "123456789",
      "apiId": "test",
      "domainName": "localhost",
      "domainPrefix": "test",
      "http": {
        "method": "POST",
        "path": "/chat",
        "protocol": "HTTP/1.1",
        "sourceIp": "127.0.0.1",
        "userAgent": "curl"
      },
      "requestId": "test-123",
      "routeKey": "POST /chat",
      "stage": "prod",
      "time": "05/Feb/2026:00:00:00 +0000",
      "timeEpoch": 1770000000000
    },
    "body": "{\"messages\":[{\"role\":\"user\",\"text\":\"'"$QUESTION"'\"}]}",
    "isBase64Encoded": false
  }' | jq
