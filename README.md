# MCP Linux Shell Server

A Model Context Protocol (MCP) server that provides secure Linux command-line access for Claude Desktop. This server enables Claude to execute shell commands, navigate directories, and interact with the Linux filesystem in a controlled environment.

## 🚀 Features

- **Command Execution**: Run any Linux shell command with proper error handling
- **Directory Navigation**: Change directories and track current working directory
- **Structured Output**: Clean, parseable command output for Claude integration
- **Async Architecture**: Built with modern Python async/await patterns
- **Type Safety**: Full type hints and mypy compatibility
- **Security Focused**: Runs with user-level permissions only

## 📋 Requirements

- Python 3.8 or higher
- Linux operating system
- Claude Desktop application

## 🛠️ Installation

## Local Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Frost26/mcp-linux-shell-server.git
   cd mcp-linux-shell-server
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Linux/macOS
   ```

3. **Install in development mode**:
   ```bash
   pip install -e .
   ```

## ⚙️ Configuration

### Claude Desktop Setup

Add the server to your Claude Desktop configuration file. For detailed configuration instructions, see [CONFIGURATION.md](CONFIGURATION.md).

**Quick Setup:**

1. Copy the example configuration:
   ```bash
   cp claude_desktop_config.example.json ~/.config/claude-desktop/claude_desktop_config.json
   ```

2. Edit the configuration file and update the path to your repository:
   ```bash
   nano ~/.config/claude-desktop/claude_desktop_config.json
   ```

3. Restart Claude Desktop

The configuration file is typically located at:
- **Linux**: `~/.config/claude-desktop/claude_desktop_config.json`

## 🧪 Usage

Once configured and Claude Desktop is restarted, you can interact with your Linux system through Claude using natural language commands.

### Available Tools

The server provides three main tools:

- **`execute_command`**: Execute any Linux shell command
  - Parameters: `command` (required), `working_directory` (optional)
  
- **`change_directory`**: Change the current working directory
  - Parameters: `path` (required)
  
- **`get_current_directory`**: Get the current working directory
  - Parameters: none

### Example Interactions

Try asking Claude:

- "What files are in the current directory?"
- "Show me the disk usage with df -h"
- "Navigate to /var/log and show the latest entries"
- "Check the system uptime"
- "Create a new directory called 'projects'"
- "What's the current working directory?"

## 🧪 Development & Testing

### Development Setup

1. **Clone and setup**:
   ```bash
   git clone https://github.com/yourusername/mcp-linux-shell-server.git
   cd mcp-linux-shell-server
   python3 -m venv venv
   source venv/bin/activate
   ```

2. **Install with development dependencies**:
   ```bash
   pip install -e ".[dev]"
   ```

3. **Code Quality Tools**:
   ```bash
   # Format code
   black .
   
   # Lint code
   ruff check .
   
   # Type checking
   mypy .
   ```

### Testing

Run the test suite to ensure everything works correctly:

```bash
# Run all tests
pytest

# Run tests with verbose output
pytest -v

# Run tests with coverage report
pytest --cov=linux_shell_server --cov-report=term-missing

# Run tests and generate HTML coverage report
pytest --cov=linux_shell_server --cov-report=html
```

### Project Structure

```
mcp-linux-shell-server/
├── linux_shell_server/        # Main package
│   ├── __init__.py
│   └── main.py                # MCP server implementation
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   └── test_main.py
├── pyproject.toml            # Project configuration
├── requirements.txt          # Runtime dependencies
├── requirements-dev.txt      # Development dependencies
├── README.md                 # This file
├── LICENSE                   # MIT License
└── claude_desktop_config.example.json  # Example configuration
```

## 🔒 Security Considerations

⚠️ **Important Security Notes:**

- Commands execute with the same permissions as the server process
- No command filtering or sandboxing is implemented by default
- **Recommended for development environments only**
- For production use, consider implementing:
  - Command whitelisting
  - Directory restrictions
  - Resource limits
  - Audit logging

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

**Quick Start for Contributors:**

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run the test suite**: `pytest`
5. **Format your code**: `black . && ruff check .`
6. **Submit a pull request**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter issues:

1. Check the [Claude Desktop debugging documentation](https://modelcontextprotocol.io/docs/tools/debugging)
2. Review the server logs in Claude Desktop
3. Ensure your virtual environment has all dependencies installed
4. Verify the configuration file syntax

## 📚 Related Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/create-python-server)
- [Claude Desktop Configuration Guide](https://docs.anthropic.com/claude/docs)


