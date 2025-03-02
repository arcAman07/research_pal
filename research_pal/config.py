import os
import json
import yaml
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Default configuration path
CONFIG_PATH = os.path.expanduser("~/.research_pal/config.yaml")

# Default configuration
DEFAULT_CONFIG = {
    "openai_api_key": "",
    "google_api_key": "",
    "db_path": "~/.research_pal/chroma_db",
    "output_dir": "~/research_pal_output",
    "default_model": "gpt-4o-mini",
    "chunk_size": 8000,
    "chunk_overlap": 200
}

def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    if not config_path:
        config_path = CONFIG_PATH
    
    config_path = os.path.expanduser(config_path)
    
    # If config file doesn't exist, create default
    if not os.path.exists(config_path):
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        
        # Save default config
        save_config(DEFAULT_CONFIG, config_path)
        return DEFAULT_CONFIG.copy()
    
    # Load config from file
    try:
        with open(config_path, "r") as f:
            if config_path.endswith(".json"):
                config = json.load(f)
            else:
                config = yaml.safe_load(f)
        
        # Merge with default config to ensure all keys exist
        merged_config = DEFAULT_CONFIG.copy()
        merged_config.update(config)
        
        return merged_config
    
    except Exception as e:
        logger.error(f"Failed to load config from {config_path}: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any], config_path: str = None) -> bool:
    """
    Save configuration to file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to configuration file
        
    Returns:
        True if successful, False otherwise
    """
    if not config_path:
        config_path = CONFIG_PATH
    
    config_path = os.path.expanduser(config_path)
    
    # Create directory if it doesn't exist
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    try:
        with open(config_path, "w") as f:
            if config_path.endswith(".json"):
                json.dump(config, f, indent=2)
            else:
                yaml.dump(config, f, default_flow_style=False)
        
        return True
    
    except Exception as e:
        logger.error(f"Failed to save config to {config_path}: {e}")
        return False

def get_api_key(key_name: str) -> str:
    """
    Get API key from environment or config.
    
    Args:
        key_name: Name of the API key
        
    Returns:
        API key if found, empty string otherwise
    """
    # Try to get from environment
    api_key = os.environ.get(key_name.upper())
    
    # If not found, try to get from config
    if not api_key:
        config = load_config()
        api_key = config.get(key_name.lower(), "")
    
    return api_key