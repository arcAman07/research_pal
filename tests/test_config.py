"""
Tests for the configuration utilities.
"""
import os
import pytest
import tempfile
import yaml
from unittest.mock import patch, MagicMock

from research_pal.utils.config import load_config, save_config, get_api_key, DEFAULT_CONFIG


@pytest.fixture
def temp_config_file():
    """Create a temporary config file."""
    with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as f:
        yield f.name
    # Clean up after the test
    os.unlink(f.name)


def test_load_config_default(temp_config_file):
    """Test loading default configuration."""
    # Test loading when file doesn't exist
    os.unlink(temp_config_file)  # Delete the file
    
    config = load_config(temp_config_file)
    
    # Verify that we get default config
    assert config == DEFAULT_CONFIG
    
    # File should be created
    assert os.path.exists(temp_config_file)


def test_load_config_existing(temp_config_file):
    """Test loading configuration from existing file."""
    # Create a test config
    test_config = {
        "openai_api_key": "test_key",
        "default_model": "test_model",
        "db_path": "~/test_db"
    }
    
    # Write the config to file
    with open(temp_config_file, 'w') as f:
        yaml.dump(test_config, f)
    
    # Load the config
    config = load_config(temp_config_file)
    
    # Verify that we get our test config with defaults filled in
    assert config["openai_api_key"] == "test_key"
    assert config["default_model"] == "test_model"
    assert "~/test_db" in config["db_path"]  # Path should be expanded
    
    # Missing values should be filled with defaults
    for key in DEFAULT_CONFIG:
        if key not in test_config:
            assert key in config
            assert config[key] == DEFAULT_CONFIG[key]


def test_save_config(temp_config_file):
    """Test saving configuration."""
    # Create a test config
    test_config = {
        "openai_api_key": "test_key",
        "default_model": "test_model"
    }
    
    # Save the config
    save_config(test_config, temp_config_file)
    
    # Verify that the file was created
    assert os.path.exists(temp_config_file)
    
    # Load the config and verify contents
    with open(temp_config_file, 'r') as f:
        loaded_config = yaml.safe_load(f)
    
    assert loaded_config["openai_api_key"] == "test_key"
    assert loaded_config["default_model"] == "test_model"


def test_get_api_key_from_env():
    """Test getting API key from environment."""
    # Set environment variable
    with patch.dict(os.environ, {"OPENAI_API_KEY": "env_key"}):
        key = get_api_key("openai")
        assert key == "env_key"


def test_get_api_key_from_config():
    """Test getting API key from config when not in environment."""
    # Mock load_config
    with patch("research_pal.utils.config.load_config") as mock_load_config:
        mock_load_config.return_value = {"openai_api_key": "config_key"}
        
        # Ensure no environment variable
        with patch.dict(os.environ, {}, clear=True):
            key = get_api_key("openai")
            assert key == "config_key"
            mock_load_config.assert_called_once()


def test_get_api_key_not_found():
    """Test behavior when API key is not found."""
    # Mock load_config to return empty config
    with patch("research_pal.utils.config.load_config") as mock_load_config:
        mock_load_config.return_value = {}
        
        # Ensure no environment variable
        with patch.dict(os.environ, {}, clear=True):
            key = get_api_key("nonexistent")
            assert key is None