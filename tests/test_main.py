"""Tests for the Linux Shell Server MCP implementation"""

import pytest
import asyncio
import json
import sys
import os
from unittest.mock import AsyncMock, patch, MagicMock

# Add the parent directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from linux_shell_server.main import ShellExecutor, handle_list_tools, handle_call_tool


class TestShellExecutor:
    """Test cases for ShellExecutor class"""
    
    def test_init(self):
        """Test ShellExecutor initialization"""
        executor = ShellExecutor()
        assert executor.current_directory is not None
        # Check if it's a valid path
        assert os.path.exists(executor.current_directory)
    
    def test_get_current_directory(self):
        """Test getting current directory"""
        executor = ShellExecutor()
        result = executor.get_current_directory()
        
        assert result["error"] is False
        assert "Current directory:" in result["output"]
        assert executor.current_directory in result["output"]
    
    @pytest.mark.asyncio
    async def test_change_directory_success(self):
        """Test successful directory change"""
        executor = ShellExecutor()
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = await executor.change_directory(temp_dir)
            
            assert result["error"] is False
            assert f"Changed directory to: {temp_dir}" in result["output"]
            assert executor.current_directory == temp_dir
    
    @pytest.mark.asyncio
    async def test_change_directory_not_exists(self):
        """Test changing to non-existent directory"""
        executor = ShellExecutor()
        result = await executor.change_directory("/this/path/does/not/exist")
        
        assert result["error"] is True
        assert "does not exist" in result["output"]
    
    @pytest.mark.asyncio
    async def test_change_directory_not_directory(self):
        """Test changing to a file instead of directory"""
        executor = ShellExecutor()
        import tempfile
        
        with tempfile.NamedTemporaryFile() as temp_file:
            result = await executor.change_directory(temp_file.name)
            
            assert result["error"] is True
            assert ("does not exist" in result["output"] or "not a directory" in result["output"])
    
    @pytest.mark.asyncio
    async def test_execute_command_success(self):
        """Test successful command execution"""
        executor = ShellExecutor()
        
        # Use a simple command that works on Linux
        result = await executor.execute_command("echo 'Hello World'")
        
        assert result["error"] is False
        assert result["exit_code"] == 0
        assert "Hello World" in result["output"]
        assert "Exit code: 0" in result["output"]
    
    @pytest.mark.asyncio
    async def test_execute_command_error(self):
        """Test command execution with error"""
        executor = ShellExecutor()
        
        result = await executor.execute_command("nonexistent_command_12345")
        
        assert result["error"] is True
        assert result["exit_code"] != 0
        # The error message could be in stdout or stderr, so check both
        assert ("command not found" in result["output"].lower() or 
                "not found" in result["output"].lower() or
                result["exit_code"] != 0)
    
    @pytest.mark.asyncio
    async def test_execute_command_invalid_directory(self):
        """Test command execution with invalid working directory"""
        executor = ShellExecutor()
        
        result = await executor.execute_command("echo test", "/invalid/directory")
        
        assert result["error"] is True
        assert "does not exist" in result["output"]
    
    @pytest.mark.asyncio
    async def test_execute_command_empty(self):
        """Test command execution with empty command"""
        executor = ShellExecutor()
        
        result = await executor.execute_command("")
        
        assert result["error"] is True
        assert "cannot be empty" in result["output"]


class TestMCPHandlers:
    """Test cases for MCP protocol handlers"""
    
    @pytest.mark.asyncio
    async def test_list_tools(self):
        """Test the list_tools handler"""
        tools = await handle_list_tools()
        
        assert len(tools) == 3
        tool_names = [tool.name for tool in tools]
        
        assert "execute_command" in tool_names
        assert "change_directory" in tool_names
        assert "get_current_directory" in tool_names
        
        # Check execute_command tool schema
        execute_tool = next(tool for tool in tools if tool.name == "execute_command")
        assert "command" in execute_tool.inputSchema["properties"]
        assert "working_directory" in execute_tool.inputSchema["properties"]
        assert "command" in execute_tool.inputSchema["required"]
    
    @pytest.mark.asyncio
    async def test_call_tool_get_current_directory(self):
        """Test calling get_current_directory tool"""
        result = await handle_call_tool("get_current_directory", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Current directory:" in result[0].text
    
    @pytest.mark.asyncio
    async def test_call_tool_change_directory(self):
        """Test calling change_directory tool"""
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = await handle_call_tool("change_directory", {"path": temp_dir})
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Changed directory to:" in result[0].text
    
    @pytest.mark.asyncio
    async def test_call_tool_execute_command(self):
        """Test calling execute_command tool"""
        # Reset the global shell executor to a valid directory before running the test
        from linux_shell_server.main import shell_executor
        import os
        shell_executor.current_directory = os.path.expanduser("~")
        
        result = await handle_call_tool("execute_command", {"command": "echo test"})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert ("test" in result[0].text or "Exit code: 0" in result[0].text)
    
    @pytest.mark.asyncio
    async def test_call_tool_execute_command_with_working_dir(self):
        """Test calling execute_command tool with working directory"""
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = await handle_call_tool("execute_command", {
                "command": "pwd", 
                "working_directory": temp_dir
            })
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert temp_dir in result[0].text
    
    @pytest.mark.asyncio
    async def test_call_tool_unknown(self):
        """Test calling unknown tool"""
        result = await handle_call_tool("unknown_tool", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Unknown tool" in result[0].text
    
    @pytest.mark.asyncio
    async def test_call_tool_execute_command_missing_param(self):
        """Test calling execute_command without required command parameter"""
        result = await handle_call_tool("execute_command", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "required" in result[0].text.lower()
    
    @pytest.mark.asyncio
    async def test_call_tool_change_directory_missing_param(self):
        """Test calling change_directory without required path parameter"""
        result = await handle_call_tool("change_directory", {})
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "required" in result[0].text.lower()
