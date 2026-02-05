"""
RAG implementation using Bedrock Knowledge Base.

Uses bedrock-agent-runtime retrieve() API for semantic search,
then generates response using the LLM.
"""

import os
import boto3
from .generator import generate_response
from utils.logging import get_logger

logger = get_logger(__name__)

bedrock_agent = boto3.client('bedrock-agent-runtime')
KNOWLEDGE_BASE_ID = os.environ.get('KNOWLEDGE_BASE_ID', '')


def retrieve_context(query: str, top_k: int = 3) -> str:
    """
    Retrieve relevant documents from Bedrock Knowledge Base.

    Args:
        query: User's question
        top_k: Number of results to retrieve

    Returns:
        Concatenated text from retrieved documents
    """
    if not KNOWLEDGE_BASE_ID:
        raise ValueError("KNOWLEDGE_BASE_ID environment variable not set")

    logger.info("Retrieving context for query: %s...", query[:50])

    response = bedrock_agent.retrieve(
        knowledgeBaseId=KNOWLEDGE_BASE_ID,
        retrievalQuery={'text': query},
        retrievalConfiguration={
            'vectorSearchConfiguration': {
                'numberOfResults': top_k
            }
        }
    )

    chunks = []
    for result in response.get('retrievalResults', []):
        text = result.get('content', {}).get('text', '')
        if text:
            chunks.append(text)

    logger.info("Retrieved %d chunks", len(chunks))
    return '\n\n---\n\n'.join(chunks)


def retrieve_and_generate(question: str) -> str:
    """
    Main RAG function: retrieve context and generate response.

    Args:
        question: User's question

    Returns:
        Generated response grounded in retrieved context
    """
    if not question:
        raise ValueError("Question cannot be empty")

    context = retrieve_context(question)

    if not context:
        logger.warning("No context retrieved for question")
        return "I don't have enough information in my knowledge base to answer that question."

    return generate_response(context, question)
