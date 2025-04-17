#!/usr/bin/env python
"""
Kusto MCP Chat Client

A chat-like interface for interacting with the MCP server providing Azure Data Explorer (Kusto) tools.
This client allows using #sym: syntax directly in a terminal chat interface.
"""

import sys
import os
import json
import re
import logging
import requests
from datetime import datetime
import argparse
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("mcp_client.log"), logging.StreamHandler()]
)
logger = logging.getLogger("kusto_mcp_client")

class MCPChatClient:
    """Chat client for interacting with MCP server that provides Kusto tools"""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.history = []
        self.command_pattern = re.compile(r'#sym:(\w+)(?:\s+(.*))?')
        logger.info(f"Chat client initialized, connecting to server at: {server_url}")
        
        # Print welcome message
        self._print_welcome()
    
    def _print_welcome(self):
        """Print welcome message with instructions"""
        print("\n" + "=" * 80)
        print(f"Kusto MCP Chat Client - {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("=" * 80)
        print("Type your commands using the #sym: syntax. For example:")
        print("  #sym:configure_kusto_connection cluster_url=\"https://yourcluster.kusto.windows.net\" database_name=\"YourDB\"")
        print("  #sym:get_database_schema database=\"YourDB\"")
        print("  #sym:run_kql_query query=\".show tables\"")
        print("\nType 'exit' or 'quit' to exit the chat.")
        print("=" * 80 + "\n")
    
    def parse_params(self, param_str: str) -> Dict[str, Any]:
        """Parse parameters from a command string"""
        if not param_str:
            return {}
        
        params = {}
        # Use regex to handle quoted values correctly
        pattern = r'(\w+)=(?:"([^"]*)"|([^ ]*))'
        matches = re.finditer(pattern, param_str)
        
        for match in matches:
            key = match.group(1)
            # Take quoted value if available, otherwise take unquoted value
            value = match.group(2) if match.group(2) is not None else match.group(3)
            params[key] = value
        
        return params
    
    def call_mcp_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Call an MCP tool with provided parameters"""
        url = f"{self.server_url}/tools"
        
        payload = {
            "name": tool_name,
            "parameters": params
        }
        
        try:
            logger.info(f"Calling tool: {tool_name} with params: {params}")
            response = requests.post(url, json=payload, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error. Is the MCP server running at {self.server_url}?")
            return {"error": f"Cannot connect to MCP server at {self.server_url}. Please make sure it's running."}
        except requests.exceptions.Timeout:
            logger.error("Request timed out. The query might be taking too long.")
            return {"error": "Request timed out. The query might be taking too long."}
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {str(e)}")
            return {"error": f"HTTP error: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}
    
    def format_response(self, response: Dict[str, Any]) -> str:
        """Format the response for display"""
        if "error" in response:
            return f"\n❌ ERROR: {response['error']}\n"
        
        try:
            # Pretty print the response
            return "\n" + json.dumps(response, indent=2) + "\n"
        except:
            # Fallback if json formatting fails
            return str(response)
    
    def handle_input(self, user_input: str) -> bool:
        """Process user input and return whether to continue the chat"""
        if user_input.lower() in ["exit", "quit"]:
            print("Goodbye! Exiting chat client...")
            return False
        
        # Check if it's an MCP command
        match = self.command_pattern.match(user_input.strip())
        if match:
            tool_name = match.group(1)
            param_str = match.group(2) or ""
            
            # Parse parameters
            params = self.parse_params(param_str)
            
            # Call the tool
            response = self.call_mcp_tool(tool_name, params)
            
            # Format and print response
            formatted_response = self.format_response(response)
            print(formatted_response)
            
            # Save to history
            self.history.append({
                "input": user_input,
                "response": response
            })
        else:
            # Not a command
            print("\nℹ️  To use MCP tools, start your message with #sym:{tool_name}")
        
        return True
    
    def start_chat(self):
        """Start the chat loop"""
        continue_chat = True
        
        try:
            while continue_chat:
                try:
                    user_input = input("\n> ")
                    continue_chat = self.handle_input(user_input)
                except KeyboardInterrupt:
                    print("\nInterrupted by user. Type 'exit' to quit.")
                    continue
        except Exception as e:
            logger.error(f"Unexpected error in chat loop: {str(e)}")
            print(f"\n❌ An unexpected error occurred: {str(e)}")
        
        print("Chat session ended.")

def main():
    """Main function to start the chat client"""
    parser = argparse.ArgumentParser(description="Chat client for Kusto MCP server")
    parser.add_argument("--server", default="http://localhost:8000", 
                      help="MCP server URL (default: http://localhost:8000)")
    args = parser.parse_args()
    
    client = MCPChatClient(server_url=args.server)
    client.start_chat()

if __name__ == "__main__":
    main()