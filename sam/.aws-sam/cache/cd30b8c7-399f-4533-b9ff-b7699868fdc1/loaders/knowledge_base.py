"""
Knowledge base loader for Virtual Me chatbot.

Handles loading and splitting markdown files from the knowledge_base directory
while maintaining context hierarchy from markdown headers.

Supports multiple .md files for organizing different types of content:
- resume.md: Professional experience
- skills.md: Technical skills
- projects.md: Project descriptions
- etc.
"""

from pathlib import Path
from typing import List
from langchain_text_splitters import MarkdownHeaderTextSplitter
from langchain_core.documents import Document

from constants import KNOWLEDGE_BASE_DIR, RESUME_PATH, MARKDOWN_HEADERS_TO_SPLIT
from utils.logging import get_logger

logger = get_logger(__name__)


def load_knowledge_base() -> List[Document]:
    """
    Load and split all markdown files from the knowledge base directory.

    Falls back to legacy resume.md location if knowledge_base directory
    doesn't exist (backward compatibility).

    Uses MarkdownHeaderTextSplitter to maintain hierarchical context
    from markdown headers (#, ##, ###).

    Returns:
        List of Document objects with content and metadata

    Raises:
        FileNotFoundError: If no knowledge base files found
        IOError: If files cannot be read

    Example:
        >>> docs = load_knowledge_base()
        >>> len(docs)
        15
        >>> docs[0].metadata
        {'Header 1': 'John Doe', 'Header 2': 'Experience', 'source': 'resume.md'}
    """
    all_documents: List[Document] = []

    # Check for knowledge_base directory first
    if KNOWLEDGE_BASE_DIR.exists() and KNOWLEDGE_BASE_DIR.is_dir():
        md_files = list(KNOWLEDGE_BASE_DIR.glob("*.md"))

        if not md_files:
            raise FileNotFoundError(
                f"No markdown files found in {KNOWLEDGE_BASE_DIR}. "
                f"Add .md files to the knowledge_base directory."
            )

        logger.info("Loading %d markdown files from %s", len(md_files), KNOWLEDGE_BASE_DIR)

        for md_file in sorted(md_files):
            docs = _load_markdown_file(md_file)
            all_documents.extend(docs)

    # Fall back to legacy single resume.md
    elif RESUME_PATH.exists():
        logger.info("Using legacy resume.md location")
        all_documents = _load_markdown_file(RESUME_PATH)

    else:
        raise FileNotFoundError(
            f"No knowledge base found. Either:\n"
            f"  1. Create {KNOWLEDGE_BASE_DIR}/ with .md files, or\n"
            f"  2. Create {RESUME_PATH}"
        )

    logger.info("Loaded knowledge base: %d total chunks", len(all_documents))
    return all_documents


def _load_markdown_file(file_path: Path) -> List[Document]:
    """
    Load and split a single markdown file.

    Args:
        file_path: Path to the markdown file

    Returns:
        List of Document objects with source metadata
    """
    try:
        content = file_path.read_text(encoding='utf-8')
    except IOError as e:
        raise IOError(f"Failed to read {file_path}: {e}")

    # Split the markdown maintaining header context
    markdown_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=MARKDOWN_HEADERS_TO_SPLIT,
        strip_headers=False
    )

    splits = markdown_splitter.split_text(content)

    # Add source file and source type to metadata
    for doc in splits:
        doc.metadata['source'] = file_path.name
        # Tag resume files vs blog posts for better retrieval
        doc.metadata['source_type'] = 'resume' if 'resume' in file_path.name.lower() else 'blog'

    logger.info("Loaded %s: %d chunks", file_path.name, len(splits))
    return splits
