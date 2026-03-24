# Simple RAG Demo

A minimal, elegant Retrieval-Augmented Generation (RAG) system using Python with an in-memory vector store.

**✨ New: Interactive web interface for easy demos!**

👉 See [QUICKSTART.md](QUICKSTART.md) for a quick 3-step setup guide.

## Features

- **🌐 Interactive web interface** - Beautiful UI for demos and experimentation
- **Simple in-memory vector database** - No external DB setup required
- **Semantic search** - Uses sentence transformers for embeddings
- **LLM integration** - OpenAI API for answer generation
- **Clean prompt engineering** - Following RAG best practices from the docs
- **Minimal dependencies** - Flask, OpenAI, sentence-transformers, and numpy

## Setup

### 1. Install UV (if not already installed)

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and install dependencies

```bash
cd /Users/jerryliu/rag_demo_1
uv sync
```

### 3. Configure environment variables

Copy the example env file:

```bash
cp .env.example .env
```

Edit `.env` and add your keys:

```bash
# Required: OpenAI API key
OPENAI_API_KEY=sk-xxxxxxxxxxxxx

# Optional: Use a different OpenAI model
OPENAI_MODEL=gpt-3.5-turbo

# Optional: HuggingFace token for faster model downloads
# Get from: https://huggingface.co/settings/tokens
HF_TOKEN=hf_xxxxxxxxxxxxx
```

The project automatically loads all variables from `.env` when running.

## Usage

### 🌐 Web App (Recommended)

Launch the interactive web interface:

```bash
uv run python app.py
```

Then open http://localhost:5000 in your browser.

**Features:**
- Add documents to the knowledge base in real-time
- Ask questions and get AI-powered answers
- View all documents in the knowledge base
- Clear and reset the knowledge base
- Clean, modern UI with instant feedback

**Keyboard shortcuts:**
- `Ctrl+Enter` in document field: Add document
- `Ctrl+Enter` in question field: Ask question

### 📟 Command Line

**Quick Start:**

```bash
uv run python rag.py
```

This runs the demo with Tony Q's employee profile.

**Run Examples:**

```bash
uv run python example.py
```

Includes 3 different scenarios:
- Employee directory
- Product documentation
- Using metadata for organization

### Use in Your Code

```python
from rag import SimpleRAG

# Create RAG instance
rag = SimpleRAG()

# Add documents to knowledge base
rag.add_document("Your document text here")
rag.add_document("Another document", metadata={"source": "api-docs"})

# Query the knowledge base
answer = rag.generate_answer("Your question here")
print(answer)
```

## How It Works

1. **Indexing**: Documents are converted to embeddings using `sentence-transformers`
2. **Retrieval**: User query is embedded, then top-k similar documents are found using cosine similarity
3. **Generation**: Retrieved documents are formatted into a prompt following RAG best practices
4. **LLM Call**: The prompt is sent to GPT-3.5-turbo for answer generation

## Architecture

```
User Query
    ↓
Embedding Model
    ↓
Similarity Search (Cosine)
    ↓
Top-K Documents Retrieved
    ↓
Format RAG Prompt
    ↓
OpenAI API
    ↓
Generated Answer
```

## RAG Prompt Template

The system uses this prompt structure (from `/doc/prompt_gpt.txt`):

```
You are a helpful assistant.

Follow these rules:
- Use ONLY the provided context
- Be concise and factual
- If unsure, say "I don't know"
- Do not make up information

Context:
{retrieved_documents}

Question:
{user_query}

Helpful Answer:
```

## Files

- `app.py` - Flask web app for interactive demo
- `templates/index.html` - Web UI (clean, modern interface)
- `rag.py` - Core RAG implementation
- `rag_local.py` - Optional local LLM variant
- `example.py` - Command-line usage examples
- `pyproject.toml` - Project configuration for UV
- `QUICKSTART.md` - Quick start guide (3 steps)
- `README.md` - Full documentation (this file)
- `.env.example` - Example environment variables (copy and fill)
- `.env` - Local environment variables (not committed to git)

## Environment Variables

All variables are loaded from `.env` automatically:

- **OPENAI_API_KEY** (required) - Your OpenAI API key for GPT models
- **OPENAI_MODEL** (optional) - Defaults to `gpt-3.5-turbo`, can use `gpt-4` or other models
- **HF_TOKEN** (optional) - HuggingFace token for faster model downloads without rate limits
  - Without token: ~100 req/hour limit
  - With token: Significantly higher limits
  - Get your token from: https://huggingface.co/settings/tokens

## Notes

- The embedding model (`all-MiniLM-L6-v2`) is lightweight and runs on CPU
- For larger deployments, consider external vector databases like Pinecone, Weaviate, or Milvus
- You can swap embeddings model by passing `embedding_model` to `SimpleRAG()`
