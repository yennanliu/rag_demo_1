"""Simple Flask web app for interactive RAG demo."""

import json
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from rag import SimpleRAG

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")

app = Flask(__name__)

# Config file path
CONFIG_FILE = Path(__file__).parent / "config.json"


def load_config():
    """Load configuration from config.json."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {"sample_documents": []}


def save_config(config):
    """Save configuration to config.json."""
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)


# Initialize RAG system
rag = SimpleRAG()

# Load and add sample documents from config
config = load_config()
for doc in config.get("sample_documents", []):
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


@app.route("/api/config", methods=["GET"])
def get_config():
    """Get current configuration."""
    config = load_config()
    return jsonify({
        "success": True,
        "config": config
    })


@app.route("/api/config", methods=["POST"])
def update_config():
    """Update configuration."""
    try:
        data = request.json
        new_config = data.get("config", {})
        save_config(new_config)
        return jsonify({
            "success": True,
            "message": "Configuration saved successfully"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/reload", methods=["POST"])
def reload_samples():
    """Reload sample documents from config."""
    global rag
    try:
        rag = SimpleRAG()
        config = load_config()
        for doc in config.get("sample_documents", []):
            rag.add_document(doc)
        return jsonify({
            "success": True,
            "message": f"Reloaded {len(rag.documents)} sample documents",
            "total_docs": len(rag.documents)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    print("=" * 60)
    print("🚀 RAG Demo Web App")
    print("=" * 60)
    print(f"📚 Loaded {len(rag.documents)} sample documents")
    print("🌐 Open: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
