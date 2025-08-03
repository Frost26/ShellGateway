#!/usr/bin/env python3
"""
MCP Server for Linux Shell Access
Provides tools for executing Linux commands safely through MCP protocol.
Fixed version to handle connection issues properly.
"""

import asyncio
import json
import logging
import subprocess
import sys
import os
import shlex
import shutil
import signal
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple
from mcp.server import Server
from mcp.types import (
    Tool,
    TextContent,
    InitializeResult,
    Resource,
    Prompt
)
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("linux-shell-server")

# Performance Configuration
DEFAULT_TIMEOUT = 30  # Reduced from 200 to 30 seconds
MAX_TIMEOUT = 120     # Reduced from 500 to 120 seconds
MAX_OUTPUT_SIZE = 10000  # Reduced from 50000 to 10000 characters
CACHE_DURATION = 60   # Reduced cache duration

# Commands that typically take longer
LONG_RUNNING_COMMANDS = {'find', 'grep', 'du', 'tar', 'zip', 'rsync', 'cp', 'mv'}
# Commands safe to cache
CACHEABLE_COMMANDS = {'ls', 'pwd', 'whoami', 'id', 'date', 'hostname', 'uname'}

# Claude workspace configuration
CLAUDE_WORKSPACE_DIR = Path.home() / "claude-workspace"
WORKSPACE_CLEANUP_DAYS = 7  # Clean up files older than this

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
        # Initialize claude workspace
        self._initialize_workspace()
        self.current_directory = str(CLAUDE_WORKSPACE_DIR)
        self.cache = CommandCache()
    
    def _initialize_workspace(self):
        """Initialize the Claude workspace directory"""
        try:
            # Create workspace directory if it doesn't exist
            CLAUDE_WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
            logger.info(f"Claude workspace initialized at: {CLAUDE_WORKSPACE_DIR}")
            
            # Clean up old files
            self._cleanup_old_files()
            
            # Create session subdirectory
            session_dir = CLAUDE_WORKSPACE_DIR / f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            session_dir.mkdir(exist_ok=True)
            
        except Exception as e:
            logger.error(f"Failed to initialize workspace: {e}")
            # Fall back to home directory if workspace creation fails
            self.current_directory = os.path.expanduser("~")
    
    def _cleanup_old_files(self):
        """Clean up files older than WORKSPACE_CLEANUP_DAYS"""
        try:
            cutoff_time = datetime.now() - timedelta(days=WORKSPACE_CLEANUP_DAYS)
            
            for item in CLAUDE_WORKSPACE_DIR.iterdir():
                if item.is_dir() and item.name.startswith("session-"):
                    # Check modification time
                    mtime = datetime.fromtimestamp(item.stat().st_mtime)
                    if mtime < cutoff_time:
                        # Remove old session directory
                        shutil.rmtree(item)
                        logger.info(f"Cleaned up old session: {item.name}")
                        
        except Exception as e:
            logger.warning(f"Error during workspace cleanup: {e}")
        
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
        process = None
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
            if process is not None:
                try:
                    if hasattr(os, 'killpg') and hasattr(process, 'pid') and process.pid is not None:
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
                        if process.returncode is None:
                            process.kill()
                except Exception as e:
                    logger.error(f"Error killing process: {e}")
                
                try:
                    await asyncio.wait_for(process.wait(), timeout=5)
                except:
                    pass
            
            raise TimeoutError(f"Command timed out after {timeout} seconds")
        
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            if process is not None:
                try:
                    process.terminate()
                    await asyncio.wait_for(process.wait(), timeout=5)
                except:
                    pass
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
        """Change the current working directory"""
        try:
            # Expand user home directory and environment variables
            expanded_path = os.path.expanduser(os.path.expandvars(path))
            
            # Handle relative paths from current directory
            if not os.path.isabs(expanded_path):
                expanded_path = os.path.join(self.current_directory, expanded_path)
            
            abs_path = os.path.abspath(expanded_path)
            
            # Check if directory exists and is accessible
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
            
            # Try to access the directory
            try:
                os.listdir(abs_path)
            except PermissionError:
                return {
                    "output": f"Error: Permission denied accessing directory '{abs_path}'",
                    "error": True
                }
            except Exception as e:
                return {
                    "output": f"Error: Cannot access directory '{abs_path}': {str(e)}",
                    "error": True
                }
            
            # Change directory
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
        try:
            return {
                "output": f"Current directory: {self.current_directory}",
                "error": False
            }
        except Exception as e:
            logger.error(f"Error getting current directory: {e}")
            return {
                "output": f"Error getting current directory: {str(e)}",
                "error": True
            }
    
    def get_workspace_directory(self) -> Dict[str, Any]:
        """Get the Claude workspace directory"""
        try:
            return {
                "output": f"Claude workspace directory: {CLAUDE_WORKSPACE_DIR}",
                "error": False
            }
        except Exception as e:
            logger.error(f"Error getting workspace directory: {e}")
            return {
                "output": f"Error getting workspace directory: {str(e)}",
                "error": True
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
        ),
        Tool(
            name="get_workspace_directory",
            description="Get the Claude workspace directory (a safe place for temporary work)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        )
    ]

# Add missing MCP endpoints to fix "Method not found" errors
@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available resources - Currently no resources are provided"""
    return []

@server.list_prompts()
async def handle_list_prompts() -> List[Prompt]:
    """List available prompts - Currently no prompts are provided"""
    return []

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> List[types.TextContent]:
    """Handle tool calls with proper error handling"""
    try:
        if name == "execute_command":
            command = arguments.get("command")
            if not command or not isinstance(command, str):
                return [
                    types.TextContent(
                        type="text",
                        text="Error: Command parameter is required and must be a string"
                    )
                ]
            
            working_dir = arguments.get("working_directory")
            if working_dir is not None and not isinstance(working_dir, str):
                return [
                    types.TextContent(
                        type="text",
                        text="Error: Working directory must be a string"
                    )
                ]
            
            result = await shell_executor.execute_command(command, working_dir)
            return [
                types.TextContent(
                    type="text",
                    text=result["output"]
                )
            ]
        
        elif name == "change_directory":
            path = arguments.get("path")
            if not path or not isinstance(path, str):
                return [
                    types.TextContent(
                        type="text",
                        text="Error: Path parameter is required and must be a string"
                    )
                ]
            
            result = await shell_executor.change_directory(path)
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
        
        elif name == "get_workspace_directory":
            result = shell_executor.get_workspace_directory()
            return [
                types.TextContent(
                    type="text",
                    text=result["output"]
                )
            ]
        
        else:
            return [
                types.TextContent(
                    type="text",
                    text=f"Error: Unknown tool '{name}'"
                )
            ]
    
    except Exception as e:
        logger.error(f"Error in handle_call_tool: {e}")
        return [
            types.TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )
        ]

async def main():
    """Main entry point with error handling"""
    try:
        # Run the server using stdin/stdout streams
        from mcp import stdio_server
        
        logger.info("Starting MCP Linux Shell Server...")
        logger.info("Initializing server...")
        
        async with stdio_server() as (read_stream, write_stream):
            logger.info("Server started and connected successfully")
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {e}")
        import traceback
        traceback.print_exc()
        raise

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown completed")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        import sys
        sys.exit(1)