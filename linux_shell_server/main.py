#!/usr/bin/env python3
"""
MCP Server for Linux Shell Access
Provides tools for executing Linux commands safely through MCP protocol.
"""

import asyncio
import json
import logging
import subprocess
import sys
import os
import shlex
from typing import Any, Dict, List, Optional, Sequence
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    InitializeResult
)
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("linux-shell-server")

# Create a server instance
server = Server("linux-shell-server")

class ShellExecutor:
    def __init__(self):
        self.current_directory = os.path.expanduser("~")
        
    async def execute_command(self, command: str, working_directory: Optional[str] = None) -> Dict[str, Any]:
        """Execute a shell command safely"""
        try:
            # Use provided working directory or current directory
            cwd = working_directory if working_directory else self.current_directory
            
            # Validate that the directory exists
            if not os.path.exists(cwd):
                return {
                    "output": f"Error: Directory '{cwd}' does not exist",
                    "exit_code": 1,
                    "error": True
                }
            
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd
            )
            
            stdout, stderr = await process.communicate()
            
            # Decode output
            stdout_text = stdout.decode('utf-8', errors='replace')
            stderr_text = stderr.decode('utf-8', errors='replace')
            
            # Prepare response
            output_parts = []
            if stdout_text:
                output_parts.append(f"STDOUT:\n{stdout_text}")
            if stderr_text:
                output_parts.append(f"STDERR:\n{stderr_text}")
            
            output_text = "\n\n".join(output_parts) if output_parts else "Command executed with no output"
            output_text += f"\n\nExit code: {process.returncode}"
            output_text += f"\nWorking directory: {cwd}"
            
            return {
                "output": output_text,
                "exit_code": process.returncode,
                "error": process.returncode != 0
            }
            
        except Exception as e:
            return {
                "output": f"Error executing command: {str(e)}",
                "exit_code": -1,
                "error": True
            }
    
    def change_directory(self, path: str) -> Dict[str, Any]:
        """Change the current working directory"""
        try:
            expanded_path = os.path.expanduser(path)
            abs_path = os.path.abspath(expanded_path)
            
            if not os.path.exists(abs_path):
                return {
                    "output": f"Error: Directory '{abs_path}' does not exist",
                    "error": True
                }
            
            if not os.path.isdir(abs_path):
                return {
                    "output": f"Error: '{abs_path}' is not a directory",
                    "error": True
                }
            
            self.current_directory = abs_path
            return {
                "output": f"Changed directory to: {abs_path}",
                "error": False
            }
            
        except Exception as e:
            return {
                "output": f"Error changing directory: {str(e)}",
                "error": True
            }
    
    def get_current_directory(self) -> Dict[str, Any]:
        """Get the current working directory"""
        return {
            "output": f"Current directory: {self.current_directory}",
            "error": False
        }

# Create shell executor instance
shell_executor = ShellExecutor()

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="execute_command",
            description="Execute a Linux shell command",
            inputSchema={
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The shell command to execute"
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Working directory for the command (optional)"
                    }
                },
                "required": ["command"]
            }
        ),
        Tool(
            name="change_directory",
            description="Change the current working directory",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The directory path to change to"
                    }
                },
                "required": ["path"]
            }
        ),
        Tool(
            name="get_current_directory",
            description="Get the current working directory",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
    """Handle tool calls"""
    
    if name == "execute_command":
        result = await shell_executor.execute_command(
            arguments.get("command"),
            arguments.get("working_directory")
        )
        return [
            types.TextContent(
                type="text",
                text=result["output"]
            )
        ]
    
    elif name == "change_directory":
        result = shell_executor.change_directory(arguments.get("path"))
        return [
            types.TextContent(
                type="text", 
                text=result["output"]
            )
        ]
    
    elif name == "get_current_directory":
        result = shell_executor.get_current_directory()
        return [
            types.TextContent(
                type="text",
                text=result["output"]
            )
        ]
    
    else:
        raise ValueError(f"Unknown tool: {name}")

async def main():
    """Main entry point"""
    # Run the server using stdin/stdout streams
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
