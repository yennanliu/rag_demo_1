"""Simple RAG (Retrieval-Augmented Generation) implementation."""

import os
import numpy as np
from pathlib import Path
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from openai import OpenAI

# Load environment variables from .env file
# This loads OPENAI_API_KEY, HF_TOKEN, and other config
load_dotenv(Path(__file__).parent / ".env")


class SimpleRAG:
    """In-memory vector store with semantic search and LLM integration."""

    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2", llm_model: str = None):
        """Initialize RAG with embeddings model and LLM client.

        Args:
            embedding_model: HuggingFace model for embeddings (default is lightweight)
            llm_model: OpenAI model to use (default: from .env or gpt-3.5-turbo)
        """
        self.embeddings_model = SentenceTransformer(embedding_model)
        self.documents = []
        self.embeddings = np.array([])

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            raise ValueError(
                "OPENAI_API_KEY not found. Please set it in .env file or environment variable."
            )

        self.client = OpenAI(api_key=api_key)
        self.llm_model = llm_model or os.environ.get("OPENAI_MODEL", "gpt-3.5-turbo")

    def add_document(self, text: str, metadata: dict = None):
        """Add a document to the knowledge base.

        Args:
            text: Document content
            metadata: Optional metadata dictionary
        """
        embedding = self.embeddings_model.encode(text, convert_to_numpy=True)
        self.documents.append({"text": text, "metadata": metadata or {}})

        if len(self.embeddings) == 0:
            self.embeddings = embedding.reshape(1, -1)
        else:
            self.embeddings = np.vstack([self.embeddings, embedding])

    def retrieve(self, query: str, top_k: int = 3) -> list[dict]:
        """Retrieve most relevant documents using semantic search.

        Args:
            query: User query
            top_k: Number of top results to return

        Returns:
            List of relevant documents with scores
        """
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
        """Generate answer using RAG pipeline.

        Args:
            query: User question
            top_k: Number of documents to retrieve

        Returns:
            Generated answer from LLM
        """
        # Retrieve relevant documents
        documents = self.retrieve(query, top_k)
        context = "\n".join([doc["text"] for doc in documents])

        # Format prompt according to RAG best practices
        prompt = f"""You are a helpful assistant.

Follow these rules:
- Use ONLY the provided context
- Be concise and factual
- If unsure, say "I don't know"
- Do not make up information

Context:
{context}

Question:
{query}

Helpful Answer:"""

        # Call LLM
        response = self.client.chat.completions.create(
            model=self.llm_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=512
        )

        return response.choices[0].message.content.strip()


def main():
    """Demo: Knowledge base about Tony Q."""
    rag = SimpleRAG()

    # Add sample documents
    docs = [
        "Tony Q is a Senior Software Engineer (SDE) with 10+ years of experience.",
        "Tony Q specializes in distributed systems and backend architecture.",
        "Tony Q's current focus is on AI-driven development tools and high-concurrency systems.",
        "Tony Q has expertise in Go, Kubernetes, and cloud infrastructure.",
        "Tony Q leads projects involving ticket systems and scalable microservices.",
    ]

    for doc in docs:
        rag.add_document(doc)

    # Test queries
    queries = [
        "Does Tony Q have experience with scaling systems?",
        "What technologies does Tony Q use?",
        "What is Tony Q's current focus?",
    ]

    print("=" * 60)
    print("RAG Demo: Knowledge Base Query")
    print("=" * 60)

    for query in queries:
        print(f"\n📝 Question: {query}")
        print("-" * 60)
        answer = rag.generate_answer(query)
        print(f"✨ Answer: {answer}")


if __name__ == "__main__":
    main()
