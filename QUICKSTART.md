# Quick Start Guide

## 1. Setup (one-time)

```bash
# Install dependencies
uv sync

# Configure API keys
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## 2. Run the Web App

```bash
uv run python app.py
```

Then open: **http://localhost:5000**

## 3. Use the Interface

### 💬 Chat with Your Knowledge Base
1. Type your question in the chat input
2. Press `Enter` to send (or `Shift+Enter` for new line)
3. See the AI's answer with source documents highlighted
4. Continue the conversation - full history is maintained!

### 📝 Add Knowledge
1. Type information in the "Add Knowledge" box on the right
2. Click "Add Document" or press `Ctrl+Enter`
3. The document is instantly added to the knowledge base

### 📚 Manage Documents
- **View All**: Click "View All" to see a modal with all documents
- **Delete**: Remove individual documents by clicking "Delete" in the modal
- **Export**: Save your knowledge base as JSON file
- **Import**: Load a previously exported knowledge base
- **Clear**: Reset the entire knowledge base

### ⚙️ Configure Sample Documents
1. Scroll to "Sample Documents" section
2. Add, edit, or remove sample documents
3. Click "💾 Save Config" to persist to `config.json`
4. Click "🔄 Reload" to refresh knowledge base with saved samples

## Tips

- Start with sample documents (3 are pre-loaded about Tony Q)
- Add related documents to build a coherent knowledge base
- Questions work best when the knowledge base has relevant info
- The AI will say "I don't know" if info isn't in the knowledge base

## Example Session

1. Add document: "React is a JavaScript library for building UIs"
2. Add document: "React was created by Facebook in 2013"
3. Ask: "What is React?"
4. Get answer: "React is a JavaScript library for building UIs, created by Facebook in 2013"

## Troubleshooting

**Error: OPENAI_API_KEY not found**
- Edit `.env` and add your API key

**Slow responses**
- First run downloads embedding models (~100MB)
- Subsequent runs are much faster

**Port 5000 already in use**
- Stop other Flask apps or edit `app.py` to change the port
