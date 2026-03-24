"""Simple Flask web app for interactive RAG demo."""

from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from rag import SimpleRAG

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")

app = Flask(__name__)

# Initialize RAG system
rag = SimpleRAG()

# Pre-load some sample documents
SAMPLE_DOCS = [
    "Tony Q is a Senior Software Engineer with 10+ years of experience in distributed systems.",
    "Tony Q specializes in backend architecture and high-concurrency ticket systems.",
    "Tony Q's expertise includes Go, Kubernetes, and cloud infrastructure.",
]

for doc in SAMPLE_DOCS:
    rag.add_document(doc)


@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")


@app.route("/api/add", methods=["POST"])
def add_document():
    """Add a new document to the knowledge base."""
    try:
        data = request.json
        text = data.get("text", "").strip()

        if not text:
            return jsonify({"success": False, "error": "Document text is required"}), 400

        rag.add_document(text)
        return jsonify({
            "success": True,
            "message": "Document added successfully",
            "total_docs": len(rag.documents)
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/query", methods=["POST"])
def query():
    """Query the RAG system."""
    try:
        data = request.json
        question = data.get("question", "").strip()

        if not question:
            return jsonify({"success": False, "error": "Question is required"}), 400

        answer = rag.generate_answer(question)
        return jsonify({
            "success": True,
            "answer": answer,
            "total_docs": len(rag.documents)
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/documents", methods=["GET"])
def get_documents():
    """Get all documents in the knowledge base."""
    return jsonify({
        "success": True,
        "documents": [doc["text"] for doc in rag.documents],
        "total": len(rag.documents)
    })


@app.route("/api/clear", methods=["POST"])
def clear_documents():
    """Clear all documents from the knowledge base."""
    global rag
    rag = SimpleRAG()
    return jsonify({
        "success": True,
        "message": "Knowledge base cleared"
    })


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 RAG Demo Web App")
    print("=" * 60)
    print(f"📚 Loaded {len(rag.documents)} sample documents")
    print("🌐 Open: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
