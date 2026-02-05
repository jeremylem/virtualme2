"""
RAG pipeline using LangGraph. Retrieves context then generates response.
"""

from functools import lru_cache
from typing import Dict, List
from langchain_core.messages import AIMessage
from langchain_core.documents import Document
from langgraph.graph import StateGraph, END
from langgraph.graph.state import CompiledStateGraph

from .state import GraphState
from .dynamodb_retriever import get_retriever
from .generator import generate_response
from utils.logging import get_logger

logger = get_logger(__name__)


def retrieve_node(state: GraphState) -> Dict[str, str]:
    """Fetch relevant documents from the vector store."""
    question = state["question"]

    retriever = get_retriever()
    documents: List[Document] = retriever.get_relevant_documents(question)
    context = format_context(documents)

    logger.info("Retrieved %d documents", len(documents))
    return {"context": context}


def generate_node(state: GraphState) -> Dict[str, List[AIMessage]]:
    """Generate response using the LLM."""
    response_text = generate_response(state["context"], state["question"])
    return {"messages": [AIMessage(content=response_text)]}


def format_context(documents: List[Document]) -> str:
    """Combine documents into a single context string."""
    return "\n\n".join([
        f"Section: {doc.metadata.get('Header 2', 'N/A')}\n{doc.page_content}"
        for doc in documents
    ])


def build_graph() -> CompiledStateGraph:
    """Build the RAG workflow: retrieve -> generate -> done."""
    workflow = StateGraph(GraphState)

    workflow.add_node("retrieve", retrieve_node)
    workflow.add_node("generate", generate_node)

    workflow.set_entry_point("retrieve")
    workflow.add_edge("retrieve", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()


# Cached graph instance
@lru_cache(maxsize=1)
def get_graph() -> CompiledStateGraph:
    """Get compiled graph (cached for Lambda cold start)."""
    logger.info("Building graph...")
    graph = build_graph()
    logger.info("Graph ready")
    return graph


def run_rag_pipeline(question: str) -> str:
    """
    Main entry point. Takes a question, returns an answer.

    Retrieves relevant context from knowledge base, then generates response.
    """
    if not question:
        raise ValueError("Question cannot be empty")

    initial_state: GraphState = {
        "messages": [],
        "context": "",
        "question": question
    }

    graph = get_graph()
    result = graph.invoke(initial_state)

    ai_messages = result.get("messages", [])
    if not ai_messages:
        raise Exception("No response generated")

    return ai_messages[-1].content
