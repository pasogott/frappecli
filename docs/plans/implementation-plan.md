# frappecli Implementation Plan

**Version:** 0.1.0  
**Author:** pasogott - Pascal Schott  
**Date:** 2026-01-08  
**Status:** Planning

## Overview

This document outlines the complete implementation plan for `frappecli`, a Python CLI tool for managing Frappe instances via REST API. The plan is organized into phases with user stories, tasks, and acceptance criteria.

## Project Goals

1. **Primary:** Provide a robust CLI for Frappe REST API operations
2. **Secondary:** Support multi-site management and automation workflows
3. **Tertiary:** Enable integration with external systems and DevOps pipelines

## Tech Stack

- **Python:** 3.12+
- **CLI Framework:** Click
- **HTTP Client:** requests
- **Config:** PyYAML
- **Output:** Rich (terminal formatting)
- **Testing:** pytest, responses (HTTP mocking)
- **Linting:** ruff

## Before Starting: Create GitHub Issues

**Before implementing any phase, create GitHub issues for all user stories.**

### Creating Issues

For each user story below:

1. **Open GitHub Issues** in your repository
2. **Use labels:** `enhancement`, `phase-1`, `phase-2`, etc.
3. **Add milestone:** Create milestones for each phase
4. **Template:**
   ```markdown
   **User Story:** [Copy from plan]
   
   **Tasks:**
   - [ ] Task 1
   - [ ] Task 2
   
   **Acceptance Criteria:**
   - Criterion 1
   - Criterion 2
   
   **Files to Create/Modify:**
   - file1.py
   - file2.py
   
   **Phase:** 1
   **Estimate:** [optional]
   ```

### Issue Organization

- **Milestones:** Phase 1, Phase 2, Phase 3, Phase 4, Phase 5
- **Labels:** 
  - `phase-1`, `phase-2`, etc.
  - `config`, `client`, `cli`, `crud`, `files`, `reports`, `testing`
  - `tdd` (Test-Driven Development)
  - `documentation`
- **Projects:** Optional - create GitHub Project board for kanban view

### Example Issues to Create

**Phase 1 Issues:**
1. ✅ #1 - Project Setup (CLOSED - already done)
2. 🔲 #2 - Configuration Management
3. 🔲 #3 - API Client Foundation
4. 🔲 #4 - CLI Entry Point

**Phase 2 Issues:**
5. 🔲 #5 - List Doctypes Command
6. 🔲 #6 - Get Doctype Information
7. 🔲 #7 - List Documents Command
8. 🔲 #8 - Get Single Document
9. 🔲 #9 - Create Document Command
10. 🔲 #10 - Update Document Command
11. 🔲 #11 - Delete Document Command

**Phase 3 Issues:**
12. 🔲 #12 - Basic File Upload
13. 🔲 #13 - Attach File to Document
14. 🔲 #14 - File Download
15. 🔲 #15 - List Files
16. 🔲 #16 - Search Files
17. 🔲 #17 - Bulk Upload

**Phase 4 Issues:**
18. 🔲 #18 - List Reports
19. 🔲 #19 - Execute Report
20. 🔲 #20 - Call RPC Methods
21. 🔲 #21 - Site Status Command

**Phase 5 Issues:**
22. 🔲 #22 - Comprehensive Testing
23. 🔲 #23 - Documentation Polish
24. 🔲 #24 - Error Handling & UX
25. 🔲 #25 - First Release (v0.1.0)

---

## Phase 1: Foundation

**Goal:** Basic project structure, API client, and config management

### User Story 1.1: Project Setup
**As a** developer  
**I want** a properly configured Python project with uv  
**So that** I can start implementing features with proper tooling

**Tasks:**
- [x] Initialize project with uv
- [x] Create pyproject.toml with dependencies
- [x] Add LICENSE (MIT)
- [x] Create README.md
- [x] Create AGENTS.md
- [x] Add .gitignore for Python projects
- [x] Create directory structure (src/, tests/, docs/)
- [x] Initialize git repository
- [x] Create CHANGELOG.md
- [x] Create config.example.yaml
- [x] Create GitHub issue templates
- [x] Create CI/CD workflows
- [x] Create pre-commit hooks
- [x] Create CONTRIBUTING.md
- [x] Create authentication design document

**Acceptance Criteria:**
- `uv sync` installs all dependencies
- `uv run pytest` runs (even with no tests)
- `uv run ruff check` runs without errors
- All documentation files present

