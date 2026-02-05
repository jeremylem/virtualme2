"""
DynamoDB Vector Store for RAG
Stores document embeddings in DynamoDB and performs similarity search
"""

import json
import struct
import hashlib
from typing import List, Tuple, Optional
import boto3

from constants import DEFAULT_AWS_REGION, DYNAMODB_RETRY_CONFIG
from utils.logging import get_logger

logger = get_logger(__name__)


class DynamoDBVectorStore:
    """
    Vector store using DynamoDB for persistence.
    Stores text chunks with their embeddings and performs cosine similarity search.
    """

    def __init__(self, table_name: str, region: str = DEFAULT_AWS_REGION):
        """
        Initialize DynamoDB vector store.

        Args:
            table_name: Name of DynamoDB table
            region: AWS region (defaults to DEFAULT_AWS_REGION from constants)
        """
        self.table_name = table_name
        self.region = region
        self.dynamodb = boto3.resource('dynamodb', region_name=region, config=DYNAMODB_RETRY_CONFIG)
        self.table = self.dynamodb.Table(table_name)

    @staticmethod
    def _embedding_to_binary(embedding: List[float]) -> bytes:
        """Convert embedding list to binary format for efficient storage."""
        return struct.pack(f'{len(embedding)}f', *embedding)

    @staticmethod
    def _binary_to_embedding(binary: bytes) -> List[float]:
        """Convert binary back to embedding list."""
        num_floats = len(binary) // 4
        return list(struct.unpack(f'{num_floats}f', binary))

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        dot_product = sum(x * y for x, y in zip(a, b))
        magnitude_a = sum(x * x for x in a) ** 0.5
        magnitude_b = sum(x * x for x in b) ** 0.5

        if magnitude_a == 0 or magnitude_b == 0:
            return 0.0

        return dot_product / (magnitude_a * magnitude_b)

    @staticmethod
    def _generate_doc_id(text: str, index: int) -> str:
        """
        Generate deterministic document ID using SHA256.

        Args:
            text: Document text content
            index: Document index in the batch

        Returns:
            Deterministic ID in format 'doc_{index}_{hash}'
        """
        content_hash = hashlib.sha256(text.encode('utf-8')).hexdigest()[:12]
        return f"doc_{index}_{content_hash}"

    def add_documents(self, texts: List[str], embeddings: List[List[float]], metadatas: Optional[List[dict]] = None) -> None:
        """
        Add documents with embeddings to DynamoDB.

        Args:
            texts: List of text chunks
            embeddings: List of embedding vectors
            metadatas: Optional list of metadata dicts
        """
        if metadatas is None:
            metadatas = [{}] * len(texts)

        with self.table.batch_writer() as batch:
            for i, (text, embedding, metadata) in enumerate(zip(texts, embeddings, metadatas)):
                item = {
                    'id': self._generate_doc_id(text, i),
                    'text': text,
                    'embedding': self._embedding_to_binary(embedding),
                    'metadata': json.dumps(metadata)
                }
                batch.put_item(Item=item)

        logger.info("Added %d documents to DynamoDB table %s", len(texts), self.table_name)

    def similarity_search(self, query_embedding: List[float], k: int = 3, max_items: int = 1000) -> List[Tuple[str, float]]:
        """
        Find k most similar documents using cosine similarity.

        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            max_items: Maximum items to scan (safety limit, default 1000)

        Returns:
            List of (text, similarity_score) tuples
        """
        items = []
        response = self.table.scan()
        items.extend(response.get('Items', []))

        # Handle pagination with early termination at max_items
        while 'LastEvaluatedKey' in response and len(items) < max_items:
            response = self.table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))

        # Truncate to max_items if exceeded
        items = items[:max_items]

        # Calculate similarities
        results = []
        for item in items:
            doc_embedding = self._binary_to_embedding(item['embedding'].value)
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            # Parse metadata JSON string to dict
            import json
            metadata = json.loads(item.get('metadata', '{}'))
            results.append((item['text'], similarity, metadata))

        # Sort by similarity (highest first) and return top k with metadata
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:k]

    def delete_all(self) -> None:
        """Delete all items from the table (useful for reset)."""
        response = self.table.scan()
        items = response.get('Items', [])

        with self.table.batch_writer() as batch:
            for item in items:
                batch.delete_item(Key={'id': item['id']})

        logger.info("Deleted all items from %s", self.table_name)

    def count(self) -> int:
        """Return number of documents in the store."""
        response = self.table.scan(Select='COUNT')
        return response.get('Count', 0)
