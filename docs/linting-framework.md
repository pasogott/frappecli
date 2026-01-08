# Linting Framework Research & Decision

**Date:** 2026-01-08  
**Author:** pasogott - Pascal Schott  
**Decision:** Use **Ruff** for linting and formatting

## Executive Summary

After researching modern Python linting and formatting tools compatible with `uv`, we chose **Ruff** as our primary linting and formatting framework. Ruff is a fast, comprehensive Python linter written in Rust that replaces multiple legacy tools.

## Options Considered

### 1. Ruff ⭐ (Selected)

**Pros:**
- ✅ **Extremely fast** - 10-100x faster than alternatives (written in Rust)
- ✅ **All-in-one** - Replaces Black, isort, flake8, pylint, pyupgrade, etc.
- ✅ **Native uv integration** - First-class support in uv ecosystem
- ✅ **Active development** - Backed by Astral (creators of uv)
- ✅ **Modern defaults** - Sensible out-of-the-box configuration
- ✅ **Compatible with Black** - Drop-in replacement for Black formatter
- ✅ **Extensive rule set** - 700+ rules covering security, style, complexity
- ✅ **Great error messages** - Clear, actionable feedback
- ✅ **Auto-fix** - Can automatically fix many issues

**Cons:**
- ⚠️ Relatively new (but rapidly adopted by major projects)
- ⚠️ Some advanced pylint rules not yet implemented

**Installation:**
```bash
uv pip install ruff
```

**Usage:**
```bash
# Format code
uv run ruff format .

# Lint code
uv run ruff check .

# Lint with auto-fix
uv run ruff check --fix .
```

### 2. Black + flake8 + isort (Legacy Standard)

**Pros:**
- ✅ Industry standard for years
- ✅ Very stable and well-tested
- ✅ Extensive plugin ecosystem

**Cons:**
- ❌ Requires multiple tools (3+ packages)
- ❌ Slower performance
- ❌ More configuration needed
- ❌ Fragmented tooling
- ❌ Black development has slowed down

**Verdict:** Replaced by Ruff

### 3. pylint

**Pros:**
- ✅ Very comprehensive rule set
- ✅ Deep static analysis
- ✅ Customizable

**Cons:**
- ❌ Slow on large codebases
- ❌ Complex configuration
- ❌ Many false positives by default
- ❌ Separate tool for formatting still needed

**Verdict:** Ruff covers most important pylint rules

### 4. mypy (Type Checking)

**Status:** **Used in addition to Ruff**

**Pros:**
- ✅ Industry standard for type checking
- ✅ Catches type-related bugs
- ✅ Complements linting tools

**Cons:**
- ⚠️ Only checks types, not style/security
- ⚠️ Requires type stubs for third-party libraries

**Usage:**
```bash
uv run mypy src/
```

**Decision:** Use mypy alongside Ruff for complete coverage

## Our Configuration

### pyproject.toml

```toml
[tool.ruff]
line-length = 100
target-version = "py312"
src = ["src"]

[tool.ruff.lint]
select = [
    "E",     # pycodestyle errors
    "W",     # pycodestyle warnings
    "F",     # pyflakes
    "I",     # isort
    "B",     # flake8-bugbear
    "C4",    # flake8-comprehensions
    "UP",    # pyupgrade
    "N",     # pep8-naming
    "S",     # flake8-bandit (security)
    "A",     # flake8-builtins
    "T20",   # flake8-print
    "SIM",   # flake8-simplify
    "ARG",   # flake8-unused-arguments
    "PTH",   # flake8-use-pathlib
    "PL",    # pylint
    "RUF",   # ruff-specific rules
]

ignore = [
    "E501",    # line too long (handled by formatter)
    "S101",    # use of assert (ok in tests)
    "T201",    # print statements (ok in CLI)
]

[tool.ruff.lint.per-file-ignores]
"tests/**/*.py" = [
    "S101",    # assert allowed in tests
    "ARG",     # unused arguments ok in tests
]
```

### What Each Rule Set Does

| Rule Set | Replaces | Purpose |
|----------|----------|---------|
| E, W | pycodestyle | PEP 8 style violations |
| F | pyflakes | Logical errors, unused imports |
| I | isort | Import sorting |
| B | flake8-bugbear | Likely bugs and design problems |
| C4 | flake8-comprehensions | Better list/dict comprehensions |
| UP | pyupgrade | Modern Python syntax |
| N | pep8-naming | Naming conventions |
| S | bandit | Security issues |
| A | flake8-builtins | Shadowing built-ins |
| T20 | flake8-print | Print statement detection |
| SIM | flake8-simplify | Code simplification |
| ARG | flake8-unused-arguments | Unused function arguments |
| PTH | flake8-use-pathlib | pathlib usage |
| PL | pylint | Various pylint rules |
| RUF | - | Ruff-specific rules |

### Type Checking with mypy

```toml
[tool.mypy]
python_version = "3.12"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
check_untyped_defs = true
strict_equality = true
```

## Integration Points

### 1. Pre-commit Hooks

