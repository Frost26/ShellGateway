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
import signal
import time
from typing import Any, Dict, List, Optional, Sequence, Tuple
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

# Performance Configuration
DEFAULT_TIMEOUT = 30  # seconds
MAX_TIMEOUT = 300     # 5 minutes max for long operations
MAX_OUTPUT_SIZE = 50000  # Maximum characters in output
CACHE_DURATION = 60   # Cache duration in seconds

# Commands that typically take longer
LONG_RUNNING_COMMANDS = {'find', 'grep', 'du', 'tar', 'zip', 'rsync', 'cp', 'mv'}
# Commands safe to cache
CACHEABLE_COMMANDS = {'ls', 'pwd', 'whoami', 'id', 'date', 'hostname', 'uname'}

class CommandCache:
    """Simple cache for command results"""
    def __init__(self, max_age: int = CACHE_DURATION):
        self.cache = {}
        self.max_age = max_age
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        if key in self.cache:
            result, timestamp = self.cache[key]
            if time.time() - timestamp < self.max_age:
                return result
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, result: Dict[str, Any]):
        # Only cache successful results from safe commands
        if not result.get("error", False):
            command_start = key.split()[0] if key.split() else ""
            if command_start in CACHEABLE_COMMANDS:
                self.cache[key] = (result, time.time())

# Create a server instance
server = Server("linux-shell-server")

class ShellExecutor:
    def __init__(self):
        self.current_directory = os.path.expanduser("~")
        self.cache = CommandCache()
        
    def _determine_timeout(self, command: str) -> int:
        """Determine appropriate timeout based on command type"""
        command_parts = command.strip().split()
        if not command_parts:
            return DEFAULT_TIMEOUT
            
        first_command = command_parts[0]
        
        # Check for long-running commands
        if any(cmd in command for cmd in LONG_RUNNING_COMMANDS):
            return MAX_TIMEOUT
        elif first_command in LONG_RUNNING_COMMANDS:
            return MAX_TIMEOUT
        else:
            return DEFAULT_TIMEOUT
    
    def _truncate_output(self, text: str) -> str:
        """Truncate output if it's too long"""
        if len(text) > MAX_OUTPUT_SIZE:
            return text[:MAX_OUTPUT_SIZE] + f"\n... (output truncated, showing first {MAX_OUTPUT_SIZE} characters)"
        return text
    
    async def _execute_with_timeout(self, command: str, cwd: str, timeout: int) -> Tuple[str, str, int]:
        """Execute command with timeout and proper process management"""
        try:
            # Create process with process group for better cleanup
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=cwd,
                preexec_fn=os.setsid if hasattr(os, 'setsid') else None
            )
            
            # Wait for process with timeout
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
            
            return stdout.decode('utf-8', errors='replace'), stderr.decode('utf-8', errors='replace'), process.returncode
            
        except asyncio.TimeoutError:
            logger.warning(f"Command timed out after {timeout}s: {command}")
            
            # Kill the entire process group if possible
            try:
                if hasattr(os, 'killpg') and hasattr(process, 'pid'):
                    os.killpg(os.getpgid(process.pid), signal.SIGTERM)
                    # Give it a moment to terminate gracefully
                    await asyncio.sleep(1)
                    # Force kill if still running
                    try:
                        os.killpg(os.getpgid(process.pid), signal.SIGKILL)
                    except:
                        pass
                else:
                    process.terminate()
                    await asyncio.sleep(1)
                    process.kill()
            except Exception as e:
                logger.error(f"Error killing process: {e}")
            
            try:
                await process.wait()
            except:
                pass
            
            raise TimeoutError(f"Command timed out after {timeout} seconds")
        
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            raise
        
    async def execute_command(self, command: str, working_directory: Optional[str] = None) -> Dict[str, Any]:
        """Execute a shell command safely with performance optimizations"""
        try:
            if not command or not command.strip():
                return {
                    "output": "Error: Command cannot be empty",
                    "exit_code": 1,
                    "error": True
                }
            
            # Use provided working directory or current directory
            cwd = working_directory if working_directory else self.current_directory
            
            # Validate that the directory exists
            if not os.path.exists(cwd):
                return {
                    "output": f"Error: Directory '{cwd}' does not exist",
                    "exit_code": 1,
                    "error": True
                }
            
            # Create cache key
            cache_key = f"{command}:{cwd}"
            
            # Check cache first
            cached_result = self.cache.get(cache_key)
            if cached_result:
                logger.info(f"Returning cached result for: {command}")
                cached_result["output"] += "\n\n[Result from cache]"
                return cached_result
            
            # Determine appropriate timeout
            timeout = self._determine_timeout(command)
            
            # Execute command with timeout
            stdout_text, stderr_text, exit_code = await self._execute_with_timeout(command, cwd, timeout)
            
            # Truncate output if too long
            stdout_text = self._truncate_output(stdout_text)
            stderr_text = self._truncate_output(stderr_text)
            
            # Prepare response
            output_parts = []
            if stdout_text:
                output_parts.append(f"STDOUT:\n{stdout_text}")
            if stderr_text:
                output_parts.append(f"STDERR:\n{stderr_text}")
            
            output_text = "\n\n".join(output_parts) if output_parts else "Command executed with no output"
            output_text += f"\n\nExit code: {exit_code}"
            output_text += f"\nWorking directory: {cwd}"
            
            result = {
                "output": output_text,
                "exit_code": exit_code,
                "error": exit_code != 0
            }
            
            # Cache the result if appropriate
            self.cache.set(cache_key, result)
            
            return result
            
        except TimeoutError as e:
            return {
                "output": f"Error: {str(e)}",
                "exit_code": -1,
                "error": True
            }
        except Exception as e:
            logger.error(f"Unexpected error executing command '{command}': {e}")
            return {
                "output": f"Error executing command: {str(e)}",
                "exit_code": -1,
                "error": True
            }
    
    async def change_directory(self, path: str) -> Dict[str, Any]:
        """Change the current working directory with async validation"""
        try:
            expanded_path = os.path.expanduser(path)
            abs_path = os.path.abspath(expanded_path)
            
            # Use async check if path is accessible
            try:
                # Quick async test by trying to list the directory
                proc = await asyncio.create_subprocess_exec(
                    'test', '-d', abs_path,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL
                )
                await proc.wait()
                
                if proc.returncode != 0:
                    return {
                        "output": f"Error: Directory '{abs_path}' does not exist or is not accessible",
                        "error": True
                    }
            except:
                # Fallback to sync check
                if not os.path.exists(abs_path) or not os.path.isdir(abs_path):
                    return {
                        "output": f"Error: Directory '{abs_path}' does not exist or is not a directory",
                        "error": True
                    }
            
            self.current_directory = abs_path
            return {
                "output": f"Changed directory to: {abs_path}",
                "error": False
            }
            
        except Exception as e:
            logger.error(f"Error changing directory to '{path}': {e}")
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
        result = await shell_executor.change_directory(arguments.get("path"))
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
