"""Unit tests for ConversationManager."""

import pytest
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import datetime
from utils.conversation_manager import ConversationManager


class TestConversationManager:
    """Test cases for ConversationManager class."""

    def test_initialization(self):
        """Test ConversationManager initialization."""
        with TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir)
            manager = ConversationManager(storage_path)

            assert manager.storage_path == storage_path
            assert storage_path.exists()

    def test_save_conversation_with_auto_name(self):
        """Test saving conversation with auto-generated name."""
        with TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir)
            manager = ConversationManager(storage_path)

            messages = [
                {"role": "user", "content": "Hello", "timestamp": 123},
                {"role": "assistant", "content": "Hi", "timestamp": 124}
            ]

            conv_id = manager.save_conversation(messages)

            assert conv_id is not None
            assert (storage_path / f"{conv_id}.json").exists()

    def test_save_conversation_with_custom_name(self):
        """Test saving conversation with custom name."""
        with TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir)
            manager = ConversationManager(storage_path)

            messages = [{"role": "user", "content": "Test"}]
            custom_name = "my_conversation"

            conv_id = manager.save_conversation(messages, custom_name)

            assert conv_id == custom_name
            assert (storage_path / f"{custom_name}.json").exists()

    def test_load_conversation(self):
        """Test loading a saved conversation."""
        with TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir)
            manager = ConversationManager(storage_path)

            messages = [
                {"role": "user", "content": "Question"},
                {"role": "assistant", "content": "Answer"}
            ]

            conv_id = manager.save_conversation(messages, "test_conv")
            loaded = manager.load_conversation("test_conv")

            assert loaded["id"] == "test_conv"
            assert loaded["messages"] == messages
            assert "created_at" in loaded

    def test_load_nonexistent_conversation(self):
        """Test loading non-existent conversation raises error."""
        with TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir)
            manager = ConversationManager(storage_path)

            with pytest.raises(FileNotFoundError):
                manager.load_conversation("nonexistent")

    def test_list_conversations_empty(self):
        """Test listing conversations when none exist."""
        with TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir)
            manager = ConversationManager(storage_path)

            conversations = manager.list_conversations()

            assert conversations == []

    def test_list_conversations(self):
        """Test listing multiple conversations."""
        with TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir)
            manager = ConversationManager(storage_path)

            # Create multiple conversations
            for i in range(3):
                messages = [{"role": "user", "content": f"Message {i}"}]
                manager.save_conversation(messages, f"conv_{i}")

            conversations = manager.list_conversations()

            assert len(conversations) == 3
            assert all("id" in conv for conv in conversations)
            assert all("created_at" in conv for conv in conversations)
            assert all("message_count" in conv for conv in conversations)

    def test_list_conversations_sorting(self):
        """Test that conversations are sorted by created_at (newest first)."""
        with TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir)
            manager = ConversationManager(storage_path)

            # Create conversations with different timestamps
            messages = [{"role": "user", "content": "Test"}]
            manager.save_conversation(messages, "conv_1")
            manager.save_conversation(messages, "conv_2")
            manager.save_conversation(messages, "conv_3")

            conversations = manager.list_conversations()

            # Should be sorted newest first
            timestamps = [conv["created_at"] for conv in conversations]
            assert timestamps == sorted(timestamps, reverse=True)

    def test_delete_conversation(self):
        """Test deleting a conversation."""
        with TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir)
            manager = ConversationManager(storage_path)

            messages = [{"role": "user", "content": "Test"}]
            conv_id = manager.save_conversation(messages, "test_delete")

            # Verify it exists
            assert (storage_path / f"{conv_id}.json").exists()

            # Delete it
            result = manager.delete_conversation(conv_id)

            assert result is True
            assert not (storage_path / f"{conv_id}.json").exists()

    def test_delete_nonexistent_conversation(self):
        """Test deleting non-existent conversation returns False."""
        with TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir)
            manager = ConversationManager(storage_path)

            result = manager.delete_conversation("nonexistent")

            assert result is False

    def test_export_all_empty(self):
        """Test exporting all conversations when none exist."""
        with TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir)
            manager = ConversationManager(storage_path)

            export_data = manager.export_all()

            assert "exported_at" in export_data
            assert export_data["count"] == 0
            assert export_data["conversations"] == []

    def test_export_all(self):
        """Test exporting all conversations."""
        with TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir)
            manager = ConversationManager(storage_path)

            # Create multiple conversations
            for i in range(3):
                messages = [{"role": "user", "content": f"Message {i}"}]
                manager.save_conversation(messages, f"conv_{i}")

            export_data = manager.export_all()

            assert export_data["count"] == 3
            assert len(export_data["conversations"]) == 3
            assert "exported_at" in export_data

    def test_import_conversations(self):
        """Test importing conversations."""
        with TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir)
            manager = ConversationManager(storage_path)

            # Create export data
            import_data = {
                "conversations": [
                    {
                        "id": "imported_1",
                        "messages": [{"role": "user", "content": "Test 1"}]
                    },
                    {
                        "id": "imported_2",
                        "messages": [{"role": "user", "content": "Test 2"}]
                    }
                ]
            }

            count = manager.import_conversations(import_data)

            assert count == 2
            assert (storage_path / "imported_1.json").exists()
            assert (storage_path / "imported_2.json").exists()

    def test_import_conversations_with_invalid_data(self):
        """Test importing with invalid data gracefully handles errors."""
        with TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir)
            manager = ConversationManager(storage_path)

            # Invalid import data
            import_data = {
                "conversations": [
                    {"messages": [{"role": "user", "content": "Valid"}]},
                    {"invalid": "data"},  # Missing required fields
                ]
            }

            count = manager.import_conversations(import_data)

            # Should import at least the valid one
            assert count >= 1

    def test_conversation_file_format(self):
        """Test that saved conversation has correct format."""
        with TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir)
            manager = ConversationManager(storage_path)

            messages = [
                {"role": "user", "content": "Question", "timestamp": 123},
                {
                    "role": "assistant",
                    "content": "Answer",
                    "sources": ["Source 1"],
                    "timestamp": 124
                }
            ]

            conv_id = manager.save_conversation(messages, "test_format")

            # Load and check format
            with open(storage_path / f"{conv_id}.json", 'r') as f:
                data = json.load(f)

            assert "id" in data
            assert "created_at" in data
            assert "messages" in data
            assert data["messages"] == messages

    def test_message_count_accuracy(self):
        """Test that message_count in list is accurate."""
        with TemporaryDirectory() as tmpdir:
            storage_path = Path(tmpdir)
            manager = ConversationManager(storage_path)

            messages = [
                {"role": "user", "content": "Q1"},
                {"role": "assistant", "content": "A1"},
                {"role": "user", "content": "Q2"},
                {"role": "assistant", "content": "A2"}
            ]

            manager.save_conversation(messages, "test_count")
            conversations = manager.list_conversations()

            assert len(conversations) == 1
            assert conversations[0]["message_count"] == 4
