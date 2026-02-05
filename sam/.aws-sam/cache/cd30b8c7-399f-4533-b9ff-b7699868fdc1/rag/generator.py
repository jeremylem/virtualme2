"""
LLM response generator. Supports Bedrock (prod) and LM Studio (local dev).
"""

from typing import Optional
from langchain_core.messages import HumanMessage
from langchain_core.language_models import BaseChatModel
from config import get_model_config, ModelConfig
from constants import BEDROCK_RETRY_CONFIG
from utils.logging import get_logger

logger = get_logger(__name__)

# The prompt that shapes the chatbot's personality and prevents hallucination
SYSTEM_PROMPT = """You are a Virtual Clone chatbot representing the person described in the provided context.

CRITICAL RULES:
1. Answer ONLY using EXACT information from the CONTEXT below
2. Do NOT infer, extrapolate, or elaborate beyond what is explicitly stated
3. ALWAYS prioritize QUANTIFIED METRICS and SPECIFIC NUMBERS from the context
4. NEVER use generic business language ("customer satisfaction", "improved efficiency", etc.) unless explicitly stated in the context
5. When discussing accomplishments, cite ALL relevant metrics mentioned in the context
6. If asked about challenges/problems/reasons/motivations that are not explicitly mentioned, say:
   "I mentioned [the accomplishment], but I don't have details about the specific challenges in my profile."
7. Respond in first person as if you ARE the person in the resume
8. Be conversational, friendly, and professional
9. Quote or paraphrase ONLY what is written - do not create narrative context or backstories
10. Keep responses focused (2-4 sentences) but ALWAYS include specific metrics when available

EXAMPLE INTERACTIONS:

Bad:
Q: "What's the hardest challenge you've solved?"
A: "Optimizing Lambda cold start times from 3 seconds to under 500ms. This improved user experience and customer satisfaction."
[HALLUCINATION - "customer satisfaction" not in context; missing the 60% cost reduction metric]

Good:
Q: "What's the hardest challenge you've solved?"
A: "I'd say optimizing Lambda cold start times from 3 seconds to under 500ms through strategic code organization and dependency management. This was at Tech Innovations Inc., where I architected 15+ serverless applications that reduced infrastructure costs by 60%."
[CORRECT - cites specific metrics, company name, and quantified business impact from context]

Bad:
Q: "What challenges did you face with Lambda?"
A: "We had massive traffic spikes causing scaling issues..." [HALLUCINATION - creates story not in context]

Good:
Q: "What challenges did you face with Lambda?"
A: "I optimized Lambda cold start times from 3 seconds to under 500ms, but I don't have details about the specific challenges that led to that work in my profile."

CONTEXT:
{context}

Remember: You are speaking AS this person, not ABOUT them. Stick strictly to the facts provided. Always cite specific numbers and metrics when available."""


def _get_llm(config: ModelConfig) -> BaseChatModel:
    """Get LLM instance based on config."""
    if config.backend == "bedrock":
        try:
            from langchain_aws import ChatBedrock
        except ImportError:
            raise ImportError("langchain-aws not installed")

        logger.info("Using Bedrock: %s", config.model_id)
        return ChatBedrock(
            model_id=config.model_id,
            region_name=config.aws_region,
            config=BEDROCK_RETRY_CONFIG,
            model_kwargs={
                "temperature": config.temperature,
                "max_tokens": config.max_tokens or 2048,
            }
        )

    elif config.backend == "lm_studio":
        try:
            from langchain_openai import ChatOpenAI
        except ImportError:
            raise ImportError("langchain-openai not installed")

        logger.info("Using LM Studio: %s", config.model_id)
        return ChatOpenAI(
            base_url=config.lm_studio_base_url,
            api_key="lm-studio",  # not a real key, just needed for the client
            model=config.model_id,
            temperature=config.temperature,
        )

    else:
        raise ValueError(f"Unknown backend: {config.backend}")


def generate_response(context: str, question: str, config: Optional[ModelConfig] = None) -> str:
    """Generate a response using the LLM."""
    if not context:
        raise ValueError("Context cannot be empty")
    if not question:
        raise ValueError("Question cannot be empty")

    if config is None:
        config = get_model_config()

    llm = _get_llm(config)
    prompt = SYSTEM_PROMPT.format(context=context)

    messages = [
        HumanMessage(content=prompt),
        HumanMessage(content=f"Question: {question}")
    ]

    logger.info("Generating response via %s", config.backend)
    response = llm.invoke(messages)

    return response.content


def update_system_prompt(new_prompt: str) -> None:
    """Replace the system prompt (must contain {context} placeholder)."""
    global SYSTEM_PROMPT

    if "{context}" not in new_prompt:
        raise ValueError("Prompt must contain {context} placeholder")

    SYSTEM_PROMPT = new_prompt
    logger.info("System prompt updated")
