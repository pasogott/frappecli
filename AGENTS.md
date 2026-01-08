# AGENTS.md

This file provides guidance to AI coding agents when working with this repository.

## Project Overview

`frappecli` is a Python CLI tool for managing Frappe instances via REST API. It provides command-line access to CRUD operations, file management (upload/download), reports, and custom RPC methods across multiple Frappe sites.

**Example Use Cases:**
- Business Apps: Work with any Frappe app (ERPNext, Healthcare, Education, etc.)
- Custom Applications: Manage custom Frappe apps and doctypes
- Automation: Batch operations, scheduled data imports, report generation, webhooks
- Integration: Connect Frappe with external systems, sync data, automated workflows
- DevOps: Site management, data migrations, testing automation

**Tech Stack:** Python 3.12+, Click, requests/httpx, Rich, PyYAML

## Development Environment

This project uses **`uv`** for dependency management following workspace conventions.

### Setup
```bash
# Clone and enter the project
cd /Users/pascal/projects/frappecli

# Install dependencies
uv sync

# Run CLI locally
uv run frappecli --help
```

### Development Commands
```bash
uv run frappecli <command>       # Run CLI during development
uv run pytest tests/ -v          # Run tests with verbose output
uv run ruff check src/           # Lint code
uv run ruff format src/          # Format code
uv pip install -e .              # Install in editable mode
```

## GitHub Workflow (TDD Approach)

**We follow Test-Driven Development and GitHub best practices.**

### Complete Workflow

```
1. Pick Issue → 2. Assign → 3. Branch → 4. Write Tests → 5. Implement 
   → 6. Test → 7. Commit → 8. PR → 9. Review → 10. Merge → Repeat
```

### Step-by-Step Process

#### 1. Pick an Issue

```bash
# View open issues
gh issue list --label "phase-1"

# Pick next issue (e.g., #2 - Configuration Management)
gh issue view 2
```

#### 2. Assign Issue to Yourself

```bash
gh issue edit 2 --add-assignee @me
```

#### 3. Create Feature Branch

```bash
# Branch naming: feature/{issue-number}-{short-description}
git checkout -b feature/2-config-management
```

#### 4. Write Tests FIRST (TDD Red Phase)

**Test-Driven Development:**
1. **Write the test** (it will fail - RED)
2. **Implement the code** (make it pass - GREEN)
3. **Refactor** (improve code - REFACTOR)

```bash
# Create test file first
touch tests/test_config.py

# Write failing tests
cat > tests/test_config.py << 'EOF'
import pytest
from frappecli.config import Config

def test_load_config():
    """Test loading configuration from file."""
    config = Config("tests/fixtures/test_config.yaml")
    assert config.data is not None
    assert "sites" in config.data

def test_env_var_substitution():
    """Test environment variable substitution."""
    import os
    os.environ["TEST_API_KEY"] = "test_key"
    config = Config("tests/fixtures/test_config.yaml")
    site_config = config.get_site_config("test")
    assert site_config["api_key"] == "test_key"
EOF

# Run tests - they should FAIL (RED)
uv run pytest tests/test_config.py -v
```

#### 5. Implement Code (TDD Green Phase)

```bash
# Now create the actual implementation
touch src/frappecli/config.py

# Implement until tests pass
# ... write code ...

# Run tests - they should PASS (GREEN)
uv run pytest tests/test_config.py -v
```

#### 6. Run All Tests

```bash
# Run all tests to ensure nothing broke
uv run pytest tests/ -v

# Check coverage
uv run pytest --cov=src/frappecli --cov-report=term-missing

# Lint and format
uv run ruff format .
uv run ruff check --fix .

# Type check
uv run mypy src/
```

#### 7. Commit with Conventional Commits

```bash
# Stage changes
git add .

# Commit with conventional format
git commit -m "feat(config): implement configuration management with env var substitution

- Add Config class for loading YAML config
- Support ${VAR} environment variable substitution
- Add get_site_config() and list_sites() methods
- Add comprehensive tests with fixtures

Closes #2"
```

