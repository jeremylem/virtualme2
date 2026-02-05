"""
Reusable validation helpers for Pydantic models.
"""


def validate_not_empty_whitespace(value: str, strip: bool = True) -> str:
    """
    Validate that a string is not empty or whitespace-only.

    Args:
        value: String to validate
        strip: Whether to strip whitespace and return stripped value

    Returns:
        Stripped value if strip=True, otherwise original value

    Raises:
        ValueError: If value is empty or whitespace-only
    """
    stripped = value.strip()
    if not stripped:
        raise ValueError("Text cannot be empty or whitespace only")
    return stripped if strip else value


def validate_no_null_bytes(value: str) -> str:
    """
    Validate that a string contains no null bytes.

    Args:
        value: String to validate

    Returns:
        Original value if valid

    Raises:
        ValueError: If value contains null bytes
    """
    if '\x00' in value:
        raise ValueError("Text cannot contain null bytes")
    return value
