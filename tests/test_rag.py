"""Unit tests for RAG core functionality."""

import pytest
import numpy as np
from rag import SimpleRAG


class TestSimpleRAG:
    """Test cases for SimpleRAG class."""

    def test_initialization(self):
        """Test RAG initialization."""
        rag = SimpleRAG()
        assert rag.documents == []
        assert len(rag.embeddings) == 0
        assert rag.embeddings_model is not None
        assert rag.client is not None

    def test_add_single_document(self):
        """Test adding a single document."""
        rag = SimpleRAG()
        doc_text = "Python is a programming language."

        rag.add_document(doc_text)

        assert len(rag.documents) == 1
        assert rag.documents[0]["text"] == doc_text
        assert rag.embeddings.shape[0] == 1

    def test_add_multiple_documents(self):
        """Test adding multiple documents."""
        rag = SimpleRAG()
        docs = [
            "Python is a programming language.",
            "JavaScript is used for web development.",
            "SQL is for database queries."
        ]

        for doc in docs:
            rag.add_document(doc)

        assert len(rag.documents) == 3
        assert rag.embeddings.shape[0] == 3

    def test_add_document_with_metadata(self):
        """Test adding document with metadata."""
        rag = SimpleRAG()
        doc_text = "Test document"
        metadata = {"source": "test", "category": "demo"}

        rag.add_document(doc_text, metadata)

        assert rag.documents[0]["text"] == doc_text
        assert rag.documents[0]["metadata"] == metadata

    def test_retrieve_with_empty_knowledge_base(self):
        """Test retrieval with no documents."""
        rag = SimpleRAG()
        results = rag.retrieve("test query")

        assert results == []

    def test_retrieve_returns_relevant_documents(self):
        """Test that retrieve returns documents with scores."""
        rag = SimpleRAG()
        docs = [
            "Python is a programming language.",
            "The weather is sunny today.",
            "JavaScript is used for web development."
        ]

        for doc in docs:
            rag.add_document(doc)

        # Query about programming
        results = rag.retrieve("programming languages", top_k=2)

        assert len(results) <= 2
        assert all("text" in r for r in results)
        assert all("score" in r for r in results)
        assert all("metadata" in r for r in results)

    def test_retrieve_top_k_parameter(self):
        """Test that top_k parameter limits results."""
        rag = SimpleRAG()
        docs = ["Doc " + str(i) for i in range(10)]

        for doc in docs:
            rag.add_document(doc)

        results = rag.retrieve("Doc", top_k=3)

        assert len(results) == 3

    def test_embeddings_shape_consistency(self):
        """Test that embeddings maintain correct shape."""
        rag = SimpleRAG()

        rag.add_document("First document")
        shape_1 = rag.embeddings.shape

        rag.add_document("Second document")
        shape_2 = rag.embeddings.shape

        assert shape_1[1] == shape_2[1]  # Same embedding dimension
        assert shape_2[0] == shape_1[0] + 1  # One more document

    def test_custom_embedding_model(self):
        """Test initialization with custom embedding model."""
        # Test with same model but explicit parameter
        rag = SimpleRAG(embedding_model="all-MiniLM-L6-v2")
        assert rag.embeddings_model is not None

    @pytest.mark.llm
    def test_generate_answer_integration(self, run_llm):
        """Integration test for answer generation (requires API key)."""
        if not run_llm:
            pytest.skip("Skipping LLM tests (use --run-llm to enable)")
        rag = SimpleRAG()
        docs = [
            "Python is a high-level programming language.",
            "Python was created by Guido van Rossum.",
            "Python is known for its readability and simplicity."
        ]

        for doc in docs:
            rag.add_document(doc)

        answer = rag.generate_answer("What is Python?")

        assert isinstance(answer, str)
        assert len(answer) > 0
