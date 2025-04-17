#!/usr/bin/env python
"""
Kusto CLI - A command-line tool for querying Azure Data Explorer (Kusto) databases
Integrates with the existing MCP server functionality.

Usage examples:
  # Get schema of a specific table
  python kusto_cli.py schema Scheduled_Maintenance
  
  # Get full database schema
  python kusto_cli.py schema
  
  # Execute a KQL query
  python kusto_cli.py query "Scheduled_Maintenance | order by EndTime desc | take 5"
  
  # Format output as table (default is JSON)
  python kusto_cli.py query --format table "Scheduled_Maintenance | order by EndTime desc | take 5"
  
  # Save query results to a file
  python kusto_cli.py query --output results.json "Scheduled_Maintenance | order by EndTime desc | take 5"
"""

import sys
import os
import json
import argparse
from datetime import datetime
from tabulate import tabulate

# Add the project root to Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    # Import MCP server tools
    from server.main import run_kql_query, get_database_schema, get_table_schema
    from utils.config import load_config
except ImportError as e:
    print(f"Error: Failed to import required modules: {e}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)

def format_output(data, format_type):
    """Format the query results based on the specified format type"""
    if format_type == 'json':
        return json.dumps(data, indent=2, default=str)
    elif format_type == 'table':
        if not data.get('data'):
            return "No data found or error in response."
        
        headers = data['data'][0].keys() if data['data'] else []
        rows = [list(item.values()) for item in data['data']]
        return tabulate(rows, headers=headers, tablefmt='grid')
    else:
        return f"Unsupported format: {format_type}"

def save_output(content, output_file):
    """Save the formatted output to a file"""
    try:
        with open(output_file, 'w') as f:
            f.write(content)
        return f"Results saved to {output_file}"
    except Exception as e:
        return f"Error saving to file: {e}"

def handle_query(args):
    """Handle the 'query' subcommand"""
    try:
        start_time = datetime.now()
        results = run_kql_query(args.query)
        end_time = datetime.now()
        
        if 'error' in results:
            print(f"Error executing query: {results['error']}")
            return 1
            
        formatted_output = format_output(results, args.format)
        print(formatted_output)
        
        if args.output:
            save_message = save_output(formatted_output, args.output)
            print(save_message)
            
        print(f"Query executed in {(end_time - start_time).total_seconds():.2f} seconds")
        return 0
    except Exception as e:
        print(f"Unexpected error executing query: {str(e)}")
        return 1

def handle_schema(args):
    """Handle the 'schema' subcommand"""
    try:
        start_time = datetime.now()
        
        if args.table:
            results = get_table_schema(args.table)
        else:
            results = get_database_schema()
            
        end_time = datetime.now()
        
        if 'error' in results:
            print(f"Error getting schema: {results['error']}")
            return 1
            
        formatted_output = format_output(results, args.format)
        print(formatted_output)
        
        if args.output:
            save_message = save_output(formatted_output, args.output)
            print(save_message)
            
        print(f"Schema retrieved in {(end_time - start_time).total_seconds():.2f} seconds")
        return 0
    except Exception as e:
        print(f"Unexpected error getting schema: {str(e)}")
        return 1

def main():
    """Main function for the Kusto CLI tool"""
    # Load configuration
    config = load_config()
    kusto_cluster = config.get("kusto_cluster")
    kusto_database = config.get("kusto_database")
    
    # Create argument parser
    parser = argparse.ArgumentParser(description="Kusto CLI - Query Azure Data Explorer (Kusto) databases")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Query subcommand
    query_parser = subparsers.add_parser("query", help="Execute a KQL query")
    query_parser.add_argument("query", help="KQL query to execute")
    query_parser.add_argument("--format", choices=["json", "table"], default="json", help="Output format (default: json)")
    query_parser.add_argument("--output", help="Save output to file")
    
    # Schema subcommand
    schema_parser = subparsers.add_parser("schema", help="Get database schema")
    schema_parser.add_argument("table", nargs="?", help="Optional table name to get schema for")
    schema_parser.add_argument("--format", choices=["json", "table"], default="json", help="Output format (default: json)")
    schema_parser.add_argument("--output", help="Save output to file")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Print connection information
    print(f"Connected to Kusto cluster: {kusto_cluster}")
    print(f"Using database: {kusto_database}")
    
    # Execute appropriate command
    if args.command == "query":
        return handle_query(args)
    elif args.command == "schema":
        return handle_schema(args)
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    sys.exit(main())