**Files to Create:**
```
.gitignore
src/frappecli/__init__.py
tests/__init__.py
tests/conftest.py
```

---

### User Story 1.2: Configuration Management
**As a** user  
**I want** to store my Frappe site credentials in a config file  
**So that** I don't have to pass credentials with every command

**Tasks:**
- [ ] Create `src/frappecli/config.py`
- [ ] Implement YAML config file loading from `~/.config/frappecli/config.yaml`
- [ ] Support environment variable substitution (${VAR_NAME})
- [ ] Implement multi-site configuration
- [ ] Add default site selection
- [ ] Create example config file (`config.example.yaml`)
- [ ] Add config validation (URL format, required fields)
- [ ] Write tests for config loading

**Acceptance Criteria:**
- Config loads from default location
- Environment variables are expanded
- Multiple sites can be configured
- Invalid config shows helpful error messages
- All edge cases tested (missing file, invalid YAML, missing fields)

**Files to Create:**
```
src/frappecli/config.py
config.example.yaml
tests/test_config.py
tests/fixtures/test_config.yaml
```

---

### User Story 1.3: API Client Foundation
**As a** developer  
**I want** a reusable Frappe API client  
**So that** all commands can interact with the API consistently

**Tasks:**
- [ ] Create `src/frappecli/client.py`
- [ ] Implement `FrappeClient` class with session management
- [ ] Add authentication (API Key + Secret in header)
- [ ] Implement base HTTP methods (GET, POST, PUT, DELETE)
- [ ] Add error handling (HTTP errors, connection errors, timeouts)
- [ ] Implement response parsing (extract `message` field)
- [ ] Add retry logic with exponential backoff
- [ ] Write comprehensive tests with mocked responses

**Acceptance Criteria:**
- Client initializes with site URL and credentials
- Authentication header is correctly formatted
- All HTTP methods work correctly
- Errors are caught and re-raised with context
- Retries work for transient failures
- 100% test coverage for client module

**Files to Create:**
```
src/frappecli/client.py
tests/test_client.py
tests/fixtures/api_responses.json
```

---

### User Story 1.4: CLI Entry Point
**As a** user  
**I want** to run `frappecli --help` and see available commands  
**So that** I can discover what the tool can do

**Tasks:**
- [ ] Create `src/frappecli/cli.py`
- [ ] Set up Click application with command groups
- [ ] Add global options (`--site`, `--config`, `--json`, `--verbose`)
- [ ] Implement version display (`--version`)
- [ ] Add help text for main command
- [ ] Set up Rich console for output
- [ ] Create command groups (site, files, reports)
- [ ] Wire up entry point in pyproject.toml

**Acceptance Criteria:**
- `frappecli --help` shows command groups
- `frappecli --version` shows version from pyproject.toml
- Global options work across all commands
- Help text is clear and formatted nicely
- Entry point is installed correctly with `uv pip install -e .`

**Files to Create:**
```
src/frappecli/cli.py
tests/test_cli.py
```

---

## Phase 2: Core CRUD Operations

**Goal:** Implement basic doctype CRUD commands

### User Story 2.1: List Doctypes
**As a** user  
**I want** to see all available doctypes on my Frappe site  
**So that** I know what data I can work with

**Tasks:**
- [ ] Create `src/frappecli/commands/site.py`
- [ ] Implement `doctypes` command
- [ ] Add API call to get DocType list
- [ ] Add filtering options (`--module`, `--custom`, `--standard`)
- [ ] Format output as table (Rich) or JSON
- [ ] Add sorting by name or module
- [ ] Write tests with mocked API responses

**Acceptance Criteria:**
- `frappecli doctypes` lists all doctypes
- `frappecli doctypes --module "Core"` filters by module
- `frappecli doctypes --custom` shows only custom doctypes
- `frappecli doctypes --json` outputs valid JSON
- Table output is properly formatted and readable

**API Endpoint:**
```http
POST /api/method/frappe.client.get_list
Body: {
  "doctype": "DocType",
  "fields": ["name", "module", "custom", "issingle"],
  "limit_page_length": 0
}
```

**Files to Create:**
```
src/frappecli/commands/__init__.py
src/frappecli/commands/site.py
tests/test_commands_site.py
```

---

### User Story 2.2: Get Doctype Information
**As a** user  
**I want** to see detailed information about a specific doctype  
**So that** I know what fields and structure it has

