# Kusto MCP Chat Client

A simple chat-like interface for interacting with your MCP (Model Context Protocol) server that provides Azure Data Explorer (Kusto) tools.

## Features

- Interactive chat-like terminal interface
- Support for `#sym:` command syntax
- Error handling and logging
- Pretty-printed JSON responses
- Command history tracking

## Quick Start

### 1. Start your MCP server

First, make sure your MCP server is running. Open a terminal and run:

```bash
python server/main.py
```

This will start your FastMCP server, typically on port 8000.

### 2. Start the chat client

Open another terminal and run:

```bash
python chat_client.py
```

### 3. Use MCP commands

Now you can use the `#sym:` commands directly in the chat interface. Examples:

```
#sym:configure_kusto_connection cluster_url="https://gpucapmonitoringkusto.westus.kusto.windows.net" database_name="gpucapmonitoring"
```

```
#sym:get_database_schema database="Scheduled_Maintenance"
```

```
#sym:run_kql_query query=".show tables"
```

## Command Reference

### 1. Configure Kusto Connection

```
#sym:configure_kusto_connection cluster_url="https://yourcluster.kusto.windows.net" database_name="YourDB"
```

### 2. Get Database Schema

```
#sym:get_database_schema database="YourDB"
```

If you want to use the default database you configured:

```
#sym:get_database_schema
```

### 3. Run KQL Query

```
#sym:run_kql_query query=".show tables" 
```

For a different database than the default:

```
#sym:run_kql_query query=".show tables" database="AnotherDB"
```

## Tips

- Type `exit` or `quit` to exit the chat client
- Press Ctrl+C to interrupt a long-running operation
- Logs are saved to `mcp_client.log` for troubleshooting
- If your server is running on a different port, use: `python chat_client.py --server http://localhost:YOUR_PORT`

## Authentication

The client uses the authentication configured in your MCP server, which relies on:

1. DefaultAzureCredential - Automatically uses available credentials
2. AzureCliCredential - Falls back to Azure CLI login

Make sure you're logged in with `az login` before using Kusto commands.

## Security Best Practices

This client follows Azure best practices:
- No hardcoded credentials
- Uses secure managed identity authentication
- Implements proper error handling and logging
- Sets appropriate timeouts for operations