#### 8. Push and Create PR

```bash
# Push branch
git push origin feature/2-config-management

# Create PR via GitHub CLI
gh pr create \
  --title "feat(config): implement configuration management" \
  --body "Implements #2

## Changes
- Configuration loading with YAML
- Environment variable substitution
- Multi-site support
- Tests with 100% coverage

## Checklist
- [x] Tests written first (TDD)
- [x] All tests pass
- [x] Code formatted (ruff)
- [x] Type hints added
- [x] Documentation updated" \
  --base main
```

#### 9. Wait for CI and Review

- GitHub Actions runs automatically
- CI checks: lint, test, security
- Self-review or wait for maintainer review
- Address any feedback

#### 10. Merge and Close

```bash
# After approval, merge PR
gh pr merge --squash

# Switch back to main
git checkout main
git pull origin main

# Delete feature branch
git branch -D feature/2-config-management
```

#### 11. Repeat with Next Issue

```bash
# Pick next issue from the list
gh issue list --label "phase-1"

# Start from step 1 again
```

### TDD Best Practices

**Red-Green-Refactor Cycle:**

1. **🔴 RED:** Write a failing test
   ```bash
   # Test doesn't pass yet
   uv run pytest tests/test_client.py::test_get_doctype
   # FAILED - method not implemented
   ```

2. **🟢 GREEN:** Write minimal code to pass
   ```python
   def get_doctype(self, name):
       # Simplest implementation that passes
       return {"name": name}
   ```

3. **🔵 REFACTOR:** Improve code quality
   ```python
   def get_doctype(self, name: str) -> dict:
       """Get doctype information.
       
       Args:
           name: Doctype name
           
       Returns:
           Doctype metadata
       """
       response = self._make_request("GET", f"/api/resource/DocType/{name}")
       return response.json()["message"]
   ```

**TDD Benefits:**
- ✅ Confidence in code (tests prove it works)
- ✅ Better design (testable code is good code)
- ✅ Documentation (tests show how to use it)
- ✅ Regression prevention (tests catch breaks)
- ✅ Easier refactoring (tests verify behavior)

### Issue Management

**Labels for Issues:**
- `phase-1`, `phase-2`, `phase-3`, `phase-4`, `phase-5`
- `config`, `client`, `cli`, `crud`, `files`, `reports`
- `tdd` - Test-Driven Development
- `bug` - Bug fixes
- `enhancement` - New features
- `documentation` - Docs updates

**Milestones:**
- Phase 1: Foundation
- Phase 2: CRUD Operations
- Phase 3: File Management
- Phase 4: Reports & RPC
- Phase 5: Polish & Release

### Branch Naming

```
feature/{issue-number}-{short-description}
fix/{issue-number}-{short-description}
docs/{issue-number}-{short-description}
test/{issue-number}-{short-description}
```

**Examples:**
- `feature/2-config-management`
- `feature/3-api-client`
- `fix/15-file-upload-spaces`
- `docs/23-update-readme`

### PR Best Practices

1. **One issue per PR** - Keep PRs focused
2. **Reference issue** - Use "Closes #X" in description
3. **Add checklist** - Tests, linting, docs
4. **Squash merge** - Keep main branch clean
5. **Delete branch** - After merge

### Example Complete Cycle

