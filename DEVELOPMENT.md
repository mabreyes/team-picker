# Development Guide

This guide covers the development setup, pre-commit hooks, and code quality
standards for the Team Picker project.

## Quick Setup

```bash
# 1. Install development dependencies
make install-dev

# 2. Setup pre-commit hooks
make setup-pre-commit

# 3. Verify everything works
make check
```

## Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality and consistency. The
hooks run automatically before each commit and include:

### Python Code Quality

-   **Black**: Code formatting with 88-character line length
-   **isort**: Import sorting compatible with Black
-   **flake8**: Linting for code style and potential errors
-   **mypy**: Static type checking
-   **bandit**: Security vulnerability scanning
-   **safety**: Dependency vulnerability checking
-   **pydocstyle**: Docstring style checking (Google convention)

### JavaScript/CSS/HTML

-   **Prettier**: Code formatting for frontend files
-   Consistent indentation and style across all web assets

### General File Checks

-   **Trailing whitespace removal**
-   **End-of-file newline enforcement**
-   **YAML/JSON syntax validation**
-   **Merge conflict detection**
-   **Large file prevention** (>1MB)
-   **Case conflict detection**
-   **Line ending normalization** (LF)

### Security

-   **detect-secrets**: Prevents accidental commit of secrets
-   **bandit**: Python security linting

### Git Workflow

-   **commitizen**: Enforces conventional commit message format

## Development Workflow

### Initial Setup

```bash
# Clone the repository
git clone https://github.com/mabreyes/team-picker.git
cd team-picker

# Setup development environment
make install-dev
make setup-pre-commit
```

### Daily Development

```bash
# Start development server
make run

# Format code before committing
make format

# Run all quality checks
make check

# Clean up generated files
make clean
```

### Commit Process

The pre-commit hooks will automatically run when you commit:

```bash
git add .
git commit -m "feat: add new team assignment feature"
```

If hooks fail, fix the issues and commit again:

```bash
# Fix any issues reported by the hooks
make format  # Auto-fix formatting issues
# Manually fix any remaining issues

git add .
git commit -m "feat: add new team assignment feature"
```

## Code Quality Standards

### Python Code Style

-   **Line length**: 88 characters (Black default)
-   **Import sorting**: isort with Black profile
-   **Type hints**: Encouraged but not required
-   **Docstrings**: Google style for public functions/classes
-   **Security**: No hardcoded secrets or vulnerable patterns

### JavaScript/CSS Style

-   **Indentation**: 4 spaces for JS, 4 spaces for CSS
-   **Quotes**: Single quotes for JS strings
-   **Line length**: 100 characters for JS, 120 for CSS
-   **Semicolons**: Required in JavaScript

### Commit Message Format

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**

-   `feat`: New feature
-   `fix`: Bug fix
-   `docs`: Documentation changes
-   `style`: Code style changes (formatting, etc.)
-   `refactor`: Code refactoring
-   `test`: Adding or updating tests
-   `chore`: Maintenance tasks

**Examples:**

```
feat: add team size validation
fix: resolve image export memory leak
docs: update installation instructions
style: format JavaScript with prettier
refactor: extract team assignment logic
test: add unit tests for student model
chore: update dependencies
```

## Available Commands

### Setup Commands

```bash
make install          # Install production dependencies
make install-dev      # Install development dependencies
make setup-pre-commit # Install and setup pre-commit hooks
```

### Development Commands

```bash
make run              # Start Flask development server
make test             # Run all tests with coverage
make lint             # Run all linting checks
make format           # Format all code
make check            # Run all quality checks (lint + test)
```

### Maintenance Commands

```bash
make clean            # Clean up generated files
make update-deps      # Update all dependencies
make pre-commit-run   # Run pre-commit on all files
make git-setup        # Configure git for consistent line endings
```

## Troubleshooting

### Pre-commit Hook Failures

**Black formatting issues:**

```bash
make format  # Auto-fix formatting
```

**Import sorting issues:**

```bash
isort .  # Auto-fix import order
```

**Flake8 linting errors:**

-   Fix manually based on error messages
-   Common issues: unused imports, long lines, undefined variables

**MyPy type checking:**

-   Add type hints or use `# type: ignore` comments
-   Install missing type stubs: `pip install types-<package>`

**Security issues (Bandit):**

-   Review and fix security vulnerabilities
-   Use `# nosec` comment for false positives (with justification)

**Prettier formatting:**

```bash
npx prettier --write "static/**/*.{js,css}" "templates/**/*.html"
```

### Skipping Hooks (Emergency Only)

```bash
# Skip all hooks (not recommended)
git commit --no-verify -m "emergency fix"

# Skip specific hooks
SKIP=flake8,mypy git commit -m "work in progress"
```

### Updating Hooks

```bash
make pre-commit-update  # Update to latest hook versions
```

## Testing

### Running Tests

```bash
# Run all tests
make test

# Run specific test file
pytest tests/test_models.py -v

# Run with coverage
pytest --cov=. --cov-report=html
```

### Test Categories

-   **Unit tests**: Test individual functions/classes
-   **Integration tests**: Test component interactions
-   **Slow tests**: Mark with `@pytest.mark.slow`

### Writing Tests

-   Use descriptive test names
-   Follow AAA pattern: Arrange, Act, Assert
-   Use fixtures for common setup
-   Mock external dependencies

## Configuration Files

-   `.pre-commit-config.yaml`: Pre-commit hook configuration
-   `pyproject.toml`: Python tool configuration (Black, isort, pytest, etc.)
-   `.prettierrc.json`: Prettier configuration for frontend files
-   `Makefile`: Development task automation
-   `.gitignore`: Git ignore patterns
-   `.secrets.baseline`: Detect-secrets baseline file

## IDE Integration

### VS Code

Install these extensions for the best experience:

-   Python (Microsoft)
-   Black Formatter
-   isort
-   Prettier
-   GitLens

### PyCharm

-   Enable Black as external tool
-   Configure isort integration
-   Install Prettier plugin

## Continuous Integration

The same quality checks run in CI/CD:

-   All pre-commit hooks
-   Full test suite
-   Security scanning
-   Dependency vulnerability checks

Make sure `make check` passes locally before pushing!
