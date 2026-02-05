"""
LangGraph state definition for RAG workflow.
"""

from typing import TypedDict, Annotated, Sequence
from operator import add
from langchain_core.messages import BaseMessage


class GraphState(TypedDict):
    """
    Represents the state of the RAG conversation graph.

    Attributes:
        messages: The conversation history (list of BaseMessage)
        context: Retrieved relevant documents from vector store (formatted string)
        question: The current user question (string)

    Example:
        >>> state = GraphState(
        ...     messages=[],
        ...     context="I have 8 years experience...",
        ...     question="What is your experience?"
        ... )
    """
    messages: Annotated[Sequence[BaseMessage], add]
    context: str
    question: str
