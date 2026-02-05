"""
Virtual Me Chatbot - AWS Lambda Handler

Main entry point for the Lambda function. Delegates to the RAG pipeline.
"""

import json
from typing import Dict, Any
from pydantic import ValidationError

from rag.pipeline import run_rag_pipeline
from utils.http import http_response
from utils.logging import get_logger
from models.requests import ChatRequest, ErrorResponse
from constants import MIN_REMAINING_TIME_MS, CONVERSATION_TRUNCATE_LIMIT

logger = get_logger(__name__)


def is_meta_question(question: str) -> bool:
    """
    Detect if question is about the chatbot itself (meta question).

    Meta questions ask about how THIS chatbot works, not about Jeremy's projects.

    Args:
        question: User's question text

    Returns:
        True if this is a meta question about the chatbot
    """
    question_lower = question.lower()

    # Keywords that indicate asking about the chatbot itself
    meta_indicators = [
        'how were you built',
        'how were you implemented',
        'how have you been built',
        'how have you been implemented',
        'tell me how you have been implemented',
        'tell me how you were built',
        'how does this chatbot work',
        'how does this work',
        'what technology powers you',
        'what powers you',
        'how are you implemented',
        'what are you built with',
        'what stack are you using',
        'how do you work',
        'explain how you work',
        'what technology are you using'
    ]

    return any(indicator in question_lower for indicator in meta_indicators)


def get_meta_response() -> str:
    """
    Return canned response for meta questions about the chatbot.

    Returns:
        Explanation of how Virtual Me chatbot works
    """
    return (
        "I'm Virtual Me, a RAG-powered chatbot representing Jeremy Lemaire. "
        "I'm built with AWS Lambda, DynamoDB vector store, LangGraph orchestration, "
        "and Amazon Bedrock (Nova 2 Lite model). When you ask a question, I retrieve "
        "relevant sections from Jeremy's resume using semantic search, then generate "
        "grounded responses to prevent hallucinations. The full technical breakdown "
        "is in Jeremy's blog post about this project."
    )


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main AWS Lambda handler function.

    Processes POST requests from Deep Chat frontend with conversation history.
    Extracts the latest user message and runs it through the RAG pipeline.

    Args:
        event: API Gateway event containing request data
        context: Lambda context object

    Returns:
        HTTP response with AI-generated answer

    Example event:
        {
            'body': '{"messages": [{"role": "user", "text": "Hello"}]}',
            'requestContext': {'http': {'method': 'POST'}}
        }
    """

    # Handle CORS preflight requests
    if event.get('requestContext', {}).get('http', {}).get('method') == 'OPTIONS':
        return http_response(200, {'message': 'OK'})

    try:
        # Parse and validate request body
        body = json.loads(event.get('body', '{}'))

        # Validate request with Pydantic
        try:
            chat_request = ChatRequest(**body)
        except ValidationError as e:
            # Return detailed validation errors
            error_response = ErrorResponse(
                error="Invalid request format",
                details=e.errors()
            )
            return http_response(422, error_response.model_dump())

        # Truncate conversation to last N messages (silently drop older ones)
        messages = chat_request.messages
        if len(messages) > CONVERSATION_TRUNCATE_LIMIT:
            logger.info("Truncating conversation from %d to %d messages", len(messages), CONVERSATION_TRUNCATE_LIMIT)
            messages = messages[-CONVERSATION_TRUNCATE_LIMIT:]

        # Extract the last user message
        last_user_message = messages[-1].text

        logger.info("Processing question: %s...", last_user_message[:100])

        # Check if this is a meta question about the chatbot itself
        if is_meta_question(last_user_message):
            logger.info("Detected meta question - bypassing RAG pipeline")
            answer = get_meta_response()
        else:
            # Check remaining execution time before starting expensive RAG pipeline
            if context is not None:
                remaining_ms = context.get_remaining_time_in_millis()
                if remaining_ms < MIN_REMAINING_TIME_MS:
                    logger.warning("Insufficient time remaining: %dms < %dms", remaining_ms, MIN_REMAINING_TIME_MS)
                    error_response = ErrorResponse(
                        error="Insufficient time remaining for request processing"
                    )
                    return http_response(503, error_response.model_dump())

            # Run the RAG pipeline
            answer = run_rag_pipeline(last_user_message)

        logger.info("Generated answer (%d chars)", len(answer))

        # Format response for Deep Chat
        response_body = {
            'text': answer
        }

        return http_response(200, response_body)

    except json.JSONDecodeError as e:
        logger.warning("Invalid JSON: %s", e)
        error_response = ErrorResponse(error="Invalid JSON in request body")
        return http_response(400, error_response.model_dump())

    except ValueError as e:
        logger.warning("Validation error: %s", e)
        error_response = ErrorResponse(error=str(e))
        return http_response(400, error_response.model_dump())

    except Exception:
        logger.exception("Unexpected error in lambda handler")
        error_response = ErrorResponse(error="Internal server error")
        return http_response(500, error_response.model_dump())


# ============================================================================
# LOCAL TESTING
# ============================================================================

if __name__ == "__main__":
    """
    Local testing script. Set OPENAI_API_KEY environment variable before running.

    Usage:
        export OPENAI_API_KEY="sk-proj-xxx"
        cd src
        python lambda_function.py
    """
    print("=" * 60)
    print("Virtual Me Chatbot - Local Test")
    print("=" * 60)

    # Mock event for testing
    test_event = {
        'body': json.dumps({
            'messages': [
                {'role': 'user', 'text': 'What is your main area of expertise?'}
            ]
        }),
        'requestContext': {
            'http': {'method': 'POST'}
        }
    }

    print("\nProcessing test request...")
    response = lambda_handler(test_event, None)

    print("\n" + "=" * 60)
    print("Test Response")
    print("=" * 60)
    print(f"Status Code: {response['statusCode']}")
    print(f"\nBody:")
    print(json.dumps(json.loads(response['body']), indent=2))
    print("=" * 60)