```bash
# 1. Pick issue
gh issue view 3
gh issue edit 3 --add-assignee @me

# 2. Create branch
git checkout -b feature/3-api-client

# 3. TDD: Write tests first
cat > tests/test_client.py << 'EOF'
def test_client_initialization():
    client = FrappeClient("https://example.com", "key", "secret")
    assert client.base_url == "https://example.com"
    assert "Authorization" in client.session.headers
EOF

# 4. Run tests (RED)
uv run pytest tests/test_client.py -v
# FAILED

# 5. Implement
cat > src/frappecli/client.py << 'EOF'
class FrappeClient:
    def __init__(self, base_url, api_key, api_secret):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"token {api_key}:{api_secret}"
EOF

# 6. Run tests (GREEN)
uv run pytest tests/test_client.py -v
# PASSED

# 7. Run all tests
uv run pytest tests/ -v --cov

# 8. Commit
git add .
git commit -m "feat(client): implement Frappe API client

- Add FrappeClient class with authentication
- Support for token-based auth header
- Session management for all requests
- Add comprehensive tests

Closes #3"

# 9. Push and PR
git push origin feature/3-api-client
gh pr create --title "feat(client): implement Frappe API client" --base main

# 10. After merge
git checkout main
git pull origin main
git branch -D feature/3-api-client

# 11. Next issue
gh issue list --label "phase-1"
```

## Project Structure

```
frappecli/
├── AGENTS.md              # This file
├── README.md              # User documentation
├── pyproject.toml         # UV project config
├── .python-version        # Python version (3.12+)
├── src/
│   └── frappecli/
│       ├── __init__.py
│       ├── cli.py          # Main CLI entry point (Click)
│       ├── client.py       # Frappe API client
│       ├── config.py       # Config file management
│       └── commands/
│           ├── __init__.py
│           ├── site.py      # Site info, doctypes list, status
│           ├── doctypes.py  # CRUD commands (list, get, create, update, delete)
│           ├── files.py     # File upload/download/management
│           ├── reports.py   # Report execution
│           └── rpc.py       # RPC method calls
└── tests/
    ├── __init__.py
    ├── test_client.py
    ├── test_commands.py
    └── fixtures/
```

## Testing Requirements

- **Framework:** pytest
- **Coverage:** Target 80%+
- **Mocking:** Use `responses` or `httpx-mock` for API calls
- **Test locations:** All tests in `/tests/` directory
- Run before committing: `uv run pytest tests/ -v`

### Critical Test Cases
- Spaces in doctype names and document names (e.g., "Production Order", "Service Contract")
- Special characters in names (Umlauts, ampersands, slashes)
- File uploads (multipart/form-data) with various file types
- Private vs public file handling
- Multi-site configuration
- Error responses from API (404, 403, 500)
- Large file uploads and pagination

## Code Style Guidelines

### Python Standards
- Python 3.12+ features allowed
- **Type hints required** on all functions
- Use `ruff` for linting and formatting (configured in `pyproject.toml`)
- Follow PEP 8 naming conventions
- Prefer functional patterns over classes where appropriate

### Naming Conventions
- Functions and variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private functions: `_leading_underscore`

### Error Handling
- Use Rich for user-facing error messages
- Provide actionable error messages
- Include HTTP status codes in API errors
- Guide users to fix configuration issues

### Security
- Never log API keys or secrets
- Validate file paths (prevent path traversal)
- Warn users when uploading public files
- Support environment variables for credentials

## CLI Design Principles

### 1. Security First
**All uploads are private by default.** Use `--public` flag explicitly for public files.

```bash
frappecli upload file.pdf                    # → Private (default)
frappecli upload logo.png --public           # → Public (explicit)
```

### 2. Quoted Arguments Required
**All doctype and docname arguments must be quoted** to handle spaces and special characters.

```bash
# Correct ✅
frappecli get "Customer" "CUST-001"
frappecli get "Customer" "Müller GmbH & Co. KG"
frappecli upload file.pdf --attach "Legal Case" "Case 2026-001"

# Wrong ❌ (will fail with spaces)
frappecli get Customer Acme Corp
```

### 3. Multi-Site Support
Config file supports multiple Frappe sites:

```yaml
# ~/.config/frappecli/config.yaml
sites:
  production:
    url: https://erp-prod.company.com
    api_key: ${FRAPPE_PROD_API_KEY}
    api_secret: ${FRAPPE_PROD_API_SECRET}
  staging:
    url: https://erp-staging.company.com
    api_key: ${FRAPPE_STAGING_API_KEY}
    api_secret: ${FRAPPE_STAGING_API_SECRET}

default_site: production
```

