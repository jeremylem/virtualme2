#!/usr/bin/env python3
"""
Manually populate the DynamoDB vector store.

Use this if auto-population fails or you want to force a refresh.

Usage:
    cd /Users/jeremy/Developer/Projects/virtualme
    python3 scripts/populate-vectors.py
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../src'))

os.environ['AWS_DEFAULT_REGION'] = 'eu-west-3'
os.environ['DYNAMODB_TABLE'] = os.environ.get('DYNAMODB_TABLE', 'virtual-me-v2-vectors')

from loaders.knowledge_base import load_knowledge_base
from vectorstores.dynamodb_vector_store import DynamoDBVectorStore
from rag.dynamodb_retriever import _get_embeddings

def main():
    print("=" * 80)
    print("Manual Vector Store Population")
    print("=" * 80)

    # Load documents
    print("\n1. Loading knowledge base...")
    documents = load_knowledge_base()
    print(f"   Loaded {len(documents)} documents")

    # Check metadata
    print("\n2. Checking metadata...")
    resume_count = sum(1 for doc in documents if doc.metadata.get('source_type') == 'resume')
    blog_count = sum(1 for doc in documents if doc.metadata.get('source_type') == 'blog')
    print(f"   Resume chunks: {resume_count}")
    print(f"   Blog chunks: {blog_count}")

    # Initialize vector store
    print("\n3. Connecting to DynamoDB...")
    table_name = os.environ.get('DYNAMODB_TABLE', 'virtual-me-v2-vectors')
    vector_store = DynamoDBVectorStore(
        table_name=table_name,
        region='eu-west-3'
    )

    current_count = vector_store.count()
    print(f"   Current vectors in table: {current_count}")

    if current_count > 0:
        response = input(f"\n   Table has {current_count} vectors. Clear and repopulate? (yes/no): ")
        if response.lower() != 'yes':
            print("   Aborted.")
            return
        print("   Clearing existing vectors...")
        vector_store.delete_all()

    # Get embeddings
    print("\n4. Initializing embeddings model...")
    embeddings = _get_embeddings()

    # Extract texts and metadata
    texts = [doc.page_content for doc in documents]
    metadatas = [doc.metadata for doc in documents]

    # Generate embeddings
    print("\n5. Generating embeddings (this may take 30-60 seconds)...")
    embedding_vectors = embeddings.embed_documents(texts)
    print(f"   Generated {len(embedding_vectors)} embeddings")

    # Store in DynamoDB
    print("\n6. Storing vectors in DynamoDB...")
    vector_store.add_documents(texts, embedding_vectors, metadatas)

    # Verify
    final_count = vector_store.count()
    print(f"\n✅ Complete! Vector store now has {final_count} vectors")

    print("\n" + "=" * 80)
    print("Summary")
    print("=" * 80)
    print(f"Documents loaded: {len(documents)}")
    print(f"Vectors stored: {final_count}")
    print(f"Resume chunks: {resume_count}")
    print(f"Blog chunks: {blog_count}")
    print("\nYou can now test the chatbot!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nAborted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
