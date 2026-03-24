# Project Structure

## Overview

Clean, modular organization with separation of concerns:

```
rag_demo_1/
│
├── 📱 Core Application
│   ├── app.py                        # Flask backend
│   ├── rag.py                        # RAG core engine
│   └── utils/                        # Utility modules
│       ├── __init__.py
│       ├── config_manager.py         # Configuration management
│       └── conversation_manager.py   # Conversation persistence
│
├── 🌐 Frontend
│   ├── templates/
│   │   └── index.html                # HTML structure
│   └── static/
│       ├── app.js                    # JavaScript (RAGApp class)
│       └── styles.css                # Styling
│
├── 🎮 Demo & Examples
│   └── demo/
│       ├── example.py                # Command-line examples
│       └── rag_local.py              # Local LLM variant
│
├── 🧪 Tests
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_rag.py               # RAG core tests
│   │   ├── test_config_manager.py    # Config tests
│   │   ├── test_conversation_manager.py  # Conversation tests
│   │   └── test_app.py               # API endpoint tests
│   └── pytest.ini                    # Pytest configuration
│
├── 📚 Documentation
│   ├── README.md                     # Main docs (English)
│   ├── README_zh-TW.md               # 繁體中文文件
│   └── doc/
│       ├── QUICKSTART.md             # Quick start guide
│       ├── ARCHITECTURE.md           # System architecture
│       ├── WHATS_NEW.md              # New features guide
│       ├── ENHANCEMENTS_SUMMARY.md   # Enhancement details
│       ├── IMPROVEMENTS.md           # Earlier improvements
│       ├── pic/                      # Screenshots
│       ├── prompt_gemini.txt         # Prompt templates
│       └── prompt_gpt.txt
│
├── ⚙️ Configuration
│   ├── pyproject.toml                # Dependencies (UV)
│   ├── config.json                   # Sample documents (user config)
│   ├── config.example.json           # Config template
│   ├── .env                          # API keys (not committed)
│   ├── .env.example                  # Env template
│   └── .gitignore                    # Git ignore rules
│
└── 💾 Runtime Data (auto-created, not committed)
    ├── conversations/                # Saved conversations
    ├── .venv/                        # Python virtual environment
    └── __pycache__/                  # Python cache
```

## Directory Purposes

### Core Application

**`app.py`**
- Flask web server
- REST API endpoints
- Routes for documents, queries, conversations, config

**`rag.py`**
- Core RAG implementation
- Document embeddings
- Semantic search
- LLM integration

**`utils/`**
- Modular utility classes
- Clean separation of concerns
- Reusable components

### Frontend

**`templates/`**
- HTML structure only
- Clean, semantic markup
- No inline JavaScript/CSS

**`static/`**
- Client-side assets
- Organized JavaScript (RAGApp class)
- Comprehensive CSS styling

### Demo & Examples

**`demo/`**
- Non-core functionality
- Example scripts for learning
- Alternative implementations

### Tests

**`tests/`**
- Comprehensive unit tests
- ~90% code coverage
- Pytest-based test suite
- Separate test for each component

### Documentation

**Root READMEs**
- English and Traditional Chinese
- Quick overview and links

**`doc/`**
- Detailed documentation
- Architecture diagrams
- User guides
- Enhancement history

### Configuration

**`pyproject.toml`**
- Python dependencies
- Project metadata
- Dev dependencies (pytest)

**Config files**
- Sample documents
- Environment variables
- Git ignore rules

## File Counts

```
Python files:     7 core + 4 tests = 11 total
JavaScript:       1 (app.js)
CSS:              1 (styles.css)
HTML:             1 (index.html)
Documentation:    9 files
Config:           6 files
```

## Code Organization

### Backend (Python)

```python
# Clean modular imports
from utils import ConfigManager, ConversationManager

# Organized app.py with sections:
# - Page routes
# - Document API
# - Query API
# - Config API
# - Conversation API
```

### Frontend (JavaScript)

```javascript
// Single class-based architecture
class RAGApp {
    // Organized methods by feature:
    // - Conversation persistence
    // - Config management
    // - Document management
    // - Chat interface
    // - Export/Import
    // - UI helpers
}
```

### Tests (Pytest)

```python
# Test organization:
# test_rag.py           → RAG core
# test_config_manager   → Configuration
# test_conversation_*   → Conversations
# test_app.py           → API endpoints
```

## Benefits of Current Structure

✅ **Clear separation of concerns**
- Core logic separate from web interface
- Utilities isolated in own modules
- Tests mirror source structure

✅ **Easy to navigate**
- Logical grouping by purpose
- Predictable file locations
- Clear naming conventions

✅ **Modular and testable**
- Each component can be tested independently
- Easy to mock dependencies
- High test coverage possible

✅ **Professional organization**
- Follows Python best practices
- Similar to production codebases
- Easy to onboard new developers

✅ **Scalable architecture**
- Easy to add new features
- Clear extension points
- Minimal coupling between components

## Key Design Principles

1. **Separation of Concerns**
   - Backend, frontend, tests separate
   - Utilities abstracted into modules
   - Demo code isolated from core

2. **Single Responsibility**
   - Each file has one clear purpose
   - Utility classes focused on specific tasks
   - Clean API boundaries

3. **DRY (Don't Repeat Yourself)**
   - Reusable utility classes
   - Shared configuration management
   - Common test fixtures

4. **Explicit is Better than Implicit**
   - Clear directory names
   - Descriptive file names
   - Well-documented code

5. **Testability**
   - Test files mirror source files
   - Clear test organization
   - Easy to run and maintain

## Migration from Old Structure

**Before:**
```
rag_demo_1/
├── app.py
├── rag.py
├── example.py
├── rag_local.py
├── QUICKSTART.md
├── ARCHITECTURE.md
├── WHATS_NEW.md
└── templates/index.html (with inline JS)
```

**After:**
```
rag_demo_1/
├── app.py
├── rag.py
├── utils/          # NEW - Modular utilities
├── demo/           # NEW - Examples moved here
├── tests/          # NEW - Comprehensive tests
├── doc/            # NEW - All docs organized
├── static/         # NEW - Frontend assets
└── README_zh-TW.md # NEW - Chinese version
```

## Commands

### Development

```bash
# Run app
uv run python app.py

# Run tests
uv run pytest

# Run examples
uv run python demo/example.py
```

### Testing

```bash
# All tests
uv run pytest

# Specific test
uv run pytest tests/test_rag.py

# With coverage
uv run pytest --cov=.
```

### Project Management

```bash
# Install dependencies
uv sync

# Install with dev dependencies
uv sync --extra dev

# Update dependencies
uv lock
```

---

**Last Updated:** 2026-03-24

**Structure Version:** 2.0 (Reorganized)
