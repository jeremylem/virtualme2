"""
Configuration constants for Virtual Me chatbot.
"""

from pathlib import Path
from botocore.config import Config

# --- Paths ---

SRC_DIR = Path(__file__).parent
KNOWLEDGE_BASE_DIR = SRC_DIR / "knowledge_base"
PROMPTS_DIR = SRC_DIR / "prompts"
RESUME_PATH = SRC_DIR / "resume.md"  # legacy, kept for compatibility

# --- LLM ---

DEFAULT_LLM_MODEL = "nova-2-lite"
DEFAULT_TEMPERATURE = 0.1  # low = more factual, less hallucination
DEFAULT_MAX_TOKENS = 2048

# --- Message limits ---

MAX_MESSAGE_LENGTH = 5000  # max characters per individual message
MAX_CONVERSATION_LENGTH = 100  # reject requests with too many messages (prevents abuse)
CONVERSATION_TRUNCATE_LIMIT = 20  # only use last N messages (keeps context window manageable, reduces token cost)
CONVERSATION_WARNING_THRESHOLD = 15  # log warning above this threshold for monitoring

# --- RAG ---

RAG_TOP_K_CHUNKS = 3  # retrieve top 3 most similar chunks (balances context quality vs token cost)

MARKDOWN_HEADERS_TO_SPLIT = [
    ("#", "Header 1"),
    ("##", "Header 2"),
    ("###", "Header 3"),
]

# --- AWS ---

DEFAULT_AWS_REGION = "eu-west-3"

# If Lambda has less than 10s left, return 503 so client can retry
MIN_REMAINING_TIME_MS = 10000

# --- CORS ---

ALLOWED_ORIGINS = ["https://chat.lemaire.tel"]
ALLOWED_METHODS = ["OPTIONS", "POST"]
ALLOWED_HEADERS = ["content-type"]
CORS_MAX_AGE = 300

# --- HTTP ---

CONTENT_TYPE = "application/json"
DEBUG_MODE = False

# --- Retry configs ---

BEDROCK_RETRY_CONFIG = Config(
    retries={'max_attempts': 3, 'mode': 'adaptive'}
)

DYNAMODB_RETRY_CONFIG = Config(
    retries={'max_attempts': 3, 'mode': 'adaptive'}
)
