"""Conversation history management."""

import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime


class ConversationManager:
    """Manages conversation history persistence."""

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.mkdir(exist_ok=True)

    def save_conversation(self, conversation: List[Dict], name: str = None) -> str:
        """
        Save a conversation to disk.

        Args:
            conversation: List of messages with role, content, sources
            name: Optional custom name, defaults to timestamp

        Returns:
            Conversation ID (filename without extension)
        """
        if not name:
            name = datetime.now().strftime("%Y%m%d_%H%M%S")

        conversation_data = {
            "id": name,
            "created_at": datetime.now().isoformat(),
            "messages": conversation
        }

        file_path = self.storage_path / f"{name}.json"
        with open(file_path, "w") as f:
            json.dump(conversation_data, f, indent=2)

        return name

    def load_conversation(self, conversation_id: str) -> Dict:
        """Load a conversation by ID."""
        file_path = self.storage_path / f"{conversation_id}.json"
        if not file_path.exists():
            raise FileNotFoundError(f"Conversation {conversation_id} not found")

        with open(file_path, "r") as f:
            return json.load(f)

    def list_conversations(self) -> List[Dict]:
        """List all saved conversations."""
        conversations = []
        for file_path in self.storage_path.glob("*.json"):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)
                    conversations.append({
                        "id": data.get("id", file_path.stem),
                        "created_at": data.get("created_at", ""),
                        "message_count": len(data.get("messages", []))
                    })
            except Exception:
                continue

        # Sort by created_at descending (newest first)
        conversations.sort(key=lambda x: x["created_at"], reverse=True)
        return conversations

    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        file_path = self.storage_path / f"{conversation_id}.json"
        if file_path.exists():
            file_path.unlink()
            return True
        return False

    def export_all(self) -> Dict:
        """Export all conversations."""
        all_conversations = []
        for conv_info in self.list_conversations():
            try:
                conv_data = self.load_conversation(conv_info["id"])
                all_conversations.append(conv_data)
            except Exception:
                continue

        return {
            "exported_at": datetime.now().isoformat(),
            "count": len(all_conversations),
            "conversations": all_conversations
        }

    def import_conversations(self, data: Dict) -> int:
        """
        Import conversations from export data.

        Returns:
            Number of conversations imported
        """
        count = 0
        for conv in data.get("conversations", []):
            try:
                conv_id = conv.get("id", datetime.now().strftime("%Y%m%d_%H%M%S"))
                self.save_conversation(conv.get("messages", []), conv_id)
                count += 1
            except Exception:
                continue

        return count
