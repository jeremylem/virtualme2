"""
Pydantic models for request/response validation.

Uses Pydantic v2 for comprehensive input validation and type safety.
Prevents common security issues like injection attacks and oversized payloads.
"""

from typing import List, Literal
from pydantic import BaseModel, Field, field_validator, ConfigDict

from constants import (
    MAX_MESSAGE_LENGTH,
    MAX_CONVERSATION_LENGTH,
    CONVERSATION_WARNING_THRESHOLD
)
from utils.validation import validate_not_empty_whitespace, validate_no_null_bytes


class Message(BaseModel):
    """
    Single message in a conversation.

    Validates:
    - Role is either 'user' or 'ai'
    - Text is non-empty and within limits
    - No XSS vectors in text
    """

    role: Literal["user", "ai"] = Field(
        ...,
        description="Message role (user or ai)",
        examples=["user", "ai"]
    )

    text: str = Field(
        ...,
        min_length=1,
        max_length=MAX_MESSAGE_LENGTH,
        description="Message text content",
        examples=["What is your experience with Python?"]
    )

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate text is not empty and has no null bytes."""
        v = validate_not_empty_whitespace(v)
        return validate_no_null_bytes(v)

    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "example": {
                "role": "user",
                "text": "What programming languages do you know?"
            }
        }
    )


class ChatRequest(BaseModel):
    """
    Chat request from frontend.

    Validates:
    - At least one message present
    - Maximum 50 messages (conversation history limit)
    - Last message is from user
    """

    messages: List[Message] = Field(
        ...,
        min_length=1,
        max_length=MAX_CONVERSATION_LENGTH,
        description="List of conversation messages",
        examples=[[
            {"role": "user", "text": "Hello"},
            {"role": "ai", "text": "Hi there!"},
            {"role": "user", "text": "Tell me about yourself"}
        ]]
    )

    @field_validator('messages')
    @classmethod
    def validate_last_message_is_user(cls, v: List[Message]) -> List[Message]:
        """Ensure last message is from user."""
        if not v:
            raise ValueError("Messages list cannot be empty")

        if v[-1].role != 'user':
            raise ValueError(
                "Last message must be from user. "
                f"Got: {v[-1].role}"
            )

        return v

    @field_validator('messages')
    @classmethod
    def validate_reasonable_history(cls, v: List[Message]) -> List[Message]:
        """Warn about very long conversation histories."""
        if len(v) > CONVERSATION_WARNING_THRESHOLD:
            # Log warning but allow (for monitoring)
            import logging
            logging.getLogger(__name__).warning(
                f"Long conversation history detected: {len(v)} messages "
                f"(threshold: {CONVERSATION_WARNING_THRESHOLD})"
            )

        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "messages": [
                    {"role": "user", "text": "What is your main expertise?"}
                ]
            }
        }
    )


class ChatResponse(BaseModel):
    """
    Chat response to frontend.

    Ensures response is non-empty and within limits.
    """

    text: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="AI-generated response text",
        examples=["I'm a Senior Software Engineer with 8+ years of experience..."]
    )

    @field_validator('text')
    @classmethod
    def validate_text(cls, v: str) -> str:
        """Validate response is not empty."""
        return validate_not_empty_whitespace(v, strip=False)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "text": "I'm a Senior Software Engineer with expertise in Python, AWS, and distributed systems."
            }
        }
    )


class ErrorResponse(BaseModel):
    """
    Error response model.

    Used for validation errors and other client errors.
    """

    error: str = Field(
        ...,
        description="Error message",
        examples=["Invalid request: message text too long"]
    )

    details: List[dict] | None = Field(
        None,
        description="Detailed validation errors (optional)",
        examples=[[
            {
                "loc": ["messages", 0, "text"],
                "msg": "String should have at most 5000 characters",
                "type": "string_too_long"
            }
        ]]
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "error": "Invalid request",
                "details": [
                    {
                        "loc": ["messages", 0, "text"],
                        "msg": "String should have at most 5000 characters",
                        "type": "string_too_long"
                    }
                ]
            }
        }
    )
