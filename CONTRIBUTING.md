# Contributing to GV Maker

Thank you for your interest in contributing to GV Maker! This document provides guidelines and instructions for contributing to the project.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct.

## How to Contribute

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes
4. Write tests for your changes
5. Ensure all tests pass
6. Submit a pull request

## Development Setup

1. Clone your fork:
```bash
git clone https://github.com/your-username/gvmaker.git
cd gvmaker
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

4. Install pre-commit hooks:
```bash
pre-commit install
```

## Code Style

We use the following tools to maintain code quality:

- Black for code formatting
- isort for import sorting
- flake8 for linting
- pylint for static analysis

Run these tools before submitting a pull request:

```bash
black .
isort .
flake8
pylint src tests
```

## Testing

We use pytest for testing. Run the tests with:

```bash
pytest
```

## Documentation

- Use docstrings for all public functions and classes
- Follow Google style for docstrings
- Update README.md for significant changes
- Add comments for complex logic

## Pull Request Process

1. Update the README.md with details of changes if needed
2. Update the CHANGELOG.md with a summary of changes
3. The PR must pass all CI checks
4. The PR must be reviewed by at least one maintainer

## Release Process

1. Update version in setup.py
2. Update CHANGELOG.md
3. Create a new release on GitHub
4. Build and upload to PyPI

## Questions?

Feel free to open an issue if you have any questions about contributing. 