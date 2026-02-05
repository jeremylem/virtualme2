"""
Configuration constants for Virtual Me chatbot.
"""

from botocore.config import Config

# --- LLM ---

DEFAULT_LLM_MODEL = "nova-2-lite"
DEFAULT_TEMPERATURE = 0.1
DEFAULT_MAX_TOKENS = 2048

# --- Message limits ---

MAX_MESSAGE_LENGTH = 5000
MAX_CONVERSATION_LENGTH = 100
CONVERSATION_TRUNCATE_LIMIT = 20
CONVERSATION_WARNING_THRESHOLD = 15

# --- AWS ---

DEFAULT_AWS_REGION = "eu-west-3"
MIN_REMAINING_TIME_MS = 10000

BEDROCK_RETRY_CONFIG = Config(
    retries={'max_attempts': 3, 'mode': 'adaptive'}
)

# --- HTTP ---

CONTENT_TYPE = "application/json"
ALLOWED_ORIGINS = ["https://chat2.lemaire.tel"]
ALLOWED_METHODS = ["OPTIONS", "POST"]
ALLOWED_HEADERS = ["content-type"]
