"""
Configuration management for ResearchPal.
"""
import os
import yaml
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

# Default configuration path
CONFIG_DIR = os.path.expanduser("~/.research_pal")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.yaml")

# Default configuration values
DEFAULT_CONFIG = {
    "openai_api_key": "",
    "google_api_key": "",
    "default_model": "gpt-4o-mini",
    "output_token_limit": 4096,
    "db_path": os.path.expanduser("~/.research_pal/chroma_db"),
    "output_dir": os.path.expanduser("~/research_pal_output")
}

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from file.
    
    Args:
        config_path: Path to configuration file (optional)
        
    Returns:
        Configuration dictionary
    """
    if config_path is None:
        config_path = CONFIG_PATH
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    # If config doesn't exist, create with defaults
    if not os.path.exists(config_path):
        save_config(DEFAULT_CONFIG, config_path)
        return DEFAULT_CONFIG.copy()
    
    # Load existing config
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        # If config is empty, use defaults
        if config is None:
            return DEFAULT_CONFIG.copy()
        
        # Update with any missing default keys
        for key, value in DEFAULT_CONFIG.items():
            if key not in config:
                config[key] = value
        
        # Process special values like paths with ~
        for key in ["db_path", "output_dir"]:
            if key in config and isinstance(config[key], str):
                config[key] = os.path.expanduser(config[key])
        
        return config
    
    except Exception as e:
        logger.error(f"Error loading config from {config_path}: {e}")
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any], config_path: Optional[str] = None) -> None:
    """
    Save configuration to file.
    
    Args:
        config: Configuration dictionary
        config_path: Path to configuration file (optional)
    """
    if config_path is None:
        config_path = CONFIG_PATH
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(config_path), exist_ok=True)
    
    try:
        with open(config_path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"Configuration saved to {config_path}")
    
    except Exception as e:
        logger.error(f"Error saving config to {config_path}: {e}")

def get_api_key(provider: str) -> Optional[str]:
    """
    Get API key for a specific provider.
    
    Args:
        provider: Provider name ('openai' or 'google')
        
    Returns:
        API key or None if not found
    """
    # Try environment variable first
    env_var = f"{provider.upper()}_API_KEY"
    api_key = os.environ.get(env_var)
    
    # If not in environment, try config file
    if not api_key:
        config = load_config()
        config_key = f"{provider.lower()}_api_key"
        api_key = config.get(config_key, "")
    
    return api_key if api_key else None