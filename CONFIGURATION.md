# Configuration Guide

This guide explains how to configure the MCP Linux Shell Server with Claude Desktop.

## Configuration File Location

The Claude Desktop configuration file is located at:
- **Linux**: `~/.config/claude-desktop/claude_desktop_config.json`

## Configuration Options

### Option 1: Development Installation (Recommended for developers)

Use this configuration when you've cloned the repository and want to run from source:

```json
{
  "mcpServers": {
    "linux-shell": {
      "command": "python3",
      "args": ["-m", "linux_shell_server.main"],
      "env": {
        "PYTHONPATH": "/path/to/your/mcp-linux-shell-server"
      }
    }
  }
}
```

**Important**: Replace `/path/to/your/mcp-linux-shell-server` with the actual path to your cloned repository.

### Option 2: Virtual Environment Installation

If you're using a virtual environment:

```json
{
  "mcpServers": {
    "linux-shell": {
      "command": "/path/to/your/venv/bin/python",
      "args": ["/path/to/mcp-linux-shell-server/linux_shell_server/main.py"]
    }
  }
}
```

### Option 3: Global pip Installation (Future)

When the package is published to PyPI, you can use:

```json
{
  "mcpServers": {
    "linux-shell": {
      "command": "linux-shell-server"
    }
  }
}
```

## Setup Steps

1. **Copy the example configuration**:
   ```bash
   cp claude_desktop_config.example.json ~/.config/claude-desktop/claude_desktop_config.json
   ```

2. **Edit the configuration file**:
   ```bash
   nano ~/.config/claude-desktop/claude_desktop_config.json
   ```

3. **Update the paths** in the configuration to match your system

4. **Restart Claude Desktop** to load the new configuration

## Troubleshooting

### Common Issues

- **ModuleNotFoundError**: Ensure the `PYTHONPATH` is set correctly
- **Command not found**: Verify the Python path is correct
- **Permission denied**: Check file permissions and user access

### Debugging

Check the Claude Desktop logs for error messages. The server should start and remain running (it won't exit on its own).

### Testing the Configuration

You can test if the server starts correctly by running it manually:

```bash
cd /path/to/your/mcp-linux-shell-server
python3 -m linux_shell_server.main
```

The server should start and wait for connections. Press Ctrl+C to stop it.
