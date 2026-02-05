"""
LLM response generator using direct Bedrock API.
"""

import json
import boto3
from config import get_llm_config
from constants import BEDROCK_RETRY_CONFIG
from utils.logging import get_logger

logger = get_logger(__name__)

bedrock = boto3.client('bedrock-runtime', config=BEDROCK_RETRY_CONFIG)

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

CONTEXT:
{context}

Remember: You are speaking AS this person, not ABOUT them. Stick strictly to the facts provided."""


def generate_response(context: str, question: str) -> str:
    """Generate a response using Bedrock."""
    if not context:
        raise ValueError("Context cannot be empty")
    if not question:
        raise ValueError("Question cannot be empty")

    config = get_llm_config()
    prompt = SYSTEM_PROMPT.format(context=context)

    body = {
        "messages": [
            {
                "role": "user",
                "content": [{"text": f"{prompt}\n\nQuestion: {question}"}]
            }
        ],
        "inferenceConfig": {
            "temperature": config["temperature"],
            "maxTokens": config["max_tokens"]
        }
    }

    logger.info("Invoking model: %s", config["model_id"])
    response = bedrock.invoke_model(
        modelId=config["model_id"],
        body=json.dumps(body)
    )

    result = json.loads(response['body'].read())
    return result['output']['message']['content'][0]['text']
