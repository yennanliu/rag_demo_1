"""RAG implementation with local LLM support (optional).

Use this if you want to avoid OpenAI API costs.
Requires: pip install transformers torch

Example:
    uv add transformers torch  # Add to dependencies first
    python rag_local.py
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import numpy as np
from sentence_transformers import SentenceTransformer

# Load environment variables from .env file
# This loads HF_TOKEN for faster model downloads and higher rate limits
load_dotenv(Path(__file__).parent / ".env")


class SimpleRAGLocal:
    """RAG with local LLM using HuggingFace Transformers (no API calls)."""

    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        """Initialize RAG with local models.

        Args:
            embedding_model: HuggingFace embedding model
        """
        self.embeddings_model = SentenceTransformer(embedding_model)
        self.documents = []
        self.embeddings = np.array([])

    def add_document(self, text: str, metadata: dict = None):
        """Add a document to the knowledge base."""
        embedding = self.embeddings_model.encode(text, convert_to_numpy=True)
        self.documents.append({"text": text, "metadata": metadata or {}})

        if len(self.embeddings) == 0:
            self.embeddings = embedding.reshape(1, -1)
        else:
            self.embeddings = np.vstack([self.embeddings, embedding])

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """Retrieve most relevant documents."""
        if len(self.documents) == 0:
            return []

        query_embedding = self.embeddings_model.encode(query, convert_to_numpy=True)
        scores = np.dot(self.embeddings, query_embedding)
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            results.append({
                "text": self.documents[idx]["text"],
                "metadata": self.documents[idx]["metadata"],
                "score": float(scores[idx])
            })
        return results

    def generate_answer(self, query: str, top_k: int = 3) -> str:
        """Generate answer using retrieved context (no API calls).

        For production use with local LLM:
            pip install ollama
            ollama run qwen2:7b
        """
        documents = self.retrieve(query, top_k)

        if not documents:
            return "I don't have any documents in the knowledge base to answer your question."

        context = "\n".join([doc["text"] for doc in documents])

        # Simple template-based response (no LLM call)
        response = f"""Based on the provided context:

{context}

Answer to "{query}":
[To enable full LLM responses, set up local LLM or use the main rag.py with OpenAI API]"""

        return response


def main():
    """Demo with local RAG (no API calls)."""
    rag = SimpleRAGLocal()

    # Add documents
    docs = [
        "Python is a high-level programming language known for readability.",
        "FastAPI is a modern framework for building APIs with Python.",
        "Docker containers allow you to package applications with dependencies.",
    ]

    for doc in docs:
        rag.add_document(doc)

    # Test query
    query = "What is FastAPI?"
    print(f"Question: {query}")
    print(f"Answer: {rag.generate_answer(query)}")


if __name__ == "__main__":
    main()
