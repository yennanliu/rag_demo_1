"""Unit tests for ConfigManager."""

import pytest
import json
from pathlib import Path
from tempfile import NamedTemporaryFile
from utils.config_manager import ConfigManager


class TestConfigManager:
    """Test cases for ConfigManager class."""

    def test_load_nonexistent_file(self):
        """Test loading from non-existent config file."""
        with NamedTemporaryFile(delete=True) as tmp:
            config_path = Path(tmp.name)

        manager = ConfigManager(config_path)
        config = manager.load()

        assert config == {"sample_documents": []}

    def test_save_and_load(self):
        """Test saving and loading configuration."""
        with NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
            config_path = Path(tmp.name)

        try:
            manager = ConfigManager(config_path)
            test_config = {
                "sample_documents": ["Doc 1", "Doc 2", "Doc 3"]
            }

            manager.save(test_config)
            loaded_config = manager.load()

            assert loaded_config == test_config
        finally:
            config_path.unlink()

    def test_get_sample_documents(self):
        """Test getting sample documents."""
        with NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
            config_path = Path(tmp.name)

        try:
            manager = ConfigManager(config_path)
            test_docs = ["Doc 1", "Doc 2", "Doc 3"]
            config = {"sample_documents": test_docs}

            manager.save(config)
            retrieved_docs = manager.get_sample_documents()

            assert retrieved_docs == test_docs
        finally:
            config_path.unlink()

    def test_get_sample_documents_empty(self):
        """Test getting sample documents from empty config."""
        with NamedTemporaryFile(delete=True) as tmp:
            config_path = Path(tmp.name)

        manager = ConfigManager(config_path)
        docs = manager.get_sample_documents()

        assert docs == []

    def test_update_sample_documents(self):
        """Test updating sample documents."""
        with NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
            config_path = Path(tmp.name)
            # Write empty JSON to start
            json.dump({}, tmp)

        try:
            manager = ConfigManager(config_path)
            initial_docs = ["Doc 1", "Doc 2"]
            updated_docs = ["New Doc 1", "New Doc 2", "New Doc 3"]

            manager.update_sample_documents(initial_docs)
            manager.update_sample_documents(updated_docs)

            retrieved_docs = manager.get_sample_documents()

            assert retrieved_docs == updated_docs
        finally:
            if config_path.exists():
                config_path.unlink()

    def test_backward_compatibility_internal_documents(self):
        """Test backward compatibility with 'internal_documents' field."""
        with NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
            config_path = Path(tmp.name)
            # Write config with old field name
            config = {"internal_documents": ["Doc 1", "Doc 2"]}
            json.dump(config, tmp)

        try:
            manager = ConfigManager(config_path)
            loaded_config = manager.load()

            # Should convert to new field name
            assert "sample_documents" in loaded_config
            assert loaded_config["sample_documents"] == ["Doc 1", "Doc 2"]
        finally:
            config_path.unlink()

    def test_preserve_other_config_fields(self):
        """Test that other config fields are preserved."""
        with NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
            config_path = Path(tmp.name)

        try:
            manager = ConfigManager(config_path)
            config = {
                "sample_documents": ["Doc 1"],
                "custom_field": "value",
                "another_field": 123
            }

            manager.save(config)
            loaded_config = manager.load()

            assert loaded_config["custom_field"] == "value"
            assert loaded_config["another_field"] == 123
        finally:
            config_path.unlink()

    def test_json_format_validation(self):
        """Test that saved config is valid JSON."""
        with NamedTemporaryFile(mode='w', delete=False, suffix='.json') as tmp:
            config_path = Path(tmp.name)

        try:
            manager = ConfigManager(config_path)
            config = {"sample_documents": ["Doc 1", "Doc 2"]}

            manager.save(config)

            # Try to load directly with json
            with open(config_path, 'r') as f:
                loaded = json.load(f)

            assert loaded == config
        finally:
            config_path.unlink()
