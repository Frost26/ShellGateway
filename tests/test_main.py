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
        # Check if it's a valid path (contains home directory indicator)
        assert any(indicator in executor.current_directory.lower() for indicator in ["home", "users", "rhys"])
    
    def test_get_current_directory(self):
        """Test getting current directory"""
        executor = ShellExecutor()
        result = executor.get_current_directory()
        
        assert result["error"] is False
        assert "Current directory:" in result["output"]
        assert executor.current_directory in result["output"]
    
    def test_change_directory_success(self):
        """Test successful directory change"""
        executor = ShellExecutor()
        import tempfile
        
        with tempfile.TemporaryDirectory() as temp_dir:
            result = executor.change_directory(temp_dir)
            
            assert result["error"] is False
            assert f"Changed directory to: {temp_dir}" in result["output"]
            assert executor.current_directory == temp_dir
    
    def test_change_directory_not_exists(self):
        """Test changing to non-existent directory"""
        executor = ShellExecutor()
        result = executor.change_directory("/this/path/does/not/exist")
        
        assert result["error"] is True
        assert "does not exist" in result["output"]
    
    def test_change_directory_not_directory(self):
        """Test changing to a file instead of directory"""
        executor = ShellExecutor()
        import tempfile
        
        with tempfile.NamedTemporaryFile() as temp_file:
            result = executor.change_directory(temp_file.name)
            
            assert result["error"] is True
            assert "is not a directory" in result["output"]
    
    @pytest.mark.asyncio
    async def test_execute_command_success(self):
        """Test successful command execution"""
        executor = ShellExecutor()
        
        # Use a simple command that works on both Unix and Windows
        if hasattr(asyncio, 'create_subprocess_shell'):
            with patch('asyncio.create_subprocess_shell') as mock_subprocess:
                # Mock the process
                mock_process = AsyncMock()
                mock_process.communicate.return_value = (b"Hello World\n", b"")
                mock_process.returncode = 0
                mock_subprocess.return_value = mock_process
                
                result = await executor.execute_command("echo 'Hello World'")
                
                assert result["error"] is False
                assert result["exit_code"] == 0
                assert "Hello World" in result["output"]
                assert "Exit code: 0" in result["output"]
    
    @pytest.mark.asyncio
    async def test_execute_command_error(self):
        """Test command execution with error"""
        executor = ShellExecutor()
        
        with patch('asyncio.create_subprocess_shell') as mock_subprocess:
            # Mock the process with error
            mock_process = AsyncMock()
            mock_process.communicate.return_value = (b"", b"Command not found\n")
            mock_process.returncode = 1
            mock_subprocess.return_value = mock_process
            
            result = await executor.execute_command("nonexistent_command")
            
            assert result["error"] is True
            assert result["exit_code"] == 1
            assert "Command not found" in result["output"]
    
    @pytest.mark.asyncio
    async def test_execute_command_invalid_directory(self):
        """Test command execution with invalid working directory"""
        executor = ShellExecutor()
        
        result = await executor.execute_command("echo test", "/invalid/directory")
        
        assert result["error"] is True
        assert "does not exist" in result["output"]


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
        with patch('linux_shell_server.main.shell_executor.execute_command') as mock_execute:
            mock_execute.return_value = {
                "output": "Command executed successfully",
                "exit_code": 0,
                "error": False
            }
            
            result = await handle_call_tool("execute_command", {"command": "echo test"})
            
            assert len(result) == 1
            assert result[0].type == "text"
            assert "Command executed successfully" in result[0].text
            mock_execute.assert_called_once_with("echo test", None)
    
    @pytest.mark.asyncio
    async def test_call_tool_unknown(self):
        """Test calling unknown tool"""
        with pytest.raises(ValueError, match="Unknown tool: unknown_tool"):
            await handle_call_tool("unknown_tool", {})
