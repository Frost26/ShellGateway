# Linux Shell Server

A Model Context Protocol (MCP) server that provides Linux CLI access for Claude Dev mode on desktop applications.

## Features

- **Safe Command Execution**: Execute Linux shell commands with proper error handling
- **Directory Management**: Change and track working directories
- **Structured Output**: Clean, parseable output for Claude integration
- **Security Focused**: Runs with user permissions only

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd mcp-linux-shell-server
   ```

2. **Install dependencies**:
   ```bash
   pip install -e .
   ```

3. **Configure Claude Desktop**:
   Add to your Claude Desktop configuration file:
   ```json
   {
     "mcpServers": {
       "linux-shell": {
         "command": "python",
         "args": ["-m", "linux_shell_server.main"],
         "env": {}
       }
     }
   }
   ```

## Testing

### Prerequisites

Before running tests, ensure you have the required test dependencies:

```bash
# Install development dependencies including test tools
pip install -e ".[dev]"

# Or install test dependencies manually
pip install pytest pytest-asyncio pytest-cov
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run tests with coverage report
pytest --cov=linux_shell_server

# Run tests with coverage and generate HTML report
pytest --cov=linux_shell_server --cov-report=html

# Run specific test file
pytest tests/test_main.py

# Run tests matching a pattern
pytest -k "test_execute_command"

# Run tests and stop on first failure
pytest -x
```

### Test Coverage

View coverage reports:
```bash
# Terminal coverage report
pytest --cov=linux_shell_server --cov-report=term-missing

# Generate HTML coverage report (opens in browser)
pytest --cov=linux_shell_server --cov-report=html
open htmlcov/index.html
```

### Continuous Testing

For development, you can run tests automatically on file changes:
```bash
# Install pytest-watch
pip install pytest-watch

# Run tests on file changes
ptw
```

## Usage

Once configured, Claude can execute Linux commands through the following tools:

### Available Tools

- **`execute_command`**: Execute any Linux shell command
  - Parameters: `command` (required), `working_directory` (optional)
  
- **`change_directory`**: Change the current working directory
  - Parameters: `path` (required)
  
- **`get_current_directory`**: Get the current working directory
  - Parameters: none

### Example Interactions

Ask Claude to:
- "List files in the current directory"
- "Check system disk usage with df -h"
- "Navigate to /var/log and show recent entries"
- "Install a package using apt"

## Development

### Setup Development Environment

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black .
ruff check .

# Type checking
mypy .
```

### Project Structure

```
mcp-linux-shell-server/
├── linux_shell_server/
│   ├── __init__.py
│   └── main.py
├── tests/
├── .github/
│   └── copilot-instructions.md
├── .vscode/
│   ├── tasks.json
│   └── mcp.json
├── pyproject.toml
├── README.md
└── LICENSE
```

## Security Considerations

- Commands execute with the same permissions as the server process
- No command filtering or sandboxing is implemented
- Suitable for development environments only
- Consider implementing command whitelisting for production use

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

MIT License


