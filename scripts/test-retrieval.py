#!/usr/bin/env python3
"""
Test retrieval to debug team management issue.

Usage:
    cd /Users/jeremy/Developer/Projects/virtualme
    python3 scripts/test-retrieval.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

os.environ['AWS_DEFAULT_REGION'] = 'eu-west-3'
os.environ['DYNAMODB_TABLE'] = os.environ.get('DYNAMODB_TABLE', 'virtual-me-v2-vectors')
os.environ['LLM_BACKEND'] = 'bedrock'

from rag.dynamodb_retriever import get_retriever

def main():
    print("=" * 80)
    print("Testing Retrieval for Team Management Question")
    print("=" * 80)

    question = "Have you already managed a team?"
    print(f"\nQuestion: {question}")
    print("\n" + "-" * 80)

    # Get retriever
    retriever = get_retriever(top_k=3)

    # Test retrieval
    print("\nRetrieving documents...")
    docs = retriever.get_relevant_documents(question)

    print(f"\nRetrieved {len(docs)} documents:\n")

    for i, doc in enumerate(docs, 1):
        print(f"\n{i}. Score: {doc.metadata.get('score', 'N/A'):.4f}")
        print(f"   Source: {doc.metadata.get('source', 'unknown')}")
        print(f"   Source Type: {doc.metadata.get('source_type', 'unknown')}")
        print(f"   Content (first 200 chars):")
        print(f"   {doc.page_content[:200]}...")
        print("-" * 80)

    # Check if any resume chunks were retrieved
    resume_count = sum(1 for doc in docs if doc.metadata.get('source_type') == 'resume')
    blog_count = sum(1 for doc in docs if doc.metadata.get('source_type') == 'blog')

    print(f"\n📊 Summary:")
    print(f"   Resume chunks: {resume_count}")
    print(f"   Blog chunks: {blog_count}")

    if resume_count == 0:
        print("\n❌ PROBLEM: No resume chunks retrieved!")
        print("   This explains why the chatbot doesn't mention team management.")
    else:
        print("\n✅ Resume chunks were retrieved.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
