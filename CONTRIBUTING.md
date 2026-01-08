# Contributing to frappecli

Thank you for your interest in contributing to frappecli! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment.

## Development Setup

### Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) package manager
- Git

### Getting Started

1. **Fork and clone the repository:**

```bash
git clone https://github.com/YOUR_USERNAME/frappecli.git
cd frappecli
```

2. **Install dependencies:**

```bash
uv sync
```

3. **Install pre-commit hooks:**

```bash
uv pip install pre-commit
pre-commit install
```

4. **Verify installation:**

```bash
uv run frappecli --version
uv run pytest
```

## Development Workflow

**We follow Test-Driven Development (TDD) and GitHub best practices.**

### Complete Workflow

```
Pick Issue → Assign → Branch → Write Tests → Implement → Test → PR → Review → Merge
```

### 1. Pick and Assign an Issue

```bash
# View open issues
gh issue list --label "phase-1"

# Pick an issue
gh issue view 2

# Assign to yourself
gh issue edit 2 --add-assignee @me
```

### 2. Create a Feature Branch

```bash
# Branch naming: feature/{issue-number}-{description}
git checkout -b feature/2-config-management
```

Branch naming conventions:
- `feature/{issue-number}-{description}` - New features
- `fix/{issue-number}-{description}` - Bug fixes
- `docs/{issue-number}-{description}` - Documentation changes
- `test/{issue-number}-{description}` - Test improvements

**Examples:**
- `feature/2-config-management`
- `fix/15-handle-spaces-in-names`
- `docs/23-update-api-docs`

### 3. Write Tests FIRST (TDD)

**Test-Driven Development - Red, Green, Refactor:**

1. **🔴 RED:** Write a failing test
2. **🟢 GREEN:** Write minimal code to pass the test
3. **🔵 REFACTOR:** Improve the code

```bash
# Create test file FIRST
touch tests/test_config.py

# Write failing test
cat > tests/test_config.py << 'EOF'
def test_load_config():
    config = Config("test_config.yaml")
    assert config.data is not None
EOF

# Run test - it will FAIL (RED)
uv run pytest tests/test_config.py -v
# FAILED - Config class doesn't exist yet

# Now implement the code
cat > src/frappecli/config.py << 'EOF'
class Config:
    def __init__(self, path):
        self.data = self._load(path)
    
    def _load(self, path):
        # Implementation
        return {}
EOF

# Run test - it should PASS (GREEN)
uv run pytest tests/test_config.py -v
# PASSED

# Refactor if needed (REFACTOR)
# Improve code quality while keeping tests green
```

### 4. Make Your Changes

Follow these guidelines:

#### Code Style

- **Formatting:** Ruff format (100 char line length)
- **Linting:** Ruff with comprehensive rule set
- **Type Hints:** Required on all functions
- **Docstrings:** Required for public APIs (Google style)

Run before committing:
```bash
# Format code
uv run ruff format .

# Fix linting issues
uv run ruff check --fix .

# Check types
uv run mypy src/

# Or let pre-commit do it:
git commit -m "your message"
```

#### Testing

- Write tests for all new features
- Maintain 80%+ code coverage
- Use pytest fixtures for common setup
- Mock external API calls with `responses`

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov

# Run specific test
uv run pytest tests/test_client.py -v

# Run without integration tests
uv run pytest -m "not integration"
```

#### Documentation

- Update README.md for user-facing changes
- Update AGENTS.md for developer context
- Add docstrings for new functions/classes
- Update CHANGELOG.md (see below)

### 3. Commit Your Changes

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

[optional body]

[optional footer]
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
git commit -m "feat(client): add retry logic with exponential backoff"
git commit -m "fix(upload): handle spaces in filenames correctly"
git commit -m "docs: update installation instructions"
git commit -m "test(doctypes): add tests for quoted arguments"
```

### 5. Run All Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Check coverage (should be 80%+)
uv run pytest --cov=src/frappecli --cov-report=term-missing

# All checks must pass
uv run ruff format .
uv run ruff check --fix .
uv run mypy src/
```

### 6. Commit with Conventional Commits

```bash
git add .
git commit -m "feat(config): implement configuration management

- Add Config class with YAML loading
- Support environment variable substitution
- Add multi-site configuration
- Add comprehensive tests

Closes #2"
```

### 7. Push and Create Pull Request

```bash
# Push branch
git push origin feature/2-config-management

# Create PR with GitHub CLI
gh pr create \
  --title "feat(config): implement configuration management" \
  --body "Closes #2

## Changes
- Configuration loading with YAML
- Environment variable substitution
- Multi-site support

## Test Coverage
- 100% coverage for config module
- All tests pass

## Checklist
- [x] Tests written first (TDD)
- [x] All tests pass
- [x] Code formatted
- [x] Type hints added
- [x] Documentation updated" \
  --base main
