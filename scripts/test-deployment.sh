#!/bin/bash
###############################################################################
# Test Deployed Lambda Function
###############################################################################

set -e

API_ENDPOINT="${1:-https://api2.lemaire.tel/chat}"

echo "=========================================="
echo "Testing Virtual Me Deployment"
echo "=========================================="
echo ""
echo "API Endpoint: $API_ENDPOINT"
echo ""

# Test 1: Simple query
echo "Test 1: Simple query..."
RESPONSE=$(curl -s -X POST "$API_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "user", "text": "What is your main expertise?"}
    ]
  }')

echo "Response:"
echo "$RESPONSE" | jq .

# Check if response contains expected data
if echo "$RESPONSE" | jq -e '.text' > /dev/null 2>&1; then
    echo "✅ Test 1 PASSED: Got valid response"
else
    echo "❌ Test 1 FAILED: Invalid response format"
    exit 1
fi

echo ""

# Test 2: Error handling
echo "Test 2: Error handling (empty message)..."
ERROR_RESPONSE=$(curl -s -X POST "$API_ENDPOINT" \
  -H "Content-Type: application/json" \
  -d '{"messages": []}')

echo "Response:"
echo "$ERROR_RESPONSE" | jq .

if echo "$ERROR_RESPONSE" | jq -e '.error' > /dev/null 2>&1; then
    echo "✅ Test 2 PASSED: Error handling works"
else
    echo "⚠️  Test 2: Expected error response"
fi

echo ""
echo "=========================================="
echo "Testing Complete!"
echo "=========================================="
echo ""
echo "View logs:"
echo "  aws logs tail /aws/lambda/virtual-me-v2-prod --follow"
echo ""
echo "View X-Ray traces:"
echo "  AWS Console → X-Ray → Traces"
echo ""
