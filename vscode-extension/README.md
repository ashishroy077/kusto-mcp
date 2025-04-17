# Copilot MCP Bridge

A VS Code extension that bridges GitHub Copilot Chat with your local MCP (Model Context Protocol) server, allowing you to execute MCP commands directly from Copilot Chat.

## Features

- Execute MCP commands directly from GitHub Copilot Chat using the `#sym:` prefix
- Execute MCP commands via the Command Palette
- Configure your MCP server URL
- View MCP command results in a dedicated output panel

## Prerequisites

- VS Code (version 1.80.0 or higher)
- GitHub Copilot Chat extension installed and activated
- A running MCP server (like your Kusto MCP server)

## Installation

Since this is a custom extension, you'll need to install it manually:

1. Install dependencies:
   ```
   cd vscode-extension
   npm install
   ```

2. Package the extension:
   ```
   npx vsce package
   ```

3. Install the extension in VS Code:
   - Open VS Code
   - Press `Ctrl+Shift+P` to open the Command Palette
   - Type "Extensions: Install from VSIX..." and press Enter
   - Select the `.vsix` file that was created in the previous step

## Usage

### Basic Usage

1. Ensure your MCP server is running (your Kusto MCP server)
2. Configure the server URL if needed (default is http://localhost:8000)
3. Open GitHub Copilot Chat and type an MCP command with the `#sym:` prefix, for example:
   ```
   #sym:get_database_schema database="Scheduled_Maintenance"
   ```
4. The command will be executed against your MCP server and the results will be displayed in the Copilot Chat window

### Available Commands

- `Copilot MCP Bridge: Execute MCP Command` - Opens an input box to run an MCP command
- `Copilot MCP Bridge: Configure MCP Server Connection` - Configure the URL of your MCP server

## Supported MCP Commands

All commands supported by your MCP server can be used with this bridge. For example:

- `#sym:configure_kusto_connection cluster_url="https://yourcluster.kusto.windows.net" database_name="YourDB"`
- `#sym:get_database_schema database="YourDB"`
- `#sym:run_kql_query query=".show tables"`

## Troubleshooting

- Make sure your MCP server is running before executing commands
- Check the VS Code Developer Console (`Help > Toggle Developer Tools`) for any error messages
- Verify that your MCP server URL is correctly configured
- Ensure you're using the correct syntax for MCP commands (`#sym:command_name param="value"`)

## Security Considerations

This extension follows Azure best practices for security:

- No hardcoded credentials
- Relies on the secure authentication set up in your MCP server
- Uses HTTPS for communication if your server supports it
- Implements proper error handling and timeout management