### 4. Output Formats
Support both JSON and pretty-printed table output:
```bash
frappecli list "Customer" --json           # JSON for piping
frappecli list "Customer" --table          # Pretty table (default)
```

### 5. File Pattern Support
Support `@file.json` syntax for complex data:
```bash
frappecli create "Customer" --data '{"customer_name": "Test"}'
frappecli create "Customer" --data @customer.json
```

## Frappe API Integration

### Authentication
**Method:** API Key + API Secret in Authorization header
```
Authorization: token api_key:api_secret
```

### REST API Endpoints

#### Resource CRUD (Doctypes)
```bash
# List
GET /api/resource/{doctype}?filters={"status":"Active"}&limit=20

# Get
GET /api/resource/{doctype}/{name}

# Create
POST /api/resource/{doctype}
Body: {"customer_name": "Acme Corp", ...}

# Update
PUT /api/resource/{doctype}/{name}
Body: {"mobile": "+43 123 456", ...}

# Delete
DELETE /api/resource/{doctype}/{name}
```

#### File Upload (multipart/form-data)
```bash
POST /api/method/upload_file
Content-Type: multipart/form-data
Authorization: token api_key:api_secret

Form fields:
- file: <binary>
- is_private: "1" (default) or "0"
- folder: "Home" (optional)
- doctype: "Customer" (optional, for attachment)
- docname: "CUST-001" (optional, for attachment)
- fieldname: "image" (optional, for attachment)
- optimize: "1" (optional, for images)
```

#### Get Available Doctypes
```bash
# Get list of all doctypes
GET /api/method/frappe.client.get_list
POST /api/method/frappe.client.get_list
Body: {"doctype": "DocType", "fields": ["name", "module", "custom", "issingle"]}

# Alternative: Get meta information
GET /api/resource/DocType
GET /api/resource/DocType/{doctype_name}
```

#### Response Format
```json
{
  "message": {
    "name": "CUST-001",
    "customer_name": "Acme Corp",
    ...
  }
}
```

## Common Commands

### Site Information
```bash
# List all available doctypes on site
frappecli doctypes
frappecli doctypes --json                    # JSON output
frappecli doctypes --module "Stock"          # Filter by module
frappecli doctypes --custom                  # Only custom doctypes
frappecli doctypes --standard                # Only standard doctypes

# Show doctype details (fields, permissions, etc.)
frappecli doctype-info "Customer"
frappecli doctype-info "Production Order" --fields  # List all fields

# List configured sites
frappecli sites
frappecli sites --show-urls                  # Include URLs

# Site status and version
frappecli status
frappecli status --detailed                  # Include modules, users count
```

### Doctype CRUD
```bash
# List documents
frappecli list "Customer"
frappecli list "Customer" --filters '{"customer_type": "Company"}' --limit 50

# Get single document
frappecli get "Customer" "CUST-001"

# Create document
frappecli create "Customer" --data '{"customer_name": "Acme Corp"}'

# Update document
frappecli update "Customer" "CUST-001" --data '{"mobile": "+43 123"}'

# Delete document
frappecli delete "Customer" "CUST-001"
```

### File Management
```bash
# Upload (private by default)
frappecli upload technical-spec.pdf
frappecli upload blueprint.jpg --attach "Production Order" "PROD-ORD-2026-001"
frappecli upload company-logo.png --public --folder "Assets"

# Download
frappecli download /files/technical-spec.pdf -o local.pdf

# List files
frappecli files list --folder "Home"
frappecli files search "specification"

# Bulk upload
frappecli bulk-upload ./quality-reports/*.pdf --folder "QA Documents"
```

## Frappe-Specific Notes

### Doctype Naming
- Frappe uses spaces in doctype names: `"User"`, `"Email Queue"`, `"Custom Field"`
- Apps add their own doctypes with spaces: `"Sales Invoice"`, `"ToDo"`, `"Web Page"`
- Document names can contain spaces, special chars: `"Administrator"`, `"Project-2026"`
- Always quote arguments in CLI to prevent parsing errors

