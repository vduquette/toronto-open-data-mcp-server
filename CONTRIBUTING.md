# Contributing to Toronto Open Data MCP Server

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/vduquette/toronto-open-data-mcp-server.git
   cd toronto-open-data-mcp-server
   ```
3. **Set up development environment**:
   ```bash
   pip install -e ".[test]"
   ```

## Development Workflow

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** following the project conventions

3. **Add tests** for new functionality:
   - Unit tests in `test_toronto_mcp.py`
   - Workflow tests in `test_workflows.py`
   - Integration tests where appropriate

4. **Run the test suite**:
   ```bash
   python run_tests.py --all
   ```

5. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Add feature: description of your changes"
   ```

6. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request** on GitHub

## Code Style

- Follow PEP 8 Python style conventions
- Use descriptive variable and function names
- Add docstrings to all public functions
- Keep functions focused and reasonably sized
- Include type hints where helpful

## Testing Guidelines

- **Unit tests**: Test individual functions with mocked dependencies
- **Integration tests**: Mark with `@pytest.mark.integration` for tests that hit real APIs
- **Coverage**: Aim for good test coverage of new features
- **Documentation**: Update documentation for user-facing changes

### Running Tests

```bash
# Quick unit tests
python run_tests.py

# All tests including integration
python run_tests.py --all

# With coverage
python run_tests.py --coverage
```

## Types of Contributions

### Bug Reports
- Use GitHub Issues
- Include reproduction steps
- Provide relevant environment details
- Include error messages and stack traces

### Feature Requests
- Use GitHub Issues
- Describe the use case
- Explain how it would benefit users
- Consider implementation complexity

### Code Contributions
- Bug fixes
- New features
- Performance improvements
- Documentation improvements
- Test coverage improvements

## API Design Principles

When adding new tools or modifying existing ones:

1. **LLM-Friendly**: Design tools that are easy for LLMs to understand and use
2. **Clear Error Messages**: Provide actionable error messages with suggestions
3. **Collaborative**: Work alongside web search rather than replacing it
4. **Consistent**: Follow existing patterns in tool naming and responses
5. **Documented**: Include clear docstrings explaining tool purpose and usage

## Commit Message Guidelines

- Use clear, descriptive commit messages
- Start with a verb (Add, Fix, Update, Remove, etc.)
- Keep the first line under 50 characters
- Add more detail in the body if needed

Examples:
```
Add support for XLS file detection
Fix error handling in dataset schema tool
Update README with new installation instructions
```

## Release Process

Releases are managed by maintainers:
1. Version bumping in `pyproject.toml`
2. Update CHANGELOG (if we add one)
3. Create GitHub release with notes
4. Publish to PyPI (if applicable)

## Questions?

- Create an issue for bugs or feature requests
- Start a discussion for general questions
- Check existing issues before creating new ones

Thank you for contributing! 🎉 