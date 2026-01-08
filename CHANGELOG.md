# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.1] - 2026-01-08

### Added
- **Homebrew installation support** via `pasogott/tap`
  - Stable release installation: `brew install pasogott/tap/frappecli`
  - HEAD installation option: `brew install --HEAD pasogott/tap/frappecli`
- Automatic Homebrew tap notification workflow on new releases
- Auto-update workflow in homebrew-tap for new releases

### Changed
- Updated README with Homebrew installation instructions (recommended method for macOS)
- Improved installation documentation with stable vs HEAD options

### Fixed
- GitHub Actions CI dependency installation

## [0.1.0] - 2026-01-08

### Added

#### Document Operations
- Complete CRUD operations for Frappe doctypes (Create, Read, Update, Delete, List)
- Advanced filtering with JSON syntax for complex queries
- Pagination support with `--offset` and `--limit` options
- Order by functionality for sorting results (`--order-by`)
- Field selection to retrieve specific fields only (`--fields`)
- Dry-run mode for Create and Update operations (`--dry-run`)
- Support for all Frappe doctypes (standard, custom, and app-specific)

#### File Management
- Single file upload with private/public options
- Bulk upload with pattern matching and recursive directory support
- File download functionality
- File attachments to specific documents and fields
- File search by name
- File listing by folder or document attachment
- Progress bars for bulk operations
- Support for large files (tested up to 1.7MB)

#### Reports & RPC
- Report listing with module filtering
- Report execution with filter support
- Export to JSON and CSV formats
- CSV export handles variable fieldnames across rows
- Custom RPC method calls
- Support for complex method arguments via JSON or file input

#### CLI Features
- Multi-site configuration support
- Environment variable substitution in config files
- Rich formatted table output
- JSON output mode (`--json` flag)
- Verbose mode flag (`--verbose`)
- Global site selection (`--site`)
- Custom config file path (`--config`)
- Site status and version information
- Doctype information with field details
- Doctype listing with filtering options

### Fixed
- API response unwrapping for both `message` and `data` wrapper fields
- Filter serialization: properly convert dict/list parameters to JSON strings
- File upload Content-Type header conflict with multipart/form-data
- Bulk upload absolute path handling
- CSV export with variable fieldnames across report rows
- Files list command handling different API response formats
- Site status command using working endpoints instead of broken version API

### Changed
- Refactored helpers to reduce code duplication
- Centralized output handling with `output_data()` helper
- Improved error messages with HTTP status codes
- Enhanced file upload with proper resource cleanup
- Increased timeout to 60s for large file uploads
- Simplified site status check using reliable endpoints

### Security
- Private files by default (requires explicit `--public` flag)
- API credentials support via environment variables
- Config file validation with required field checks

### Testing
- 54 live tests performed with real ERPNext instance
- CRUD operations tested on various doctypes
- 20+ files uploaded in bulk operations
- Report execution with 259 rows processed
- Complex filters and nested queries validated
- Error handling and edge cases verified
- All tests passed (100% success rate)

### Documentation
- Comprehensive README.md with usage examples
- AGENTS.md for AI coding assistants
- Inline code documentation with type hints
- Config file examples with comments

### Technical
- Python 3.12+ support
- Click-based CLI framework
- Rich for terminal formatting
- Requests with retry logic for HTTP
- PyYAML for configuration parsing
- Full type hints coverage
- 47% test coverage (90%+ for core modules)

## Links
- [Repository](https://github.com/pasogott/frappecli)
- [Issues](https://github.com/pasogott/frappecli/issues)
- [Releases](https://github.com/pasogott/frappecli/releases)
- [Homebrew Tap](https://github.com/pasogott/homebrew-tap)

[0.1.1]: https://github.com/pasogott/frappecli/releases/tag/v0.1.1
[0.1.0]: https://github.com/pasogott/frappecli/releases/tag/v0.1.0
