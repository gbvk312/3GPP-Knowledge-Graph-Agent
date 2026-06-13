# Contributing to 3GPP Knowledge Graph Agent

Thank you for your interest in contributing to this project! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Setting Up the Development Environment](#setting-up-the-development-environment)
- [How to Submit Pull Requests](#how-to-submit-pull-requests)
- [Code Style Guidelines](#code-style-guidelines)
- [Issue Reporting](#issue-reporting)

## Setting Up the Development Environment

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)
- Git

### Setup Steps

1. **Fork the repository** on GitHub.

2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/<your-username>/3GPP-Knowledge-Graph-Agent.git
   cd 3GPP-Knowledge-Graph-Agent
   ```

3. **Create a virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

4. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

5. **Install development dependencies** (if available):
   ```bash
   pip install -r requirements-dev.txt
   ```

6. **Verify your setup** by running the tests:
   ```bash
   pytest
   ```

## How to Submit Pull Requests

1. **Create a new branch** from `master` for your feature or fix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes** and commit them with clear, descriptive commit messages:
   ```bash
   git add .
   git commit -m "Add: brief description of your changes"
   ```

3. **Push your branch** to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```

4. **Open a Pull Request** against the `master` branch of the original repository.

5. **In your PR description**, include:
   - A clear description of the changes
   - The motivation behind the changes
   - Any related issue numbers (e.g., "Fixes #42")
   - Screenshots or examples if applicable

6. **Wait for review.** Maintainers will review your PR and may request changes. Please respond to feedback in a timely manner.

### PR Requirements

- All existing tests must pass
- New features should include appropriate tests
- Code must follow the project's style guidelines
- Documentation should be updated if necessary

## Code Style Guidelines

- Follow [PEP 8](https://peps.python.org/pep-0008/) for Python code style.
- Use meaningful variable and function names.
- Write docstrings for all public modules, classes, and functions using [Google-style docstrings](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings).
- Keep functions focused and concise — each function should do one thing well.
- Use type hints where possible.
- Maximum line length is 120 characters.
- Use `snake_case` for functions and variables, `PascalCase` for classes.
- Organize imports using the standard order: standard library, third-party, local.

## Issue Reporting

When reporting an issue, please include:

1. **A clear and descriptive title.**
2. **Steps to reproduce** the issue.
3. **Expected behavior** — what you expected to happen.
4. **Actual behavior** — what actually happened.
5. **Environment details**:
   - Operating system and version
   - Python version
   - Relevant package versions
6. **Screenshots or logs** if applicable.

### Issue Labels

- `bug` — Something isn't working as expected
- `enhancement` — New feature or improvement request
- `documentation` — Improvements or additions to documentation
- `good first issue` — Good for newcomers to the project

## Questions?

If you have questions about contributing, feel free to open an issue with the `question` label.

Thank you for contributing! 🎉
