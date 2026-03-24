"""Simple Flask web app for interactive RAG demo."""

from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from rag import SimpleRAG
from utils import ConfigManager, ConversationManager

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")

app = Flask(__name__)

# Initialize managers
BASE_DIR = Path(__file__).parent
config_manager = ConfigManager(BASE_DIR / "config.json")
conversation_manager = ConversationManager(BASE_DIR / "conversations")

# Initialize RAG system
rag = SimpleRAG()

# Load sample documents from config
for doc in config_manager.get_sample_documents():
    rag.add_document(doc)


# ============================================================================
# PAGE ROUTES
# ============================================================================

@app.route("/")
def index():
    """Render the main page."""
    return render_template("index.html")


# ============================================================================
# DOCUMENT MANAGEMENT API
# ============================================================================

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


@app.route("/api/documents", methods=["GET"])
def get_documents():
    """Get all documents in the knowledge base."""
    return jsonify({
        "success": True,
        "documents": [doc["text"] for doc in rag.documents],
        "total": len(rag.documents)
    })


@app.route("/api/delete", methods=["POST"])
def delete_document():
    """Delete a specific document by index."""
    try:
        data = request.json
        index = data.get("index")

        if index is None or index < 0 or index >= len(rag.documents):
            return jsonify({"success": False, "error": "Invalid document index"}), 400

        # Remove document and its embedding
        import numpy as np
        rag.documents.pop(index)
        rag.embeddings = np.delete(rag.embeddings, index, axis=0)

        return jsonify({
            "success": True,
            "message": "Document deleted",
            "total_docs": len(rag.documents)
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/clear", methods=["POST"])
def clear_documents():
    """Clear all documents from the knowledge base."""
    global rag
    rag = SimpleRAG()
    return jsonify({
        "success": True,
        "message": "Knowledge base cleared"
    })


# ============================================================================
# QUERY API
# ============================================================================

@app.route("/api/query", methods=["POST"])
def query():
    """Query the RAG system."""
    try:
        data = request.json
        question = data.get("question", "").strip()

        if not question:
            return jsonify({"success": False, "error": "Question is required"}), 400

        # Get relevant documents first
        top_k = data.get("top_k", 3)
        retrieved_docs = rag.retrieve(question, top_k)

        # Generate answer
        answer = rag.generate_answer(question, top_k)

        # Extract source texts
        sources = [doc["text"] for doc in retrieved_docs]

        return jsonify({
            "success": True,
            "answer": answer,
            "sources": sources,
            "total_docs": len(rag.documents)
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# CONFIGURATION API
# ============================================================================

@app.route("/api/config", methods=["GET"])
def get_config():
    """Get current configuration."""
    config = config_manager.load()
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
        config_manager.save(new_config)
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
        for doc in config_manager.get_sample_documents():
            rag.add_document(doc)
        return jsonify({
            "success": True,
            "message": f"Reloaded {len(rag.documents)} sample documents",
            "total_docs": len(rag.documents)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# CONVERSATION HISTORY API
# ============================================================================

@app.route("/api/conversations", methods=["GET"])
def list_conversations():
    """List all saved conversations."""
    try:
        conversations = conversation_manager.list_conversations()
        return jsonify({
            "success": True,
            "conversations": conversations
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/conversations", methods=["POST"])
def save_conversation():
    """Save a conversation."""
    try:
        data = request.json
        messages = data.get("messages", [])
        name = data.get("name")

        if not messages:
            return jsonify({"success": False, "error": "No messages to save"}), 400

        conversation_id = conversation_manager.save_conversation(messages, name)

        return jsonify({
            "success": True,
            "message": "Conversation saved",
            "id": conversation_id
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/conversations/<conversation_id>", methods=["GET"])
def get_conversation(conversation_id):
    """Get a specific conversation."""
    try:
        conversation = conversation_manager.load_conversation(conversation_id)
        return jsonify({
            "success": True,
            "conversation": conversation
        })
    except FileNotFoundError:
        return jsonify({"success": False, "error": "Conversation not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/conversations/<conversation_id>", methods=["DELETE"])
def delete_conversation(conversation_id):
    """Delete a conversation."""
    try:
        success = conversation_manager.delete_conversation(conversation_id)
        if success:
            return jsonify({
                "success": True,
                "message": "Conversation deleted"
            })
        else:
            return jsonify({"success": False, "error": "Conversation not found"}), 404
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/conversations/export", methods=["GET"])
def export_conversations():
    """Export all conversations."""
    try:
        data = conversation_manager.export_all()
        return jsonify({
            "success": True,
            "data": data
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/api/conversations/import", methods=["POST"])
def import_conversations():
    """Import conversations."""
    try:
        data = request.json
        count = conversation_manager.import_conversations(data)
        return jsonify({
            "success": True,
            "message": f"Imported {count} conversations"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 RAG Demo Web App")
    print("=" * 60)
    print(f"📚 Loaded {len(rag.documents)} sample documents")
    print("🌐 Open: http://localhost:5000")
    print("=" * 60)
    app.run(debug=True, host="0.0.0.0", port=5000)
