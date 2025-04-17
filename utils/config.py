"""
Configuration management for Kusto MCP server
"""
import os
import json
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kusto_config")

CONFIG_FILE = Path.home() / ".kusto_mcp_config.json"

def load_dotenv(env_file='.env'):
    """Load environment variables from .env file"""
    try:
        if os.path.exists(env_file):
            logger.info(f"Loading environment variables from {env_file}")
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    key, value = line.split('=', 1)
                    os.environ[key] = value
            return True
        return False
    except Exception as e:
        logger.error(f"Error loading .env file: {e}")
        return False

def load_config():
    """Load configuration from file or environment variables"""
    config = {}
    
    # Try loading from .env file first
    load_dotenv()
    
    # Try to load from config file
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
        except Exception as e:
            logger.error(f"Error loading config file: {e}")
    
    # Override with environment variables if present
    if os.getenv("KUSTO_CLUSTER"):
        config["kusto_cluster"] = os.getenv("KUSTO_CLUSTER")
    if os.getenv("KUSTO_DATABASE"):
        config["kusto_database"] = os.getenv("KUSTO_DATABASE")
    
    return config

def save_config(config):
    """Save configuration to file"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)
    
    # Also set as environment variables for current session
    if "kusto_cluster" in config:
        os.environ["KUSTO_CLUSTER"] = config["kusto_cluster"]
    if "kusto_database" in config:
        os.environ["KUSTO_DATABASE"] = config["kusto_database"]