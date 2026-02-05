"""
DynamoDB-based retriever for semantic search over the knowledge base.
"""

import os
from functools import lru_cache
from typing import List
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from config import get_embedding_config
from constants import RAG_TOP_K_CHUNKS, DEFAULT_AWS_REGION, BEDROCK_RETRY_CONFIG
from utils.logging import get_logger
from vectorstores.dynamodb_vector_store import DynamoDBVectorStore
from loaders.knowledge_base import load_knowledge_base

logger = get_logger(__name__)


@lru_cache(maxsize=1)
def _get_embeddings() -> Embeddings:
    """Get or create embeddings instance (cached)."""
    config = get_embedding_config()

    try:
        from langchain_aws import BedrockEmbeddings
    except ImportError:
        raise ImportError("langchain-aws not installed")

    logger.info("Using Bedrock embeddings: %s", config["model_id"])

    return BedrockEmbeddings(
        model_id=config["model_id"],
        region_name=config["aws_region"],
        config=BEDROCK_RETRY_CONFIG
    )


def _populate_vector_store(vector_store: DynamoDBVectorStore) -> None:
    """Load knowledge base docs into an empty vector store."""
    documents = load_knowledge_base()
    logger.info("Loaded %d documents", len(documents))

    embeddings = _get_embeddings()
    texts = [doc.page_content for doc in documents]
    metadatas = [doc.metadata for doc in documents]

    logger.info("Generating embeddings...")
    embedding_vectors = embeddings.embed_documents(texts)

    logger.info("Storing in DynamoDB...")
    vector_store.add_documents(texts, embedding_vectors, metadatas)
    logger.info("Stored %d vectors", len(texts))


@lru_cache(maxsize=1)
def _initialize_vector_store() -> DynamoDBVectorStore:
    """Create vector store, populating it if empty (cached)."""
    table_name = os.environ.get('DYNAMODB_TABLE', 'virtual-me-vectors-prod')
    region = os.environ.get('AWS_DEFAULT_REGION', DEFAULT_AWS_REGION)

    logger.info("Initializing vector store (table: %s, region: %s)", table_name, region)
    vector_store = DynamoDBVectorStore(table_name=table_name, region=region)

    count = vector_store.count()
    logger.info("Vector store has %d vectors", count)

    if count == 0:
        error_msg = (
            "Vector store is empty! Please populate it manually:\n"
            "  cd /Users/jeremy/Developer/Projects/virtualme\n"
            "  python3 scripts/populate-vectors.py\n"
            "Auto-population is disabled because it times out and produces incomplete results (133 vs 145 expected)."
        )
        logger.error(error_msg)
        raise RuntimeError(error_msg)
    elif count < 145:
        logger.warning(
            "Vector store has only %d vectors (expected 145). "
            "This may cause incorrect answers. Run populate-vectors.py to fix.",
            count
        )
    else:
        logger.info("Vector store ready with %d vectors", count)

    return vector_store


def get_retriever(top_k: int = RAG_TOP_K_CHUNKS) -> "DynamoDBRetriever":
    """Get retriever instance."""
    return DynamoDBRetriever(_initialize_vector_store(), _get_embeddings(), top_k)


class DynamoDBRetriever:
    """Wraps DynamoDB vector store with LangChain-compatible interface."""

    def __init__(self, vector_store: DynamoDBVectorStore, embeddings: Embeddings, top_k: int = 3):
        self.vector_store = vector_store
        self.embeddings = embeddings
        self.top_k = top_k

    def get_relevant_documents(self, query: str) -> List[Document]:
        """
        Find the most relevant documents for a query.

        Fetches more candidates than needed and re-ranks to prioritize resume content
        when the query appears to be about personal experience/skills.
        """
        query_embedding = self.embeddings.embed_query(query)

        # Fetch 2-3x more candidates for re-ranking
        fetch_k = self.top_k * 3
        results = self.vector_store.similarity_search(query_embedding, k=fetch_k)

        # Re-rank: boost resume chunks for personal questions
        query_lower = query.lower()
        is_personal_question = any(keyword in query_lower for keyword in [
            'you', 'your', 'experience', 'background', 'manage', 'lead', 'led',
            'team', 'skills', 'certifications', 'education', 'projects', 'worked'
        ])

        if is_personal_question:
            # Boost resume chunks by adding bonus to their score
            boosted_results = []
            for text, score, metadata in results:
                boost = 0.15 if metadata.get('source_type') == 'resume' else 0.0
                boosted_results.append((text, score + boost, metadata))

            # Re-sort by boosted score
            boosted_results.sort(key=lambda x: x[1], reverse=True)
            results = boosted_results[:self.top_k]
        else:
            # Use original ranking for non-personal questions
            results = results[:self.top_k]

        return [
            Document(
                page_content=text,
                metadata={**metadata, "score": score}
            )
            for text, score, metadata in results
        ]


def reset_retriever() -> None:
    """Clear cached retriever (for testing or after knowledge base update)."""
    global _vector_store, _embeddings
    _vector_store = None
    _embeddings = None
    logger.info("Retriever cache cleared")
