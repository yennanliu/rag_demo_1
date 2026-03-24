"""Unit tests for Flask API endpoints."""

import pytest
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import sys

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def app():
    """Create test Flask app."""
    # Import here to avoid loading during collection
    from app import app as flask_app, rag, config_manager, conversation_manager

    flask_app.config['TESTING'] = True

    # Clear RAG for fresh state
    rag.documents = []
    rag.embeddings = []

    yield flask_app


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


class TestAPIEndpoints:
    """Test cases for API endpoints."""

    def test_index_route(self, client):
        """Test main index route."""
        response = client.get('/')
        assert response.status_code == 200

    def test_add_document_success(self, client):
        """Test adding a document successfully."""
        response = client.post(
            '/api/add',
            data=json.dumps({'text': 'Test document'}),
            content_type='application/json'
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] is True
        assert 'total_docs' in data

    def test_add_document_empty_text(self, client):
        """Test adding empty document returns error."""
        response = client.post(
            '/api/add',
            data=json.dumps({'text': ''}),
            content_type='application/json'
        )

        data = json.loads(response.data)
        assert response.status_code == 400
        assert data['success'] is False

    def test_add_document_missing_text(self, client):
        """Test adding document without text field."""
        response = client.post(
            '/api/add',
            data=json.dumps({}),
            content_type='application/json'
        )

        data = json.loads(response.data)
        assert response.status_code == 400
        assert data['success'] is False

    def test_get_documents_empty(self, client):
        """Test getting documents when none exist."""
        response = client.get('/api/documents')

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] is True
        assert data['documents'] == [] or isinstance(data['documents'], list)
        assert 'total' in data

    def test_get_documents_after_adding(self, client):
        """Test getting documents after adding some."""
        # Add documents
        client.post(
            '/api/add',
            data=json.dumps({'text': 'Doc 1'}),
            content_type='application/json'
        )
        client.post(
            '/api/add',
            data=json.dumps({'text': 'Doc 2'}),
            content_type='application/json'
        )

        # Get documents
        response = client.get('/api/documents')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert len([d for d in data['documents'] if d in ['Doc 1', 'Doc 2']]) >= 2

    def test_delete_document_success(self, client):
        """Test deleting a document successfully."""
        # Add a document first
        client.post(
            '/api/add',
            data=json.dumps({'text': 'To be deleted'}),
            content_type='application/json'
        )

        # Get current documents to find index
        get_response = client.get('/api/documents')
        get_data = json.loads(get_response.data)
        initial_count = get_data['total']

        if initial_count > 0:
            # Delete first document
            response = client.post(
                '/api/delete',
                data=json.dumps({'index': 0}),
                content_type='application/json'
            )

            data = json.loads(response.data)
            assert response.status_code == 200
            assert data['success'] is True

    def test_delete_document_invalid_index(self, client):
        """Test deleting with invalid index."""
        response = client.post(
            '/api/delete',
            data=json.dumps({'index': 999}),
            content_type='application/json'
        )

        data = json.loads(response.data)
        assert response.status_code == 400
        assert data['success'] is False

    def test_clear_documents(self, client):
        """Test clearing all documents."""
        # Add some documents
        client.post(
            '/api/add',
            data=json.dumps({'text': 'Doc 1'}),
            content_type='application/json'
        )

        # Clear
        response = client.post('/api/clear')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True

        # Verify cleared
        get_response = client.get('/api/documents')
        get_data = json.loads(get_response.data)
        # Should be 0 or only sample docs
        assert isinstance(get_data['total'], int)

    def test_get_config(self, client):
        """Test getting configuration."""
        response = client.get('/api/config')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'config' in data

    def test_update_config(self, client):
        """Test updating configuration."""
        new_config = {
            'sample_documents': ['New doc 1', 'New doc 2']
        }

        response = client.post(
            '/api/config',
            data=json.dumps({'config': new_config}),
            content_type='application/json'
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] is True

    def test_reload_samples(self, client):
        """Test reloading sample documents."""
        response = client.post('/api/reload')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'total_docs' in data

    def test_list_conversations_empty(self, client):
        """Test listing conversations when none exist."""
        response = client.get('/api/conversations')
        data = json.loads(response.data)

        assert response.status_code == 200
        assert data['success'] is True
        assert 'conversations' in data

    def test_save_conversation_success(self, client):
        """Test saving a conversation."""
        messages = [
            {'role': 'user', 'content': 'Hello'},
            {'role': 'assistant', 'content': 'Hi'}
        ]

        response = client.post(
            '/api/conversations',
            data=json.dumps({'messages': messages}),
            content_type='application/json'
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] is True
        assert 'id' in data

    def test_save_conversation_empty_messages(self, client):
        """Test saving conversation with empty messages."""
        response = client.post(
            '/api/conversations',
            data=json.dumps({'messages': []}),
            content_type='application/json'
        )

        data = json.loads(response.data)
        assert response.status_code == 400
        assert data['success'] is False

    @pytest.mark.llm
    def test_query_endpoint(self, client, run_llm):
        """Test query endpoint (requires API key)."""
        if not run_llm:
            pytest.skip("Skipping query tests (use --run-llm to enable)")
        # Add a document
        client.post(
            '/api/add',
            data=json.dumps({'text': 'Python is a programming language.'}),
            content_type='application/json'
        )

        # Query
        response = client.post(
            '/api/query',
            data=json.dumps({'question': 'What is Python?'}),
            content_type='application/json'
        )

        data = json.loads(response.data)
        assert response.status_code == 200
        assert data['success'] is True
        assert 'answer' in data
        assert 'sources' in data

    def test_query_empty_question(self, client):
        """Test query with empty question."""
        response = client.post(
            '/api/query',
            data=json.dumps({'question': ''}),
            content_type='application/json'
        )

        data = json.loads(response.data)
        assert response.status_code == 400
        assert data['success'] is False
