# Contributing to MCP Linux Shell Server

Thank you for your interest in contributing to the MCP Linux Shell Server! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Linux operating system (for testing)

### Development Setup

1. **Fork and clone the repository**:
   ```bash
   git clone https://github.com/yourusername/mcp-linux-shell-server.git
   cd mcp-linux-shell-server
   ```

2. **Create a virtual environment**:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install development dependencies**:
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Install the package in development mode**:
   ```bash
   pip install -e .
   ```

## 📝 Development Guidelines

### Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting
- **Ruff**: Linting and style checking
- **isort**: Import sorting
- **mypy**: Type checking

Run these tools before committing:

```bash
# Format code
black .
isort .

# Check for linting issues
ruff check .

# Type checking
mypy linux_shell_server/
```

### Code Standards

- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Write descriptive docstrings for all public functions and classes
- Keep functions focused and small
- Use meaningful variable and function names

### Testing

All code changes should include appropriate tests:

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=linux_shell_server

# Run specific test file
pytest tests/test_main.py
```

### Git Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the guidelines above

3. **Commit your changes**:
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

4. **Push and create a pull request**:
   ```bash
   git push origin feature/your-feature-name
   ```

### Commit Message Format

We follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

- `feat:` new features
- `fix:` bug fixes
- `docs:` documentation changes
- `test:` adding or updating tests
- `refactor:` code refactoring
- `style:` code style changes
- `chore:` maintenance tasks

## 🐛 Reporting Issues

When reporting issues, please include:

- Your operating system and version
- Python version
- Steps to reproduce the issue
- Expected vs actual behavior
- Any error messages or logs

## 💡 Suggesting Features

We welcome feature suggestions! Please:

- Check if the feature already exists or is planned
- Clearly describe the use case and benefits
- Provide examples of how it would work
- Consider the security implications

## 🔒 Security Considerations

When contributing, keep in mind:

- This tool executes shell commands with user permissions
- Validate input parameters carefully
- Consider potential security risks of new features
- Follow the principle of least privilege

## 📋 Pull Request Process

1. **Ensure all tests pass** and coverage is maintained
2. **Update documentation** if your changes affect usage
3. **Add tests** for new functionality
4. **Follow the code style** guidelines
5. **Write a clear PR description** explaining the changes

### PR Checklist

- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated if needed
- [ ] Commit messages follow conventional format
- [ ] PR description clearly explains changes

## 🤝 Code of Conduct

Be respectful and constructive in all interactions. We want to maintain a welcoming environment for all contributors.

## 📚 Resources

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/create-python-server)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [pytest Documentation](https://docs.pytest.org/)

## ❓ Questions?

If you have questions about contributing, feel free to:

- Open an issue with the `question` label
- Start a discussion in the repository

Thank you for contributing! 🎉
