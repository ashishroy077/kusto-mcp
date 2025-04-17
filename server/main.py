import sys
import os

# Add the root directory of the project to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import logging
from azure.identity import AzureCliCredential, DefaultAzureCredential
from azure.kusto.data import KustoConnectionStringBuilder
from utils.config import load_config, save_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("kusto_mcp")

# Initialize the MCP server
from mcp.server.fastmcp import FastMCP

# Load configuration - this will load from .env file
config = load_config()
KUSTO_CLUSTER = config.get("kusto_cluster")
KUSTO_DATABASE = config.get("kusto_database")

# Log the configuration status
if KUSTO_CLUSTER and KUSTO_DATABASE:
    logger.info(f"Kusto configuration loaded: {KUSTO_CLUSTER}, {KUSTO_DATABASE}")
    sys.stderr.write(f"Kusto configuration loaded: {KUSTO_CLUSTER}, {KUSTO_DATABASE}\n")
else:
    logger.warning("Kusto configuration not found. Server will start without Kusto connection.")
    sys.stderr.write("Kusto configuration not found. Server will start without Kusto connection.\n")
    sys.stderr.write("Use the 'configure_kusto_connection' tool in the MCP chat to configure the server.\n")

# Create MCP server
mcp = FastMCP("KustoMCP")

# Define a setup tool for configuring the server
@mcp.tool()
def configure_kusto_connection(cluster_url: str, database_name: str) -> dict:
    """Configure the connection to Azure Data Explorer (Kusto)"""
    config = {
        "kusto_cluster": cluster_url,
        "kusto_database": database_name
    }
    save_config(config)
    
    # Set environment variables for current session
    os.environ["KUSTO_CLUSTER"] = cluster_url
    os.environ["KUSTO_DATABASE"] = database_name
    
    # Initialize the client
    from utils.kusto_client import initialize_client
    success = initialize_client()
    
    if success:
        return {"status": "success", "message": "Kusto connection configured successfully"}
    else:
        return {"status": "error", "message": "Failed to connect to Kusto. Please check the credentials and try again."}

# Define a tool for retrieving the schema of a Kusto database
@mcp.tool()
def get_database_schema(database: str = None) -> dict:
    """Retrieve the schema of a Kusto database."""
    from utils.kusto_client import get_schema
    return get_schema(database)

# Define a tool for getting schema of a specific table
@mcp.tool()
def get_table_schema(table_name: str, database: str = None) -> dict:
    """Retrieve the schema of a specific table in a Kusto database."""
    from utils.kusto_client import get_table_schema
    return get_table_schema(table_name, database)

# Define a tool for running KQL queries with enhanced error handling
@mcp.tool()
def run_kql_query(query: str, database: str = None) -> dict:
    """Run a KQL query against Azure Kusto with enhanced error handling."""
    from utils.kusto_client import execute_query
    return execute_query(query, database)

if __name__ == "__main__":
    # Start the MCP server
    mcp.run()