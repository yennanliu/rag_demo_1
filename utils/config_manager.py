"""Configuration management for RAG demo."""

import json
from pathlib import Path
from typing import Dict, List


class ConfigManager:
    """Manages application configuration from config.json."""

    def __init__(self, config_path: Path):
        self.config_path = config_path

    def load(self) -> Dict:
        """Load configuration from file."""
        if self.config_path.exists():
            with open(self.config_path, "r") as f:
                config = json.load(f)
                # Backward compatibility: support both field names
                if "internal_documents" in config and "sample_documents" not in config:
                    config["sample_documents"] = config["internal_documents"]
                return config
        return {"sample_documents": []}

    def save(self, config: Dict) -> None:
        """Save configuration to file."""
        with open(self.config_path, "w") as f:
            json.dump(config, f, indent=2)

    def get_sample_documents(self) -> List[str]:
        """Get list of sample documents."""
        config = self.load()
        return config.get("sample_documents", [])

    def update_sample_documents(self, documents: List[str]) -> None:
        """Update sample documents in config."""
        config = self.load()
        config["sample_documents"] = documents
        self.save(config)