`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.8.4
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.13.0
    hooks:
      - id: mypy
```

**Setup:**
```bash
uv pip install pre-commit
pre-commit install
```

**Manual run:**
```bash
pre-commit run --all-files
```

### 2. CI/CD (GitHub Actions)

`.github/workflows/ci.yml`:
```yaml
- name: Run ruff format check
  run: uv run ruff format --check .

- name: Run ruff linter
  run: uv run ruff check .
```

### 3. Editor Integration

#### VS Code

`settings.json`:
```json
{
  "[python]": {
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll": "explicit",
      "source.organizeImports": "explicit"
    },
    "editor.defaultFormatter": "charliermarsh.ruff"
  },
  "ruff.lint.enable": true,
  "ruff.format.args": ["--line-length", "100"]
}
```

**Extension:** [Ruff VS Code Extension](https://marketplace.visualstudio.com/items?itemName=charliermarsh.ruff)

#### PyCharm / IntelliJ

1. Install Ruff plugin
2. Settings → Tools → Ruff
3. Enable "Run ruff on save"

#### Vim/Neovim

Using `ale` or `nvim-lspconfig` with `ruff-lsp`:
```lua
require('lspconfig').ruff_lsp.setup{}
```

## Development Workflow

### Before Committing

```bash
# Format code
uv run ruff format .

# Fix linting issues
uv run ruff check --fix .

# Check types
uv run mypy src/

# Run tests
uv run pytest
```

### Or use pre-commit (automatic):

```bash
git commit -m "your message"
# Pre-commit hooks run automatically
```

## Performance Comparison

Based on benchmarks from the Ruff project:

| Tool | Time (CPython stdlib) | Speedup |
|------|----------------------|---------|
| Ruff | 0.29s | 1x |
| Flake8 | 34.78s | 120x slower |
| Pylint | 90.63s | 313x slower |

**For our project (~5K-10K LOC expected):**
- Ruff: < 0.1s
- Black + flake8 + isort: ~3-5s
- Full pylint: ~10-15s

## Why Not Just Use Black?

Black is great, but:
1. **Black only formats** - doesn't catch bugs or security issues
2. **Ruff formats + lints** - one tool instead of 3-5
3. **Ruff is faster** - even faster than Black alone
4. **Ruff is compatible** - produces same formatting as Black
5. **Better maintained** - Astral actively develops both uv and Ruff

## Migration from Other Tools

If you're coming from Black + flake8 + isort:

1. Remove old tools:
   ```bash
   uv pip uninstall black flake8 isort
   ```

2. Install Ruff:
   ```bash
   uv pip install ruff
   ```

3. Update `pyproject.toml` (see above)

4. Run once:
   ```bash
   uv run ruff format .
   uv run ruff check --fix .
   ```

5. Update CI/CD workflows

## Security Scanning

Ruff includes security rules from Bandit (S rule set), but we also run standalone Bandit in CI for extra safety:

```bash
uv pip install bandit[toml]
uv run bandit -r src/ -f json -o bandit-report.json
```

## Adoption in the Ecosystem

Major projects using Ruff:
- ✅ FastAPI
- ✅ Pydantic
- ✅ Prefect
- ✅ Apache Airflow
- ✅ Django (testing migration)
- ✅ Pandas (partially adopted)

Astral (Ruff creators) also created:
- ✅ uv (our package manager)
- ✅ ruff-lsp (LSP server)

## Decision Rationale

We chose Ruff because:

1. **Ecosystem alignment** - Same team as uv, tight integration
2. **Speed** - Instant feedback during development
3. **Simplicity** - One tool instead of many
4. **Modern** - Built for Python 3.7+ with modern features
5. **Future-proof** - Active development, growing adoption
6. **Complete** - Covers formatting, linting, security, imports
7. **Compatible** - Works with existing Black/flake8 configs

## Conclusion

**Ruff is the right choice for frappecli in 2026.**

It's fast, comprehensive, well-maintained, and integrates perfectly with our uv-based workflow. The combination of Ruff (linting + formatting) + mypy (type checking) gives us complete coverage without the complexity of multiple tools.

## References

- [Ruff Documentation](https://docs.astral.sh/ruff/)
- [Ruff GitHub](https://github.com/astral-sh/ruff)
- [uv Documentation](https://docs.astral.sh/uv/)
- [Ruff Rules Reference](https://docs.astral.sh/ruff/rules/)
- [Ruff vs Others Benchmark](https://github.com/astral-sh/ruff#how-does-ruff-compare-to-flake8)

## Quick Commands Reference

```bash
# Installation
uv pip install ruff mypy pre-commit

# Format
uv run ruff format .

# Lint
uv run ruff check .

# Lint + fix
uv run ruff check --fix .

# Type check
uv run mypy src/

# Pre-commit setup
pre-commit install
pre-commit run --all-files

# CI commands
uv run ruff format --check .  # Check only, don't format
uv run ruff check .           # Check only, don't fix
uv run pytest --cov           # Run tests with coverage
```
