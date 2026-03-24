"""Simple Flask web app for interactive RAG demo."""

from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from flasgger import Swagger
from rag import SimpleRAG
from utils import ConfigManager, ConversationManager
import json

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")

app = Flask(__name__)

# Configure Swagger
swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": "apispec",
            "route": "/apispec.json",
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api/docs"
}

swagger_template = {
    "info": {
        "title": "RAG Demo API",
        "description": "API documentation for the Simple RAG Demo application",
        "version": "0.1.0",
        "contact": {
            "name": "RAG Demo",
        }
    },
    "schemes": ["http", "https"],
}

swagger = Swagger(app, config=swagger_config, template=swagger_template)

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


@app.route("/visualizations")
def visualizations():
    """Render the visualizations page."""
    return render_template("visualizations.html")


# ============================================================================
# DOCUMENT MANAGEMENT API
# ============================================================================

@app.route("/api/add", methods=["POST"])
def add_document():
    """Add a new document to the knowledge base.
    ---
    tags:
      - Documents
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - text
          properties:
            text:
              type: string
              description: The document text to add
              example: "Python is a programming language"
    responses:
      200:
        description: Document added successfully
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            total_docs:
              type: integer
      400:
        description: Invalid request
      500:
        description: Server error
    """
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
    """Get all documents in the knowledge base.
    ---
    tags:
      - Documents
    responses:
      200:
        description: List of all documents
        schema:
          type: object
          properties:
            success:
              type: boolean
            documents:
              type: array
              items:
                type: string
            total:
              type: integer
    """
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
    """Query the RAG system with a question.
    ---
    tags:
      - Query
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - question
          properties:
            question:
              type: string
              description: The question to ask
              example: "What is Python?"
            top_k:
              type: integer
              description: Number of documents to retrieve
              default: 3
              example: 3
    responses:
      200:
        description: Query successful
        schema:
          type: object
          properties:
            success:
              type: boolean
            answer:
              type: string
            sources:
              type: array
              items:
                type: string
      400:
        description: Invalid request
      500:
        description: Server error
    """
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
    """Get current configuration.
    ---
    tags:
      - Configuration
    responses:
      200:
        description: Current configuration
        schema:
          type: object
          properties:
            success:
              type: boolean
            config:
              type: object
    """
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
    """List all saved conversations.
    ---
    tags:
      - Conversations
    responses:
      200:
        description: List of conversations
        schema:
          type: object
          properties:
            success:
              type: boolean
            conversations:
              type: array
              items:
                type: object
    """
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
    """Save a conversation.
    ---
    tags:
      - Conversations
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required:
            - messages
          properties:
            messages:
              type: array
              items:
                type: object
              description: Array of conversation messages
            name:
              type: string
              description: Optional name for the conversation
    responses:
      200:
        description: Conversation saved
        schema:
          type: object
          properties:
            success:
              type: boolean
            message:
              type: string
            id:
              type: string
      400:
        description: Invalid request
    """
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
# VISUALIZATION API
# ============================================================================

@app.route("/api/visualizations/data", methods=["GET"])
def get_visualization_data():
    """Get visualization data for knowledge base.
    ---
    tags:
      - Visualizations
    responses:
      200:
        description: Visualization data
        schema:
          type: object
          properties:
            success:
              type: boolean
            embeddings_2d:
              type: array
              description: 2D projection of document embeddings using t-SNE
            embeddings_3d:
              type: array
              description: 3D projection of document embeddings using t-SNE
            similarity_matrix:
              type: array
              description: Cosine similarity matrix between documents
            documents:
              type: array
              description: Document texts
            stats:
              type: object
              description: Statistics about the knowledge base
    """
    try:
        import numpy as np
        from sklearn.manifold import TSNE
        from sklearn.decomposition import PCA

        if len(rag.documents) == 0:
            return jsonify({
                "success": True,
                "message": "No documents in knowledge base",
                "embeddings_2d": [],
                "embeddings_3d": [],
                "similarity_matrix": [],
                "documents": [],
                "stats": {
                    "total_documents": 0,
                    "embedding_dimension": 0
                }
            })

        embeddings = rag.embeddings
        num_docs = len(rag.documents)

        # Compute 2D projection using t-SNE or PCA
        if num_docs >= 3:
            # Use PCA first to reduce dimensions if needed
            if embeddings.shape[1] > 50:
                pca = PCA(n_components=50)
                embeddings_reduced = pca.fit_transform(embeddings)
            else:
                embeddings_reduced = embeddings

            # t-SNE for 2D visualization
            perplexity = min(30, num_docs - 1) if num_docs > 1 else 1
            tsne_2d = TSNE(n_components=2, perplexity=perplexity, random_state=42)
            embeddings_2d = tsne_2d.fit_transform(embeddings_reduced).tolist()

            # t-SNE for 3D visualization
            tsne_3d = TSNE(n_components=3, perplexity=perplexity, random_state=42)
            embeddings_3d = tsne_3d.fit_transform(embeddings_reduced).tolist()
        elif num_docs == 2:
            # For 2 documents, just use first 2 dimensions
            embeddings_2d = embeddings[:, :2].tolist()
            embeddings_3d = np.column_stack([embeddings[:, :2], np.zeros(2)]).tolist()
        else:
            # Single document
            embeddings_2d = [[0, 0]]
            embeddings_3d = [[0, 0, 0]]

        # Compute cosine similarity matrix
        normalized = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        similarity_matrix = np.dot(normalized, normalized.T).tolist()

        # Get document texts (truncate for display)
        documents = [
            {
                "text": doc["text"][:100] + ("..." if len(doc["text"]) > 100 else ""),
                "full_text": doc["text"],
                "index": i
            }
            for i, doc in enumerate(rag.documents)
        ]

        # Compute statistics
        stats = {
            "total_documents": num_docs,
            "embedding_dimension": embeddings.shape[1],
            "avg_document_length": np.mean([len(doc["text"]) for doc in rag.documents]),
            "max_document_length": max([len(doc["text"]) for doc in rag.documents]),
            "min_document_length": min([len(doc["text"]) for doc in rag.documents]),
        }

        return jsonify({
            "success": True,
            "embeddings_2d": embeddings_2d,
            "embeddings_3d": embeddings_3d,
            "similarity_matrix": similarity_matrix,
            "documents": documents,
            "stats": stats
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
