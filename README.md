# MCP Linux Shell Server

A secure Model Context Protocol (MCP) server that provides Linux shell command execution capabilities for Claude Desktop and other MCP clients.

## Features

- **Safe Shell Execution**: Execute Linux commands with proper error handling
- **Directory Management**: Change and query current working directory
- **MCP Protocol Compliant**: Full compatibility with the Model Context Protocol
- **Async Architecture**: Built with modern async/await patterns
- **Comprehensive Testing**: Well-tested with 89% code coverage

## Prerequisites

- Python 3.8 or higher
- Debian GNU/Linux 12 (bookworm) x86_64 or Later
- Claude Desktop (for integration)
- ** There is no official Claude Desktop app for Linux; the following repository works but is no longer maintained by the creator.
```
https://github.com/aaddrick/claude-desktop-debian
```
## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/Frost26/mcp-linux-shell-server.git
cd mcp-linux-shell-server
```

### 2. Create Virtual Environment

```bash
python3 -m venv mcpEnv
source mcpEnv/bin/activate
```

### 3. Install Dependencies

```bash
# Install core dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### 4. Verify Installation

```bash
# Run tests to ensure everything works
python -m pytest tests/ -v --cov=linux_shell_server
```

## Claude Desktop Configuration

### 1. Locate Your Claude Desktop Config

The configuration file is typically located at:
```bash
~/.config/claude/claude_desktop_config.json
```

### 2. Add MCP Server Configuration

Add the following to your Claude Desktop config file:

```json
{
  "mcpServers": {
    "linux-shell": {
      "command": "/path/to/your/mcp-linux-shell-server/mcpEnv/bin/python",
      "args": [
        "-m",
        "linux_shell_server.main"
      ],
      "env": {
        "PYTHONPATH": "/path/to/your/mcp-linux-shell-server"
      }
    }
  }
}
```

### 3. Update Paths

Replace `/path/to/your/mcp-linux-shell-server` with your actual project directory path.

**Example for this project:**
```json
{
  "mcpServers": {
    "linux-shell": {
      "command": "/home/AI/Documents/CodeProjects/mcp-linux-shell-server/mcpEnv/bin/python",
      "args": [
        "-m",
        "linux_shell_server.main"
      ],
      "env": {
        "PYTHONPATH": "/home/AI/Documents/CodeProjects/mcp-linux-shell-server"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

After updating the configuration, restart Claude Desktop to load the MCP server.

## Available Tools

The MCP server provides three main tools:

| Tool | Description | Parameters |
|------|-------------|------------|
| `execute_command` | Execute shell commands | `command` (string) |
| `change_directory` | Change working directory | `path` (string) |
| `get_current_directory` | Get current working directory | None |

## Development

### Running Tests

```bash
# Run all tests
python -m pytest tests/

# Run with coverage
python -m pytest tests/ --cov=linux_shell_server --cov-report=html

# Run specific test file
python -m pytest tests/test_main.py -v
```

### Code Formatting

```bash
# Format code with Black
black linux_shell_server/ tests/

# Check code style with Ruff
ruff check linux_shell_server/ tests/

# Sort imports with isort
isort linux_shell_server/ tests/
```

### Type Checking

```bash
mypy linux_shell_server/
```

## Security Considerations

- Commands are executed in the context of the user running the MCP server
- No built-in command filtering or sandboxing (use with caution)
- Error outputs are captured and returned safely
- Working directory changes are isolated to the server process


## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Install development dependencies (`pip install -r requirements-dev.txt`)
4. Make your changes
5. Run tests (`python -m pytest`)
6. Format code (`black . && ruff check . && isort .`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## Troubleshooting

### Common Issues

**1. Claude Desktop can't connect to MCP server**
- Verify the paths in your Claude Desktop config are correct
- Check that the virtual environment is properly activated
- Ensure all dependencies are installed

**2. Permission errors when executing commands**
- The MCP server runs with the same permissions as the user
- Ensure the user has appropriate permissions for the commands being executed

**3. Module not found errors**
- Verify `PYTHONPATH` is set correctly in the Claude Desktop config
- Ensure the virtual environment contains all required dependencies

### Debug Mode

To run the server in debug mode for troubleshooting:

```bash
# Activate virtual environment
source mcpEnv/bin/activate

# Run server directly
python -m linux_shell_server.main
```

## Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/create-python-server)
- [Claude Desktop MCP Guide](https://modelcontextprotocol.io/llms-full.txt)

## License

This project is licensed under the MIT License