**Tasks:**
- [ ] Implement `doctype-info` command in `site.py`
- [ ] Add API call to get doctype metadata
- [ ] Display fields, field types, and options
- [ ] Show permissions and workflow info
- [ ] Add `--fields` flag to show only field list
- [ ] Format output clearly with Rich
- [ ] Write tests for various doctypes

**Acceptance Criteria:**
- `frappecli doctype-info "User"` shows full doctype info
- `frappecli doctype-info "User" --fields` shows only fields
- Field types and options are displayed
- Handles single doctypes correctly
- Error handling for non-existent doctypes

**API Endpoint:**
```http
GET /api/resource/DocType/{doctype_name}
```

**Files to Update:**
```
src/frappecli/commands/site.py
tests/test_commands_site.py
```

---

### User Story 2.3: List Documents
**As a** user  
**I want** to list documents of a specific doctype  
**So that** I can see what data exists

**Tasks:**
- [ ] Create `src/frappecli/commands/doctypes.py`
- [ ] Implement `list` command
- [ ] Add filtering with `--filters` (JSON)
- [ ] Add field selection with `--fields` (comma-separated)
- [ ] Add pagination with `--limit` and `--offset`
- [ ] Add sorting with `--order-by`
- [ ] Format as table or JSON
- [ ] Handle quoted doctype names
- [ ] Write comprehensive tests

**Acceptance Criteria:**
- `frappecli list "User"` lists all users
- `frappecli list "User" --limit 10` limits results
- `frappecli list "User" --filters '{"enabled": 1}'` filters correctly
- `frappecli list "User" --fields "name,email"` shows only specified fields
- Handles doctypes with spaces in names
- Table output is paginated if too large

**API Endpoint:**
```http
GET /api/resource/{doctype}?filters=...&fields=...&limit_page_length=...
```

**Files to Create:**
```
src/frappecli/commands/doctypes.py
tests/test_commands_doctypes.py
```

---

### User Story 2.4: Get Single Document
**As a** user  
**I want** to retrieve a specific document by name  
**So that** I can view its complete data

**Tasks:**
- [ ] Implement `get` command in `doctypes.py`
- [ ] Add API call to get single document
- [ ] Handle quoted doctype and document names
- [ ] Format output as JSON or pretty-printed dict
- [ ] Add `--raw` flag for unformatted JSON
- [ ] Handle errors (document not found, no permission)
- [ ] Write tests for various scenarios

**Acceptance Criteria:**
- `frappecli get "User" "administrator@example.com"` retrieves document
- Handles names with spaces and special characters
- Shows all fields by default
- `--json` outputs valid JSON for piping
- Clear error messages for non-existent documents

**API Endpoint:**
```http
GET /api/resource/{doctype}/{name}
```

**Files to Update:**
```
src/frappecli/commands/doctypes.py
tests/test_commands_doctypes.py
```

---

### User Story 2.5: Create Document
**As a** user  
**I want** to create a new document via CLI  
**So that** I can automate document creation

**Tasks:**
- [ ] Implement `create` command in `doctypes.py`
- [ ] Accept data via `--data` flag (JSON string or @file.json)
- [ ] Validate required fields before API call
- [ ] Return created document with name
- [ ] Handle validation errors from API
- [ ] Support `--dry-run` flag
- [ ] Write tests with various data inputs

**Acceptance Criteria:**
- `frappecli create "ToDo" --data '{"description": "Test"}'` creates document
- `frappecli create "ToDo" --data @todo.json` reads from file
- Returns document name and confirmation
- Validation errors are displayed clearly
- `--dry-run` shows what would be created without actually creating

**API Endpoint:**
```http
POST /api/resource/{doctype}
Body: {field: value, ...}
```

**Files to Update:**
```
src/frappecli/commands/doctypes.py
tests/test_commands_doctypes.py
tests/fixtures/sample_docs.json
```

---

### User Story 2.6: Update Document
**As a** user  
**I want** to update an existing document  
**So that** I can modify data via automation

**Tasks:**
- [ ] Implement `update` command in `doctypes.py`
- [ ] Accept data via `--data` flag (JSON string or @file.json)
- [ ] Support partial updates (only specified fields)
- [ ] Handle version conflicts
- [ ] Return updated document
- [ ] Add `--dry-run` flag
- [ ] Write tests for various update scenarios

