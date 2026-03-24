"""Example usage of the RAG system with different scenarios."""

import os
from rag import SimpleRAG


def example_employee_directory():
    """Example: Employee directory knowledge base."""
    print("\n" + "=" * 60)
    print("Example 1: Employee Directory RAG")
    print("=" * 60)

    rag = SimpleRAG()

    # Build knowledge base
    employees = [
        "Alice Chen is a Product Manager with expertise in AI/ML products.",
        "Bob Smith is a Full-Stack Engineer specializing in cloud infrastructure.",
        "Carol Wang is a DevOps Engineer with 8 years of Kubernetes experience.",
        "David Lee is a Data Scientist focusing on recommendation systems.",
        "Eve Johnson is a Security Engineer working on infrastructure security.",
    ]

    for emp in employees:
        rag.add_document(emp)

    # Query the knowledge base
    question = "Who has expertise in AI/ML?"
    print(f"\n❓ Question: {question}")
    print("-" * 60)
    answer = rag.generate_answer(question)
    print(f"✅ Answer: {answer}")


def example_product_docs():
    """Example: Product documentation."""
    print("\n" + "=" * 60)
    print("Example 2: Product Documentation RAG")
    print("=" * 60)

    rag = SimpleRAG()

    # Product documentation
    docs = [
        "Our API supports REST and GraphQL endpoints for data queries.",
        "Authentication is handled via OAuth 2.0 with JWT tokens.",
        "Rate limits: 100 requests per minute for free tier, unlimited for pro.",
        "Webhooks are supported for event notifications like order updates.",
        "SDKs are available for Python, JavaScript, Go, and Java.",
    ]

    for doc in docs:
        rag.add_document(doc)

    # Query
    question = "How do I authenticate with your API?"
    print(f"\n❓ Question: {question}")
    print("-" * 60)
    answer = rag.generate_answer(question)
    print(f"✅ Answer: {answer}")


def example_with_metadata():
    """Example: Using metadata for better organization."""
    print("\n" + "=" * 60)
    print("Example 3: RAG with Metadata")
    print("=" * 60)

    rag = SimpleRAG()

    # Add documents with metadata
    rag.add_document(
        "React is a JavaScript library for building user interfaces.",
        metadata={"source": "frontend", "category": "framework"}
    )
    rag.add_document(
        "FastAPI is a modern Python framework for building APIs.",
        metadata={"source": "backend", "category": "framework"}
    )
    rag.add_document(
        "PostgreSQL is a relational database system.",
        metadata={"source": "database", "category": "storage"}
    )

    question = "What JavaScript library should I use?"
    print(f"\n❓ Question: {question}")
    print("-" * 60)
    answer = rag.generate_answer(question)
    print(f"✅ Answer: {answer}")


if __name__ == "__main__":
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY environment variable not set")
        print("Please set it before running: export OPENAI_API_KEY='your-key'\n")
    else:
        try:
            example_employee_directory()
            example_product_docs()
            example_with_metadata()
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("\nMake sure:")
            print("1. OPENAI_API_KEY is set correctly")
            print("2. Dependencies are installed: uv sync")
