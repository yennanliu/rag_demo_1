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

### Add Knowledge
1. Type information in the "Add Knowledge" box
2. Click "Add Document" or press `Ctrl+Enter`
3. Repeat to build your knowledge base

### Ask Questions
1. Type a question in the "Ask Questions" box
2. Click "Ask Question" or press `Ctrl+Enter`
3. The AI will answer based on your knowledge base

### Configure Sample Documents
1. Scroll to "Sample Documents Configuration"
2. Add, edit, or remove sample documents
3. Click "Save Config" to persist changes to `config.json`
4. Click "Reload from Config" to reset knowledge base with saved samples

### Manage Documents
- **View All Documents**: See everything in the knowledge base
- **Clear All**: Reset the knowledge base

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
