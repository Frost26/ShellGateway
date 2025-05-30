<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# MCP Linux Shell Server - Copilot Instructions

This is an MCP (Model Context Protocol) server project that provides Linux CLI access through the MCP protocol.

## Project Context

- **Project Type**: MCP Server
- **Language**: Python 3.8+
- **Framework**: MCP SDK (Model Context Protocol)
- **Purpose**: Provide safe Linux shell command execution for Claude Dev mode

## Key Guidelines

1. **MCP Protocol Compliance**: Always follow MCP protocol specifications from https://modelcontextprotocol.io/
2. **SDK Reference**: Use the MCP Python SDK reference at https://github.com/modelcontextprotocol/create-python-server
3. **Security First**: Implement proper error handling and input validation for shell commands
4. **Async Programming**: Use async/await patterns throughout the codebase
5. **Type Safety**: Include proper type hints for all functions and methods

## Architecture

- `linux_shell_server/main.py`: Main server implementation with MCP handlers
- `linux_shell_server/__init__.py`: Package initialization
- Tools provided: `execute_command`, `change_directory`, `get_current_directory`

## Code Standards

- Follow PEP 8 style guidelines
- Use Black for code formatting
- Include comprehensive error handling
- Add docstrings for all public functions
- Maintain compatibility with Python 3.8+

## Testing

- Write tests for all shell execution functionality
- Mock subprocess calls in tests
- Test error conditions and edge cases
- Ensure async function testing with pytest-asyncio

## Documentation

You can find more info and examples at https://modelcontextprotocol.io/llms-full.txt