### File System
- **Private files**: `/private/files/` (requires authentication)
- **Public files**: `/files/` (no authentication)
- File documents stored in `File` doctype
- Content hash used for deduplication
- Files can be organized in folders

### Attachment System
- Files can be attached to any doctype
- Attachment fields: `attached_to_doctype`, `attached_to_name`, `attached_to_field`
- Multiple files per document allowed
- Attachments are versioned with document

### Core Frappe Doctypes
- User Management: `User`, `Role`, `Permission`, `User Type`
- Documents: `File`, `Comment`, `Version`, `Activity Log`
- System: `DocType`, `Custom Field`, `Print Format`, `Report`
- Communication: `Email Account`, `Email Queue`, `Notification`
- Workflow: `Workflow`, `Workflow State`, `Workflow Action`

### App-Specific Doctypes
Frappe apps (ERPNext, Healthcare, Education, etc.) add their own doctypes:
- Use `frappecli doctypes --module "ModuleName"` to filter by app/module
- Example modules: Core, Desk, Website, Setup, Integrations

### Custom Doctypes
- Create custom doctypes for your specific business needs
- Use `frappecli doctypes --custom` to list only custom doctypes
- Custom workflows, forms, and business logic
- Integration points with external systems

## Dependencies

Key dependencies in `pyproject.toml`:
```toml
[project]
dependencies = [
    "click>=8.1.7",        # CLI framework
    "requests>=2.31.0",    # HTTP client (or httpx)
    "pyyaml>=6.0.1",       # Config file parsing
    "rich>=13.7.0",        # Terminal output
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",       # Testing
    "ruff>=0.6.0",         # Linting and formatting
    "responses>=0.25.0",   # HTTP mocking
]
```

## Environment Variables

```bash
# Site credentials (used if not in config.yaml)
FRAPPE_URL=https://erp.example.com
FRAPPE_API_KEY=your_api_key
FRAPPE_API_SECRET=your_api_secret

# Config file location (optional override)
FRAPPECLI_CONFIG=~/.config/frappecli/config.yaml
```

## Pull Request Workflow

### Before Committing
1. Run tests: `uv run pytest tests/ -v`
2. Run linter: `uv run ruff check src/`
3. Format code: `uv run ruff format src/`
4. Update AGENTS.md and README.md if needed

### Commit Message Format
Follow conventional commits:
```
feat(files): add bulk upload command
fix(client): handle connection timeout gracefully
docs: update installation instructions
test(commands): add tests for quoted arguments
```

### PR Title Format
`[component] Description`
Examples:
- `[files] Add bulk upload support`
- `[client] Fix multipart form data encoding`
- `[docs] Update CLI examples in README`

## Related Projects

- **frappe-bench skill** (`/Users/pascal/projects/agent-scripts/skills/frappe-bench/`):
  - For Frappe installation and development operations
  - Commands: `bench init`, `bench get-app`, `bench migrate`
  - Separate scope: frappecli = business ops, frappe-bench = dev/admin

## Documentation

- `README.md` - User-facing documentation and installation guide
- `AGENTS.md` - This file, for AI agents
- Main workspace `CLAUDE.md` - `/Users/pascal/projects/CLAUDE.md`
- Frappe Framework repository - https://github.com/frappe/frappe
- Frappe documentation - https://docs.frappe.io/framework
- Frappe API docs - https://docs.frappe.io/framework/user/en/api
- Frappe REST API reference - https://docs.frappe.io/framework/user/en/api/rest

## Future Enhancements

Potential features to consider:
- [ ] Interactive REPL mode (`frappecli shell`)
- [ ] Watch mode for live updates (`frappecli watch "Customer"`)
- [ ] Bulk operations via CSV import/export
- [ ] Workflow action commands
- [ ] Bash/Zsh completion scripts
- [ ] Plugin system for custom commands
- [ ] Sync with local SQLite for offline work