**Acceptance Criteria:**
- `frappecli update "User" "user@example.com" --data '{"enabled": 0}'` updates field
- Partial updates work (don't need all fields)
- Handles document locking and version conflicts
- Clear error messages
- Dry-run shows changes without applying

**API Endpoint:**
```http
PUT /api/resource/{doctype}/{name}
Body: {field: value, ...}
```

**Files to Update:**
```
src/frappecli/commands/doctypes.py
tests/test_commands_doctypes.py
```

---

### User Story 2.7: Delete Document
**As a** user  
**I want** to delete a document  
**So that** I can remove unwanted data

**Tasks:**
- [ ] Implement `delete` command in `doctypes.py`
- [ ] Add confirmation prompt (--yes to skip)
- [ ] Handle linked documents warnings
- [ ] Show success message
- [ ] Handle errors (no permission, linked documents)
- [ ] Write tests including confirmation handling

**Acceptance Criteria:**
- `frappecli delete "ToDo" "TODO-001"` prompts for confirmation
- `frappecli delete "ToDo" "TODO-001" --yes` deletes without prompt
- Shows clear error if deletion not allowed
- Warns about linked documents
- Handles non-existent documents gracefully

**API Endpoint:**
```http
DELETE /api/resource/{doctype}/{name}
```

**Files to Update:**
```
src/frappecli/commands/doctypes.py
tests/test_commands_doctypes.py
```

---

## Phase 3: File Management

**Goal:** Implement complete file upload/download functionality

### User Story 3.1: Upload File (Basic)
**As a** user  
**I want** to upload files to my Frappe site  
**So that** I can store documents and attachments

**Tasks:**
- [ ] Create `src/frappecli/commands/files.py`
- [ ] Implement `upload` command
- [ ] Add multipart/form-data encoding
- [ ] Support `--public` flag (default: private)
- [ ] Add `--folder` option
- [ ] Add `--optimize` flag for images
- [ ] Show upload progress with Rich
- [ ] Return file URL and document name
- [ ] Write tests with file mocking

**Acceptance Criteria:**
- `frappecli upload document.pdf` uploads as private file
- `frappecli upload logo.png --public` uploads as public
- `frappecli upload file.pdf --folder "Documents"` places in folder
- Shows progress bar for large files
- Returns file URL and confirmation
- All uploads are private by default (security)

**API Endpoint:**
```http
POST /api/method/upload_file
Content-Type: multipart/form-data
Fields: file, is_private, folder, optimize
```

**Files to Create:**
```
src/frappecli/commands/files.py
tests/test_commands_files.py
tests/fixtures/sample_file.pdf (small test file)
```

---

### User Story 3.2: Attach File to Document
**As a** user  
**I want** to upload a file and attach it to a specific document  
**So that** files are linked to their related records

**Tasks:**
- [ ] Extend `upload` command with `--attach` option
- [ ] Accept doctype and docname as attach parameters
- [ ] Add optional `--field` parameter
- [ ] Verify document exists before upload
- [ ] Create attachment link
- [ ] Write tests for attachment scenarios

**Acceptance Criteria:**
- `frappecli upload file.pdf --attach "Project" "PROJ-001"` attaches to document
- `frappecli upload img.jpg --attach "User" "admin@x.com" --field "user_image"` sets field
- Verifies document exists before uploading
- Shows attachment confirmation
- Handles errors (document not found, field doesn't exist)

**API Endpoint:**
```http
POST /api/method/upload_file
Fields: file, doctype, docname, fieldname
```

**Files to Update:**
```
src/frappecli/commands/files.py
tests/test_commands_files.py
```

---

### User Story 3.3: Download File
**As a** user  
**I want** to download files from my Frappe site  
**So that** I can retrieve documents locally

**Tasks:**
- [ ] Implement `download` command in `files.py`
- [ ] Support file URL and File doctype name
- [ ] Add `--output` / `-o` flag for destination
- [ ] Show download progress
- [ ] Handle authentication for private files
- [ ] Support batch download with wildcards
- [ ] Write tests for download scenarios

**Acceptance Criteria:**
- `frappecli download /files/doc.pdf -o local.pdf` downloads public file
- `frappecli download /private/files/doc.pdf -o local.pdf` downloads private file
- `frappecli download "FILE-00123" -o doc.pdf` downloads by File doctype name
- Shows progress bar for large files
- Handles download failures gracefully

**API Endpoint:**
```http
GET /api/method/download_file?file_url=/files/...
GET /files/{filename}  (public)
GET /private/files/{filename}  (private, requires auth)
```

**Files to Update:**
```
src/frappecli/commands/files.py
tests/test_commands_files.py
```

---

### User Story 3.4: List Files
**As a** user  
**I want** to list files in a folder  
**So that** I can see what files are stored

**Tasks:**
- [ ] Implement `files list` command
- [ ] Add `--folder` option (default: Home)
- [ ] Add pagination support
- [ ] Show file size, type, upload date
- [ ] Add `--attached-to` filter (doctype + docname)
- [ ] Format as table or JSON
- [ ] Write tests for various filters

**Acceptance Criteria:**
- `frappecli files list` shows files in Home folder
- `frappecli files list --folder "Documents"` shows folder contents
- `frappecli files list --attached-to "Project" "PROJ-001"` shows project files
- Table shows name, size, date, private/public status
- Handles empty folders gracefully

**API Endpoint:**
```http
POST /api/method/frappe.core.api.file.get_files_in_folder
Body: {folder: "Home", start: 0, page_length: 20}
```

**Files to Update:**
```
src/frappecli/commands/files.py
tests/test_commands_files.py
```

---

### User Story 3.5: Search Files
**As a** user  
**I want** to search for files by name  
**So that** I can quickly find specific files

**Tasks:**
- [ ] Implement `files search` command
- [ ] Add text search parameter
- [ ] Show file URL, size, type
- [ ] Limit results (default: 20)
- [ ] Format as table or JSON
- [ ] Write tests for search functionality

**Acceptance Criteria:**
- `frappecli files search "invoice"` finds files with "invoice" in name
- Shows relevant file information
- Handles no results gracefully
- Fast search with reasonable limits

**API Endpoint:**
```http
POST /api/method/frappe.core.api.file.get_files_by_search_text
Body: {text: "search term"}
```

**Files to Update:**
```
src/frappecli/commands/files.py
tests/test_commands_files.py
```

---

### User Story 3.6: Bulk Upload
**As a** user  
**I want** to upload multiple files at once  
**So that** I can efficiently upload batches of documents

**Tasks:**
- [ ] Implement `bulk-upload` command in `files.py`
- [ ] Accept glob patterns (./docs/*.pdf)
- [ ] Accept directory paths (recursive option)
- [ ] Show progress for each file
- [ ] Support `--attach` for all files
- [ ] Generate summary report (success/failure counts)
- [ ] Continue on errors (don't stop batch)
- [ ] Write tests for bulk operations

**Acceptance Criteria:**
- `frappecli bulk-upload ./docs/*.pdf` uploads all PDFs
- `frappecli bulk-upload ./folder/ --recursive` uploads all files in folder
- Shows progress for each file
- Summary shows X successful, Y failed
- Failed uploads are listed with reasons
- All bulk uploads respect `--public` flag

**Files to Update:**
```
src/frappecli/commands/files.py
tests/test_commands_files.py
tests/fixtures/bulk_files/ (multiple test files)
```

---

## Phase 4: Reports & RPC

**Goal:** Implement report execution and RPC method calls

### User Story 4.1: List Reports
**As a** user  
**I want** to see all available reports  
**So that** I know what reports I can execute

**Tasks:**
- [ ] Create `src/frappecli/commands/reports.py`
- [ ] Implement `reports list` command
- [ ] Fetch all Report doctypes
- [ ] Filter by module, type (Report Builder, Script, Query)
- [ ] Show report name, module, type
- [ ] Format as table or JSON
- [ ] Write tests

**Acceptance Criteria:**
- `frappecli reports list` shows all reports
- `frappecli reports list --module "Accounts"` filters by module
- Table shows report name, type, module
- Handles sites with no custom reports

**API Endpoint:**
```http
GET /api/resource/Report?fields=["name","module","report_type"]
```

**Files to Create:**
```
src/frappecli/commands/reports.py
tests/test_commands_reports.py
```

---

### User Story 4.2: Execute Report
**As a** user  
**I want** to run a report and see the results  
**So that** I can get insights from my data

**Tasks:**
- [ ] Implement `report` command in `reports.py`
- [ ] Add `--filters` option (JSON)
- [ ] Support output formats (table, JSON, CSV)
- [ ] Handle large result sets
- [ ] Add `--output` flag to save to file
- [ ] Show execution time
- [ ] Write tests with mocked report data

**Acceptance Criteria:**
- `frappecli report "System Report"` executes and shows results
- `frappecli report "Ledger" --filters '{"from_date": "2026-01-01"}'` passes filters
- `frappecli report "Report" --output report.csv` saves to file
- Table format is readable
- Large reports don't crash terminal

**API Endpoint:**
```http
POST /api/method/frappe.desk.query_report.run
Body: {report_name: "Report Name", filters: {...}}
```

**Files to Update:**
```
src/frappecli/commands/reports.py
tests/test_commands_reports.py
```

---

### User Story 4.3: Call RPC Methods
**As a** user  
**I want** to call custom server methods  
**So that** I can execute custom business logic

**Tasks:**
- [ ] Create `src/frappecli/commands/rpc.py`
- [ ] Implement `call` command
- [ ] Accept method path (dotted notation)
- [ ] Accept arguments via `--args` (JSON or @file)
- [ ] Show return value formatted
- [ ] Handle method errors gracefully
- [ ] Write tests for various method types

**Acceptance Criteria:**
- `frappecli call frappe.client.get_count --args '{"doctype": "User"}'` works
- `frappecli call custom.method --args @params.json` reads from file
- Shows return value formatted nicely
- Handles methods that return None
- Clear error messages for non-existent methods

**API Endpoint:**
```http
POST /api/method/{method.path}
Body: {arg1: value1, ...}
```

**Files to Create:**
```
src/frappecli/commands/rpc.py
tests/test_commands_rpc.py
```

---

### User Story 4.4: Site Status Command
**As a** user  
**I want** to check my Frappe site status and version  
**So that** I can verify connectivity and site info

**Tasks:**
- [ ] Implement `status` command in `site.py`
- [ ] Call version API endpoint
- [ ] Show Frappe version, app versions
- [ ] Add `--detailed` flag for more info
- [ ] Show configured site info from config
- [ ] Test connectivity
- [ ] Write tests

**Acceptance Criteria:**
- `frappecli status` shows Frappe version
- `frappecli status --detailed` shows all installed apps
- Shows current site from config
- Indicates if site is reachable
- Handles unreachable sites gracefully

**API Endpoint:**
```http
GET /api/method/version
```

**Files to Update:**
```
src/frappecli/commands/site.py
tests/test_commands_site.py
```

---

## Phase 5: Polish & Release

**Goal:** Testing, documentation, and first release

### User Story 5.1: Comprehensive Testing
**As a** developer  
**I want** high test coverage  
**So that** the tool is reliable and maintainable

**Tasks:**
- [ ] Review all modules for test coverage
- [ ] Add integration tests
- [ ] Add edge case tests (timeouts, large files, etc.)
- [ ] Test quoted arguments extensively
- [ ] Test multi-site switching
- [ ] Test error handling paths
- [ ] Achieve 80%+ coverage
- [ ] Set up CI pipeline (GitHub Actions)

**Acceptance Criteria:**
- `uv run pytest --cov` shows 80%+ coverage
- All critical paths tested
- Edge cases covered
- CI runs tests on push
- Tests run on Python 3.12, 3.13

**Files to Create:**
```
.github/workflows/test.yml
tests/integration/test_live_api.py (optional, manual)
```

---

### User Story 5.2: Documentation
**As a** user  
**I want** clear documentation  
**So that** I can use the tool effectively

**Tasks:**
- [ ] Review and update README.md
- [ ] Add usage examples for all commands
- [ ] Create troubleshooting guide
- [ ] Add API reference docs
- [ ] Create config file examples
- [ ] Add FAQ section
- [ ] Record demo GIFs/videos (optional)
- [ ] Update AGENTS.md with implementation notes

**Acceptance Criteria:**
- README has clear install instructions
- All commands have usage examples
- Troubleshooting section covers common issues
- Config examples are provided
- Documentation is easy to navigate

**Files to Update:**
```
README.md
AGENTS.md
docs/troubleshooting.md (new)
docs/api-reference.md (new)
config.example.yaml
```

---

### User Story 5.3: Error Handling & UX Polish
**As a** user  
**I want** helpful error messages  
**So that** I can fix issues quickly

**Tasks:**
- [ ] Review all error messages for clarity
- [ ] Add suggestions to error messages
- [ ] Implement better progress indicators
- [ ] Add colors and formatting with Rich
- [ ] Handle interrupts gracefully (Ctrl+C)
- [ ] Add `--debug` flag for verbose output
- [ ] Test UX with fresh eyes
- [ ] Write UX guidelines doc

**Acceptance Criteria:**
- Error messages explain what went wrong and how to fix
- Progress bars work for long operations
- Colors enhance readability
- Ctrl+C stops gracefully without tracebacks
- `--debug` shows detailed logs

**Files to Update:**
```
All command files (error messages)
src/frappecli/cli.py (debug flag)
docs/contributing.md (UX guidelines)
```

---

### User Story 5.4: First Release
**As a** maintainer  
**I want** to publish v0.1.0  
**So that** users can install and use the tool

**Tasks:**
- [ ] Tag v0.1.0 in git
- [ ] Build package with `uv build`
- [ ] Test installation in clean environment
- [ ] Publish to PyPI (or TestPyPI first)
- [ ] Create GitHub release with changelog
- [ ] Announce on Frappe forum/discuss
- [ ] Monitor for bug reports

**Acceptance Criteria:**
- Package builds without errors
- `uv pip install frappecli` works
- Entry point `frappecli` is available
- Version shows as 0.1.0
- GitHub release created with notes

**Files to Create:**
```
CHANGELOG.md
.github/workflows/release.yml (optional)
```

---

## Future Enhancements (Backlog)

### Phase 6: Advanced Features
- [ ] Interactive REPL mode (`frappecli shell`)
- [ ] Watch mode for live updates (`frappecli watch "Customer"`)
- [ ] CSV import/export commands
- [ ] Workflow action commands
- [ ] Bash/Zsh completion scripts
- [ ] Plugin system for custom commands
- [ ] Offline mode with local SQLite cache
- [ ] Diff command for comparing documents
- [ ] Backup/restore commands
- [ ] Migration helper (site → site)

### Phase 7: Integration Features
- [ ] Webhook listener mode
- [ ] Scheduled tasks (cron integration)
- [ ] Docker container with frappecli
- [ ] GitHub Actions integration
- [ ] Ansible module
- [ ] Terraform provider (long-term)

---

## Testing Strategy

### Unit Tests
- Each function/method isolated
- Mock external dependencies (HTTP, file system)
- Fast execution (< 1 second total)
- Cover all code paths

### Integration Tests
- Test command end-to-end
- Mock HTTP at requests level
- Verify JSON parsing, error handling
- Test with realistic data

### Manual Testing
- Test against real Frappe instance (optional)
- Verify all commands work as documented
- Test on different OS (macOS, Linux, Windows)
- Test with different Python versions

### Performance Testing
- Benchmark large file uploads
- Test pagination with large datasets
- Measure startup time
- Profile memory usage

---

## Success Metrics

### v0.1.0 Release Criteria
- [ ] All Phase 1-4 user stories complete
- [ ] 80%+ test coverage
- [ ] Documentation complete
- [ ] 0 critical bugs
- [ ] Published to PyPI

### Adoption Metrics (Future)
- PyPI downloads
- GitHub stars
- Issue reports and PRs
- Forum discussions

---

## Risk Mitigation

### Technical Risks
1. **API Changes:** Frappe API might change
   - *Mitigation:* Version detection, graceful degradation
   
2. **Large File Uploads:** Memory issues
   - *Mitigation:* Streaming uploads, chunk processing
   
3. **Rate Limiting:** API rate limits
   - *Mitigation:* Retry logic, rate limit detection

### Project Risks
1. **Scope Creep:** Too many features
   - *Mitigation:* Strict MVP definition, backlog discipline
   
2. **Time Overrun:** Takes longer than planned
   - *Mitigation:* Weekly reviews, cut features if needed

---

## Timeline Summary

| Phase | Key Deliverables |
|-------|-----------------|
| Phase 1 | Foundation (config, client, CLI) |
| Phase 2 | CRUD operations |
| Phase 3 | File management |
| Phase 4 | Reports & RPC |
| Phase 5 | Polish & release → **v0.1.0** |

---

## Notes

- User stories can be reordered based on priority
- Testing is continuous throughout all phases
- Documentation is updated as features are implemented
- Release when all acceptance criteria met and critical bugs resolved

---

**Plan Status:** Ready for implementation  
**Next Step:** Begin Phase 1, User Story 1.1
