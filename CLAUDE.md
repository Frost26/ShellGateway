# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Testing
```bash
# Run all tests
python -m pytest tests/

# Run tests with coverage
python -m pytest tests/ --cov=linux_shell_server --cov-report=html

# Run specific test file
python -m pytest tests/test_main.py -v
```

### Code Quality
```bash
# Format code
black linux_shell_server/ tests/

# Check code style
ruff check linux_shell_server/ tests/

# Sort imports
isort linux_shell_server/ tests/

# Type checking
mypy linux_shell_server/
```

### Running the Server
```bash
# Test server directly
python -m linux_shell_server.main
```

## Architecture Overview

This is an MCP (Model Context Protocol) server that provides Linux shell command execution capabilities to Claude Desktop.

### Core Components

**ShellExecutor** (`linux_shell_server/main.py:68-293`):
- Manages command execution with async subprocess calls
- Handles timeouts (30s default, 120s for long commands)
- Maintains working directory state
- Implements command result caching for performance
- Truncates output at 10KB to prevent memory issues

**MCP Protocol Implementation** (`linux_shell_server/main.py:297-428`):
- Three tools: `execute_command`, `change_directory`, `get_current_directory`
- Implements required MCP endpoints: `list_tools`, `list_resources`, `list_prompts`, `call_tool`
- Uses stdio for communication with Claude Desktop

### Key Design Patterns

1. **Process Management**: Creates process groups for proper cleanup on timeout
2. **Error Handling**: All operations return structured error responses
3. **Path Validation**: Directory changes are validated before execution
4. **Async Architecture**: Built on asyncio for non-blocking operations

### Testing Approach

Tests in `tests/test_main.py` cover:
- Command execution success/failure cases
- Directory operations and validation
- MCP protocol handler responses
- Edge cases (empty commands, invalid paths, timeouts)

The test suite uses pytest with asyncio support and aims for high coverage (89% currently).

## Claude Workspace Implementation

### Solution to Directory Path Issues
To address the issue where `~` was being treated as a literal string, the following improvements have been implemented:

1. **Dedicated Claude Workspace**: The server now automatically creates and manages a `/home/rinzler/claude-workspace/` directory:
   - Created on server startup with session-based subdirectories
   - Set as the default working directory for all operations
   - Includes automatic cleanup of sessions older than 7 days

2. **Enhanced Path Expansion**: Both `execute_command` and `change_directory` now properly handle:
   - Tilde expansion (`~` → home directory)
   - Environment variable expansion
   - Relative path resolution

3. **New Tool**: Added `get_workspace_directory` tool that returns the Claude workspace path, providing a reliable location for temporary work

### Available Tools
- `execute_command`: Execute shell commands with optional working directory
- `change_directory`: Change current working directory (with proper path expansion)
- `get_current_directory`: Get current working directory
- `get_workspace_directory`: Get the Claude workspace directory path

### Workspace Structure

```
~/claude-workspace/
├── session-YYYYMMDD-HHMMSS/  # Auto-created session directories
└── ...                        # Older sessions auto-cleaned after 7 days
```

### Implementation Details

The Claude workspace functionality was added to solve the issue where `~` was being treated literally:

1. **ShellExecutor Initialization** (`main.py:75-116`):
   - `_initialize_workspace()` creates the workspace directory on startup
   - Sets `claude-workspace` as the default current directory
   - Creates timestamped session subdirectories
   - `_cleanup_old_files()` removes sessions older than 7 days

2. **Path Expansion Fix** (`main.py:281-288`):
   - `change_directory()` now uses `os.path.expanduser()` and `os.path.expandvars()`
   - Properly handles relative paths from current directory
   - Prevents creation of literal `'~'` directories

3. **New MCP Tool** (`main.py:339-351`, `407-413`, `485-492`):
   - `get_workspace_directory()` method returns workspace path
   - Added to tool list and call handlers
   - Provides reliable way to get workspace location

4. **Configuration Constants** (`main.py:45-47`):
   - `CLAUDE_WORKSPACE_DIR = Path.home() / "claude-workspace"`
   - `WORKSPACE_CLEANUP_DAYS = 7`

This ensures Claude always has a predictable, safe location for temporary work while preventing path expansion issues.
