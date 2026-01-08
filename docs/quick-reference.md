# Quick Reference Card

One-page reference for common tasks and commands.

## Development Commands

```bash
# Setup
uv sync                              # Install dependencies
pre-commit install                   # Setup git hooks

# Development
uv run frappecli --help              # Run CLI
uv run ruff format .                 # Format code
uv run ruff check --fix .            # Lint + fix
uv run mypy src/                     # Type check
uv run pytest                        # Run tests
uv run pytest --cov                  # Tests + coverage

# Pre-commit
pre-commit run --all-files           # Run all hooks manually
git commit -m "message"              # Hooks run automatically

# CI (what GitHub runs)
uv run ruff format --check .         # Check format only
uv run ruff check .                  # Check lint only
```

## File Structure

```
frappecli/
├── src/frappecli/          # Source code
├── tests/                  # Tests
├── docs/                   # Documentation
├── .github/                # GitHub config
│   ├── workflows/          # CI/CD
│   └── ISSUE_TEMPLATE/     # Issue templates
├── pyproject.toml          # Project config
├── .pre-commit-config.yaml # Pre-commit hooks
└── README.md               # User docs
```

## Git Workflow

```bash
# Create branch
git checkout -b feature/name

# Commit (conventional format)
git commit -m "feat(scope): description"
git commit -m "fix(client): handle timeout"
git commit -m "docs: update readme"

# Push and PR
git push origin feature/name
# Create PR on GitHub
```

## Commit Types

| Type | Usage |
|------|-------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation |
| `test` | Tests |
| `refactor` | Refactoring |
| `style` | Formatting |
| `chore` | Maintenance |

## Testing

```bash
# All tests
uv run pytest

# Specific test
uv run pytest tests/test_client.py

# With coverage
uv run pytest --cov

# Verbose
uv run pytest -v

# Stop on first failure
uv run pytest -x

# Skip integration tests
uv run pytest -m "not integration"
```

## Ruff Rules

| Code | Purpose |
|------|---------|
| E, W | PEP 8 style |
| F | Logical errors |
| I | Import sorting |
| B | Bug detection |
| S | Security |
| N | Naming |
| UP | Modern Python |

## mypy Flags

```bash
# Check all
uv run mypy src/

# Ignore missing imports
mypy --ignore-missing-imports

# Show error codes
mypy --show-error-codes
```

## PR Checklist

- [ ] Tests pass
- [ ] Linting clean
- [ ] Type hints added
- [ ] Docs updated
- [ ] CHANGELOG.md updated
- [ ] Conventional commits

## Links

- Repo: https://github.com/pasogott/frappecli
- Frappe: https://github.com/frappe/frappe
- Docs: https://docs.frappe.io/framework
- uv: https://docs.astral.sh/uv/
- Ruff: https://docs.astral.sh/ruff/

## Config Files

| File | Purpose |
|------|---------|
| `pyproject.toml` | Project + tool config |
| `.pre-commit-config.yaml` | Pre-commit hooks |
| `.github/workflows/ci.yml` | CI pipeline |
| `config.yaml` | User config (not in repo) |

## Environment Setup

```bash
# Install uv (if needed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and setup
git clone https://github.com/pasogott/frappecli.git
cd frappecli
uv sync
pre-commit install
```

## Help

- Questions: GitHub Discussions
- Bugs: GitHub Issues
- Docs: README.md, AGENTS.md, CONTRIBUTING.md