```

PR should include:
- **Title** - Following conventional commit format
- **Description** - "Closes #X" to link issue
- **Changes** - What was implemented
- **Tests** - Coverage information
- **Checklist** - All requirements met

## Pull Request Guidelines

### PR Checklist

Before submitting, ensure:

- [ ] Code follows style guidelines (ruff format/check pass)
- [ ] Type hints added (mypy passes)
- [ ] Tests written and passing
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
- [ ] Commit messages follow conventional format
- [ ] No merge conflicts with main branch
- [ ] Pre-commit hooks pass

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
How was this tested?

## Checklist
- [ ] Tests pass locally
- [ ] Code follows style guidelines
- [ ] Documentation updated
- [ ] CHANGELOG.md updated
```

### Review Process

1. Automated checks run (CI/CD)
2. Maintainer reviews code
3. Feedback addressed
4. Approved and merged

## Testing Guidelines

### Unit Tests

- Test individual functions/methods
- Mock external dependencies
- Fast execution (< 1s total)

Example:
```python
from frappecli.client import FrappeClient
import responses

@responses.activate
def test_client_get_doctype():
    responses.add(
        responses.GET,
        "https://example.com/api/resource/User/admin",
        json={"message": {"name": "admin"}},
        status=200,
    )
    
    client = FrappeClient("https://example.com", "key", "secret")
    doc = client.get("User", "admin")
    
    assert doc["name"] == "admin"
```

### Integration Tests

- Test command end-to-end
- Mock at HTTP level
- Mark with `@pytest.mark.integration`

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── fixtures/
│   ├── sample_config.yaml
│   └── api_responses.json
├── test_client.py           # Client tests
├── test_config.py           # Config tests
└── test_commands_*.py       # Command tests
```

## Documentation

### Docstrings

Use Google style:

```python
def upload_file(
    file_path: str,
    is_private: bool = True,
    folder: str = "Home"
) -> dict:
    """Upload a file to Frappe.

    Args:
        file_path: Path to file to upload
        is_private: Upload as private file (default: True)
        folder: Target folder name

    Returns:
        Dict with file_url, file_name, and other metadata

    Raises:
        FileNotFoundError: If file_path doesn't exist
        APIError: If upload fails

    Example:
        >>> result = upload_file("doc.pdf", is_private=True)
        >>> print(result['file_url'])
        /private/files/doc-abc123.pdf
    """
```

### CHANGELOG.md

Add entry under "Unreleased" section:

```markdown
## [Unreleased]

### Added
- New `bulk-upload` command for batch file uploads

### Changed
- Improved error messages for authentication failures

### Fixed
- Handle spaces in doctype names correctly

### Deprecated
- Old config format (will be removed in v1.0)
```

## Project Structure

```
frappecli/
├── .github/
│   ├── workflows/          # CI/CD workflows
│   └── ISSUE_TEMPLATE/     # Issue templates
├── docs/
│   ├── plans/              # Implementation plans
│   └── linting-framework.md
├── src/
│   └── frappecli/
│       ├── cli.py          # Main CLI
│       ├── client.py       # API client
│       ├── config.py       # Config management
│       └── commands/       # Command implementations
│           ├── site.py
│           ├── doctypes.py
│           ├── files.py
│           ├── reports.py
│           └── rpc.py
├── tests/                  # Test suite
├── pyproject.toml          # Project config
├── README.md
├── AGENTS.md
├── CONTRIBUTING.md
└── LICENSE
```

## Common Tasks

### Add a New Command

1. Create command in appropriate file under `src/frappecli/commands/`
2. Register in `src/frappecli/cli.py`
3. Write tests in `tests/test_commands_*.py`
4. Update README.md with usage example
5. Add to CHANGELOG.md

Example:
```python
# src/frappecli/commands/doctypes.py
@click.command()
@click.argument("doctype", type=str)
def my_command(doctype: str) -> None:
    """Command description."""
    console.print(f"Processing {doctype}")
```

### Add a New API Endpoint

1. Add method to `FrappeClient` in `src/frappecli/client.py`
2. Add type hints and docstring
3. Write tests with mocked responses
4. Use in command implementation

### Update Dependencies

```bash
# Add new dependency
uv add package-name

# Add dev dependency
uv add --dev package-name

# Update all dependencies
uv sync --upgrade
```

## Getting Help

- **Questions:** Open a [Discussion](https://github.com/pasogott/frappecli/discussions)
- **Bugs:** Open an [Issue](https://github.com/pasogott/frappecli/issues)
- **Chat:** (Coming soon)

## Code Review Guidelines

When reviewing PRs, check for:

1. **Functionality:** Does it work as intended?
2. **Tests:** Are there tests? Do they pass?
3. **Code Quality:** Is it readable and maintainable?
4. **Performance:** Are there any obvious bottlenecks?
5. **Security:** Any security concerns?
6. **Documentation:** Is it documented?

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Recognition

Contributors are recognized in:
- GitHub contributors page
- Release notes
- (Future) CONTRIBUTORS.md file

Thank you for contributing to frappecli! 🚀
