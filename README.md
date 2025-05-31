# MCP Linux Shell Server

A secure Model Context Protocol (MCP) server that provides Linux shell command execution capabilities for Claude Desktop and other MCP clients.

## 🚀 Features

- **Safe Shell Execution**: Execute Linux commands with proper error handling
- **Directory Management**: Change and query current working directory
- **MCP Protocol Compliant**: Full compatibility with the Model Context Protocol
- **Async Architecture**: Built with modern async/await patterns
- **Comprehensive Testing**: Well-tested with 89% code coverage

## 📋 Prerequisites

- Python 3.8 or higher
- Linux operating system
- Claude Desktop (for integration)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
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

## ⚙️ Claude Desktop Configuration

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
      "command": "/home/rinzler/Documents/CodeProjects/mcp-linux-shell-server/mcpEnv/bin/python",
      "args": [
        "-m",
        "linux_shell_server.main"
      ],
      "env": {
        "PYTHONPATH": "/home/rinzler/Documents/CodeProjects/mcp-linux-shell-server"
      }
    }
  }
}
```

### 4. Restart Claude Desktop

After updating the configuration, restart Claude Desktop to load the MCP server.

## 🔧 Available Tools

The MCP server provides three main tools:

| Tool | Description | Parameters |
|------|-------------|------------|
| `execute_command` | Execute shell commands | `command` (string) |
| `change_directory` | Change working directory | `path` (string) |
| `get_current_directory` | Get current working directory | None |

## 🧪 Development

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

## 🔒 Security Considerations

- Commands are executed in the context of the user running the MCP server
- No built-in command filtering or sandboxing (use with caution)
- Error outputs are captured and returned safely
- Working directory changes are isolated to the server process

## 📁 Project Structure

```
mcp-linux-shell-server/
├── linux_shell_server/
│   ├── __init__.py
│   └── main.py              # Main MCP server implementation
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test configuration
│   └── test_main.py         # Comprehensive tests
├── requirements.txt         # Core dependencies
├── requirements-dev.txt     # Development dependencies
├── claude_desktop_config.example.json # Example config
├── pyproject.toml          # Project configuration
└── README.md
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Install development dependencies (`pip install -r requirements-dev.txt`)
4. Make your changes
5. Run tests (`python -m pytest`)
6. Format code (`black . && ruff check . && isort .`)
7. Commit your changes (`git commit -m 'Add amazing feature'`)
8. Push to the branch (`git push origin feature/amazing-feature`)
9. Open a Pull Request

## 🐛 Troubleshooting

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

## 📚 Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/create-python-server)
- [Claude Desktop MCP Guide](https://modelcontextprotocol.io/llms-full.txt)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Built using the [Model Context Protocol](https://modelcontextprotocol.io/)
- Inspired by the need for safe shell access in AI development workflows
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


