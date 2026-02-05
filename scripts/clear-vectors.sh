#!/bin/bash
#
# Clear all vectors from DynamoDB to force re-indexing
# Usage: ./scripts/clear-vectors.sh
#

set -e

TABLE_NAME="${DYNAMODB_TABLE:-virtual-me-v2-vectors}"
REGION="${AWS_REGION:-eu-west-3}"

echo "Clearing vectors from DynamoDB table: $TABLE_NAME (region: $REGION)"

# Get count before
COUNT=$(aws dynamodb scan --table-name "$TABLE_NAME" --region "$REGION" --select COUNT --query 'Count' --output text 2>/dev/null || echo "0")
echo "Current vector count: $COUNT"

if [ "$COUNT" -eq 0 ]; then
    echo "Table is already empty."
    exit 0
fi

# Confirm
read -p "Delete all $COUNT vectors? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

# Delete all items
echo "Deleting vectors..."
aws dynamodb scan --table-name "$TABLE_NAME" --region "$REGION" \
    --projection-expression "id" \
    --query 'Items[*].id.S' --output text | \
    tr '\t' '\n' | \
    while read -r id; do
        if [ -n "$id" ]; then
            aws dynamodb delete-item \
                --table-name "$TABLE_NAME" \
                --region "$REGION" \
                --key "{\"id\":{\"S\":\"$id\"}}" \
                --no-cli-pager
            echo -n "."
        fi
    done

echo ""
echo "Done. Vectors will be re-indexed on next Lambda invocation."
