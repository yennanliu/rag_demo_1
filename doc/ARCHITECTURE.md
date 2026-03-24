# RAG Demo - Architecture Documentation

## Overview

The RAG Demo is a web-based application that demonstrates Retrieval-Augmented Generation using a clean, modular architecture with full separation of concerns.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Browser)                    │
│  ┌────────────┐  ┌──────────────┐  ┌─────────────────────┐ │
│  │ index.html │  │  styles.css  │  │      app.js         │ │
│  │            │  │              │  │                     │ │
│  │ Structure  │  │   Styling    │  │  Business Logic     │ │
│  │            │  │              │  │  - RAGApp class     │ │
│  └────────────┘  └──────────────┘  │  - Conversation     │ │
│                                     │  - Document Mgmt    │ │
│                                     │  - LocalStorage     │ │
│                                     └─────────────────────┘ │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API (JSON)
┌──────────────────────┴──────────────────────────────────────┐
│                    Backend (Flask / Python)                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    app.py                            │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │   │
│  │  │   Routes     │  │  Endpoints   │  │ Managers  │ │   │
│  │  │              │  │              │  │           │ │   │
│  │  │ /            │  │ /api/query   │  │ RAG       │ │   │
│  │  │ /api/*       │  │ /api/add     │  │ Config    │ │   │
│  │  │              │  │ /api/conv/*  │  │ Conv      │ │   │
│  │  └──────────────┘  └──────────────┘  └───────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              utils/ (Utility Modules)                │   │
│  │  ┌──────────────────┐  ┌──────────────────────────┐│   │
│  │  │ ConfigManager    │  │ ConversationManager      ││   │
│  │  │                  │  │                          ││   │
│  │  │ - load()         │  │ - save_conversation()    ││   │
│  │  │ - save()         │  │ - load_conversation()    ││   │
│  │  │ - get_samples()  │  │ - list_conversations()   ││   │
│  │  │ - update()       │  │ - delete_conversation()  ││   │
│  │  └──────────────────┘  │ - export_all()           ││   │
│  │                        │ - import_conversations() ││   │
│  │                        └──────────────────────────┘│   │
│  └─────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │                    rag.py                            │   │
│  │  ┌────────────────────────────────────────────────┐ │   │
│  │  │              SimpleRAG                          │ │   │
│  │  │                                                 │ │   │
│  │  │ - add_document()                                │ │   │
│  │  │ - retrieve() → Top-K semantic search           │ │   │
│  │  │ - generate_answer() → LLM response             │ │   │
│  │  └────────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                      Data Layer                              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ config.json │  │ .env         │  │ conversations/   │   │
│  │             │  │              │  │                  │   │
│  │ Sample docs │  │ API keys     │  │ *.json (saved)   │   │
│  └─────────────┘  └──────────────┘  └──────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            In-Memory (RAG Instance)                   │  │
│  │  - documents[]                                        │  │
│  │  - embeddings (numpy array)                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                       │
┌──────────────────────┴──────────────────────────────────────┐
│                  External Services                           │
│  ┌──────────────────┐  ┌─────────────────────────────────┐ │
│  │  OpenAI API      │  │  HuggingFace Hub                │ │
│  │  (GPT models)    │  │  (Embedding models)             │ │
│  └──────────────────┘  └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Module Structure

### Frontend

```
static/
├── app.js          # Main application class
│   ├── RAGApp class
│   │   ├── Conversation management
│   │   ├── Document management
│   │   ├── Configuration
│   │   └── UI helpers
│   └── Event handlers
│
├── styles.css      # All styling
│   ├── Layout (grid, cards)
│   ├── Components (buttons, modals)
│   ├── Chat interface
│   └── Responsive design
│
templates/
└── index.html      # HTML structure
    ├── Header
    ├── Main grid (chat + management)
    ├── Modals (documents, conversations)
    └── Script inclusion
```

### Backend

```
app.py                      # Main Flask application
├── Route definitions
│   ├── Page routes (/)
│   ├── Document API (/api/add, /api/documents, etc.)
│   ├── Query API (/api/query)
│   ├── Config API (/api/config, /api/reload)
│   └── Conversation API (/api/conversations/*)
└── Manager initialization

utils/
├── __init__.py
├── config_manager.py       # Configuration persistence
│   └── ConfigManager class
│       ├── load()
│       ├── save()
│       ├── get_sample_documents()
│       └── update_sample_documents()
│
└── conversation_manager.py # Conversation history
    └── ConversationManager class
        ├── save_conversation()
        ├── load_conversation()
        ├── list_conversations()
        ├── delete_conversation()
        ├── export_all()
        └── import_conversations()

rag.py                      # Core RAG engine
└── SimpleRAG class
    ├── __init__() → Load embedding model
    ├── add_document() → Add to knowledge base
    ├── retrieve() → Semantic search
    └── generate_answer() → LLM query
```

## Data Flow

### 1. Query Flow

```
User types question
    ↓
Frontend (app.js)
    ↓
POST /api/query
    ↓
Backend: rag.retrieve(question)
    ↓
Embedding model → Query vector
    ↓
Cosine similarity with document embeddings
    ↓
Top-K documents retrieved
    ↓
Backend: rag.generate_answer()
    ↓
Format RAG prompt with context
    ↓
OpenAI API (GPT)
    ↓
Return answer + sources
    ↓
Frontend: Display in chat with sources
    ↓
Save to localStorage
```

### 2. Document Addition Flow

```
User enters document text
    ↓
Frontend (app.js)
    ↓
POST /api/add
    ↓
Backend: rag.add_document(text)
    ↓
Generate embedding (sentence-transformers)
    ↓
Store in documents[] + embeddings array
    ↓
Return success + total count
    ↓
Frontend: Update UI
```

### 3. Conversation Save Flow

```
User clicks "Save"
    ↓
Frontend: app.saveConversationToServer()
    ↓
POST /api/conversations
    ↓
Backend: conversation_manager.save_conversation()
    ↓
Create JSON file with timestamp ID
    ↓
Store in conversations/ directory
    ↓
Return conversation ID
    ↓
Frontend: Show success message
```

### 4. Configuration Flow

```
User edits sample documents in UI
    ↓
Frontend: app.saveConfig()
    ↓
POST /api/config
    ↓
Backend: config_manager.save(config)
    ↓
Write to config.json
    ↓
Return success
    ↓
User clicks "Reload"
    ↓
POST /api/reload
    ↓
Backend: Clear RAG, reload from config
    ↓
Return new document count
```

## API Endpoints

### Document Management
- `POST /api/add` - Add document to knowledge base
- `GET /api/documents` - List all documents
- `POST /api/delete` - Delete document by index
- `POST /api/clear` - Clear all documents

### Query
- `POST /api/query` - Query RAG system (returns answer + sources)

### Configuration
- `GET /api/config` - Get current config
- `POST /api/config` - Update config
- `POST /api/reload` - Reload sample documents from config

### Conversations
- `GET /api/conversations` - List all saved conversations
- `POST /api/conversations` - Save new conversation
- `GET /api/conversations/<id>` - Get specific conversation
- `DELETE /api/conversations/<id>` - Delete conversation
- `GET /api/conversations/export` - Export all as JSON
- `POST /api/conversations/import` - Import conversations from JSON

## Persistence

### LocalStorage (Browser)
- **Key**: `ragConversation`
- **Data**: Current conversation history
- **Auto-save**: After each message
- **Purpose**: Session continuity (survives page refresh)

### File System (Server)

#### config.json
```json
{
  "sample_documents": [
    "Document 1",
    "Document 2"
  ]
}
```

#### conversations/{id}.json
```json
{
  "id": "20260324_143022",
  "created_at": "2026-03-24T14:30:22.123456",
  "messages": [
    {
      "role": "user",
      "content": "Question text",
      "timestamp": 1711282222123
    },
    {
      "role": "assistant",
      "content": "Answer text",
      "sources": ["Doc 1", "Doc 2"],
      "timestamp": 1711282223456
    }
  ]
}
```

## Security Considerations

1. **XSS Prevention**: HTML escaping in frontend
2. **API Keys**: Stored in .env (not committed)
3. **Input Validation**: Required fields checked in backend
4. **Error Handling**: Try-catch blocks with safe error messages
5. **File Access**: Restricted to specific directories

## Performance Optimizations

1. **Embeddings**: Cached in memory (numpy array)
2. **LocalStorage**: Immediate save without API call
3. **CSS Animations**: GPU-accelerated (transform/opacity)
4. **Lazy Loading**: Modals loaded on demand
5. **Batch Operations**: Multiple documents in single transaction

## Extensibility Points

1. **Add new embedding models**: Modify `SimpleRAG.__init__()`
2. **Add new LLM providers**: Modify `SimpleRAG.generate_answer()`
3. **Custom storage backends**: Extend `ConversationManager`
4. **Add authentication**: Middleware in `app.py`
5. **Multi-user support**: Session management + user isolation

## Dependencies

### Backend
- `flask` - Web framework
- `python-dotenv` - Environment variables
- `openai` - LLM API
- `sentence-transformers` - Embeddings
- `numpy` - Vector operations

### Frontend
- Vanilla JavaScript (no frameworks)
- CSS3 with CSS Grid
- HTML5 with semantic markup

## Deployment Considerations

1. **Production server**: Use Gunicorn/uWSGI instead of Flask dev server
2. **Database**: Consider PostgreSQL + pgvector for production
3. **Caching**: Add Redis for conversation caching
4. **CDN**: Serve static files from CDN
5. **Monitoring**: Add logging and error tracking
