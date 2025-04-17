const vscode = require('vscode');
const axios = require('axios');

/**
 * Main activation function for the extension
 * @param {vscode.ExtensionContext} context 
 */
function activate(context) {
    console.log('Copilot MCP Bridge is now active');

    // Register the command to execute an MCP command
    let executeCommandDisposable = vscode.commands.registerCommand('copilot-mcp-bridge.executeCommand', async () => {
        try {
            // Get user input for the command
            const commandInput = await vscode.window.showInputBox({
                placeHolder: '#sym:command_name param1="value1" param2="value2"',
                prompt: 'Enter MCP command with #sym: prefix'
            });
            
            if (!commandInput) return;
            
            // Check if it's an MCP command
            const commandMatch = commandInput.match(/^#sym:(\w+)(?:\s+(.*))?$/);
            if (!commandMatch) {
                vscode.window.showErrorMessage('Invalid command format. Must start with #sym:');
                return;
            }

            const toolName = commandMatch[1];
            const paramStr = commandMatch[2] || '';
            
            // Parse parameters
            const params = parseParams(paramStr);
            
            // Execute the command
            const result = await callMcpTool(toolName, params);
            
            // Display the result
            const resultPanel = vscode.window.createOutputChannel('MCP Result');
            resultPanel.clear();
            resultPanel.appendLine(JSON.stringify(result, null, 2));
            resultPanel.show();
            
            // Also show a notification
            vscode.window.showInformationMessage(`MCP command executed: ${toolName}`);
            
        } catch (error) {
            vscode.window.showErrorMessage(`Error executing MCP command: ${error.message}`);
        }
    });

    // Register command to configure the server URL
    let configureServerDisposable = vscode.commands.registerCommand('copilot-mcp-bridge.configureServer', async () => {
        try {
            const config = vscode.workspace.getConfiguration('copilotMcpBridge');
            const currentUrl = config.get('serverUrl');
            
            const serverUrl = await vscode.window.showInputBox({
                value: currentUrl,
                placeHolder: 'http://localhost:8000',
                prompt: 'Enter MCP server URL'
            });
            
            if (serverUrl) {
                await config.update('serverUrl', serverUrl, vscode.ConfigurationTarget.Global);
                vscode.window.showInformationMessage(`MCP server URL updated to: ${serverUrl}`);
            }
        } catch (error) {
            vscode.window.showErrorMessage(`Error configuring MCP server: ${error.message}`);
        }
    });

    // Add command to intercept and execute Copilot Chat messages
    let interceptChatDisposable = vscode.commands.registerCommand('github.copilot.interactiveSession.command.executeIntegration', async (args) => {
        // This is a special command that can be registered to intercept Copilot Chat commands
        // Check if the message starts with #sym:
        const message = args.message;
        if (message && message.startsWith('#sym:')) {
            // Extract and execute the MCP command
            const commandMatch = message.match(/^#sym:(\w+)(?:\s+(.*))?$/);
            if (commandMatch) {
                const toolName = commandMatch[1];
                const paramStr = commandMatch[2] || '';
                const params = parseParams(paramStr);
                
                try {
                    const result = await callMcpTool(toolName, params);
                    
                    // Return the result to Copilot Chat
                    return {
                        message: `MCP Result:\n\`\`\`json\n${JSON.stringify(result, null, 2)}\n\`\`\``,
                        messageType: 'answer'
                    };
                } catch (error) {
                    return {
                        message: `Error executing MCP command: ${error.message}`,
                        messageType: 'error'
                    };
                }
            }
        }
        
        // If not an MCP command, continue with normal Copilot behavior
        return undefined;
    });

    context.subscriptions.push(executeCommandDisposable, configureServerDisposable, interceptChatDisposable);
}

/**
 * Parse parameters from a command string
 * @param {string} paramStr - Parameter string in format 'param1="value1" param2="value2"'
 * @returns {Object} - Parsed parameters
 */
function parseParams(paramStr) {
    if (!paramStr) return {};
    
    const params = {};
    const pattern = /(\w+)=(?:"([^"]*)"|([^ ]*))/g;
    let match;
    
    while ((match = pattern.exec(paramStr)) !== null) {
        const key = match[1];
        // Take quoted value if available, otherwise take unquoted value
        const value = match[2] !== undefined ? match[2] : match[3];
        params[key] = value;
    }
    
    return params;
}

/**
 * Call an MCP tool with parameters
 * @param {string} toolName - Name of the tool to call
 * @param {Object} params - Parameters for the tool
 * @returns {Promise<Object>} - Tool execution result
 */
async function callMcpTool(toolName, params) {
    try {
        // Get server URL from configuration
        const config = vscode.workspace.getConfiguration('copilotMcpBridge');
        const serverUrl = config.get('serverUrl');
        
        if (!serverUrl) {
            throw new Error('MCP server URL not configured. Use "Configure MCP Server Connection" command.');
        }
        
        // Prepare request payload
        const url = `${serverUrl}/tools`;
        const payload = {
            name: toolName,
            parameters: params
        };
        
        // Call the MCP server
        const response = await axios.post(url, payload, {
            headers: {
                'Content-Type': 'application/json'
            },
            timeout: 30000 // 30 second timeout
        });
        
        return response.data;
    } catch (error) {
        if (error.response) {
            // Server responded with an error status
            throw new Error(`Server error: ${error.response.status} - ${JSON.stringify(error.response.data)}`);
        } else if (error.request) {
            // Server did not respond
            throw new Error('MCP server not responding. Is it running?');
        } else {
            // Error in making the request
            throw new Error(`Error making request: ${error.message}`);
        }
    }
}

function deactivate() {}

module.exports = {
    activate,
    deactivate
};