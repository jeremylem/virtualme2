#!/bin/bash
#
# Deploy frontend files to S3 and invalidate CloudFront cache
#
# This script:
# 1. Gets the S3 bucket name and CloudFront distribution ID from CloudFormation
# 2. Replaces API_ENDPOINT_PLACEHOLDER with the actual API endpoint
# 3. Syncs index.html (with replaced placeholder) and deepChat.bundle.js to S3
# 4. Creates a CloudFront invalidation to clear the cache
#

set -euo pipefail

STACK_NAME="${STACK_NAME:-virtual-me-v2}"
FRONTEND_DIR="${FRONTEND_DIR:-../frontend}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
FRONTEND_PATH="${PROJECT_ROOT}/frontend"

echo "==> Fetching stack outputs from ${STACK_NAME}..."

# Get outputs from CloudFormation
BUCKET_NAME=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --query 'Stacks[0].Outputs[?OutputKey==`FrontendBucketName`].OutputValue' \
    --output text)

DISTRIBUTION_ID=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --query 'Stacks[0].Outputs[?OutputKey==`CloudFrontDistributionId`].OutputValue' \
    --output text)

API_ENDPOINT=$(aws cloudformation describe-stacks \
    --stack-name "${STACK_NAME}" \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiEndpoint`].OutputValue' \
    --output text)

if [[ -z "${BUCKET_NAME}" || -z "${DISTRIBUTION_ID}" || -z "${API_ENDPOINT}" ]]; then
    echo "ERROR: Could not retrieve stack outputs. Is the stack deployed?"
    echo "  Bucket: ${BUCKET_NAME:-<missing>}"
    echo "  Distribution: ${DISTRIBUTION_ID:-<missing>}"
    echo "  API Endpoint: ${API_ENDPOINT:-<missing>}"
    exit 1
fi

echo "  Bucket: ${BUCKET_NAME}"
echo "  Distribution: ${DISTRIBUTION_ID}"
echo "  API Endpoint: ${API_ENDPOINT}"

# Create temp directory for processed files
TEMP_DIR=$(mktemp -d)
trap "rm -rf ${TEMP_DIR}" EXIT

echo ""
echo "==> Processing index.html (replacing API_ENDPOINT_PLACEHOLDER)..."

# Replace placeholder in index.html
sed "s|API_ENDPOINT_PLACEHOLDER|${API_ENDPOINT}|g" \
    "${FRONTEND_PATH}/index.html" > "${TEMP_DIR}/index.html"

echo "  Placeholder replaced with: ${API_ENDPOINT}"

echo ""
echo "==> Syncing files to S3..."

# Upload index.html with correct content type
aws s3 cp "${TEMP_DIR}/index.html" "s3://${BUCKET_NAME}/index.html" \
    --content-type "text/html" \
    --cache-control "max-age=300"

# Upload deepChat.bundle.js
aws s3 cp "${FRONTEND_PATH}/deepChat.bundle.js" "s3://${BUCKET_NAME}/deepChat.bundle.js" \
    --content-type "application/javascript" \
    --cache-control "max-age=86400"

echo "  Uploaded: index.html"
echo "  Uploaded: deepChat.bundle.js"

echo ""
echo "==> Creating CloudFront invalidation..."

INVALIDATION_ID=$(aws cloudfront create-invalidation \
    --distribution-id "${DISTRIBUTION_ID}" \
    --paths "/*" \
    --query 'Invalidation.Id' \
    --output text)

echo "  Invalidation ID: ${INVALIDATION_ID}"
echo "  Note: Invalidation may take a few minutes to complete"

echo ""
echo "==> Frontend deployment complete!"
echo ""
echo "  Frontend URL: https://chat.lemaire.tel"
echo "  API Endpoint: ${API_ENDPOINT}"
