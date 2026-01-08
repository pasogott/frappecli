# frappecli

A Python CLI tool for managing Frappe instances via REST API.

> **✅ MVP Complete!** All core features implemented (Phases 1-4).  
> Ready for production use. Only polish/release tasks remaining (Phase 5).  
> See [FINAL_STATUS.md](FINAL_STATUS.md) for complete summary.

## Overview

`frappecli` provides command-line access to Frappe Framework's REST API, enabling:

- **CRUD Operations**: Create, read, update, delete documents across all doctypes ✅
- **File Management**: Upload, download, and manage files (private by default) ✅
- **Reports**: Execute and export Frappe reports (JSON/CSV) ✅
- **RPC Methods**: Call custom server methods ✅
- **Multi-Site**: Manage multiple Frappe sites from one config ✅

## Installation

```bash
# From source (currently only option)
git clone https://github.com/pasogott/frappecli.git
cd frappecli
uv sync
uv pip install -e .
```

**Note:** PyPI package not yet published. Will be available with v0.1.0 release.

## Quick Start

### 1. Configure Your Site

Create `~/.config/frappecli/config.yaml`:

```yaml
sites:
  production:
    url: https://erp.company.com
    api_key: your_api_key
    api_secret: your_api_secret
  staging:
    url: https://staging.company.com
    api_key: your_staging_key
    api_secret: your_staging_secret

default_site: production
```

### 2. Site Management ✅

```bash
frappecli site doctypes                    # List all doctypes
frappecli site doctypes --module "Core"    # Filter by module
frappecli site doctypes --custom           # Only custom doctypes
frappecli site info "User"                 # Get doctype details
frappecli site info "User" --fields        # Detailed field list
frappecli site status                      # Site status & version
frappecli site status --detailed           # With installed apps
```

### 3. Document CRUD Operations ✅

```bash
# List documents
frappecli doc list "User" --limit 10
frappecli doc list "ToDo" --filters '{"status": "Open"}'

# Get a document
frappecli doc get "User" "administrator@example.com"

# Create a document
frappecli doc create "ToDo" --data '{"description": "Review PR"}'
frappecli doc create "ToDo" --data @todo.json

# Update a document
frappecli doc update "ToDo" "TODO-001" --data '{"status": "Closed"}'

# Delete a document
frappecli doc delete "ToDo" "TODO-001"
frappecli doc delete "ToDo" "TODO-001" --yes  # Skip confirmation
```

### 4. File Management ✅

```bash
# Upload file (private by default)
frappecli upload document.pdf
frappecli upload report.pdf --attach "Project" "PROJ-001"
frappecli upload logo.png --public --folder "Assets"

# Download file
frappecli download /files/document.pdf -o local.pdf

# List and search files
frappecli files list --folder "Home"
frappecli files search "invoice"

# Bulk upload
frappecli bulk-upload ./documents/*.pdf --folder "Reports"
```

### 5. Reports & RPC ✅

```bash
# List available reports
frappecli reports list
frappecli reports list --module "Accounts"

# Run a report
frappecli report "System Report" --filters '{"from_date": "2026-01-01"}'
frappecli report "Sales Report" --output report.csv

# Call custom RPC method
frappecli call frappe.client.get_count --args '{"doctype": "User"}'
frappecli call custom.method.name --args @params.json
```

## Configuration

### Environment Variables

```bash
# Override config file location
export FRAPPECLI_CONFIG=~/.config/frappecli/config.yaml

# Site credentials (if not using config file)
export FRAPPE_URL=https://erp.example.com
export FRAPPE_API_KEY=your_api_key
export FRAPPE_API_SECRET=your_api_secret
```

### Config File Format

```yaml
sites:
  site_name:
    url: https://frappe-site.com
    api_key: ${FRAPPE_API_KEY}          # Environment variable
    api_secret: ${FRAPPE_API_SECRET}    # Environment variable

default_site: site_name

# Upload defaults
upload:
  default_private: true
  default_folder: "Home"
  auto_optimize_images: false
```

## Security Best Practices

### Private by Default

All file uploads are **private by default** for security. Use `--public` flag explicitly:

```bash
frappecli upload sensitive.pdf              # Private (default) 🔒
frappecli upload marketing-asset.png --public  # Public (explicit) 🌍
```

### API Key Management

- Store API keys in environment variables
- Never commit API keys to version control
- Use separate keys for production/staging
- Rotate keys regularly

### Generating API Keys

In Frappe UI:
1. Go to User → API Access
2. Generate API Key + API Secret
3. Store securely in environment variables

## Important Notes

### Quoted Arguments

Always use quotes for doctype and document names, especially with spaces:

```bash
# Correct ✅
frappecli get "User" "admin@example.com"
frappecli list "Email Queue"
frappecli upload file.pdf --attach "Custom DocType" "DOC-001"

# Wrong ❌ (will fail)
frappecli get User admin@example.com
frappecli list Email Queue
```

### Multi-Site Usage

Switch sites using `--site` flag:

```bash
frappecli --site staging list "User"
frappecli --site production upload file.pdf
```

### File Paths

Frappe file system:
- Private files: `/private/files/` (requires auth)
- Public files: `/files/` (no auth required)
- Files are deduplicated by content hash

## Use Cases

### Automation & DevOps

```bash
# Batch create users
cat users.json | jq -c '.[]' | while read user; do
  frappecli create "User" --data "$user"
done

# Sync data between sites
frappecli --site production list "Custom DocType" --json > data.json
frappecli --site staging create "Custom DocType" --data @data.json

# Backup files
frappecli files list --json | jq -r '.[] | .file_url' | while read url; do
  frappecli download "$url" -o "backup/$(basename $url)"
done
```

### Integration with External Systems

```bash
# Export data for external processing
frappecli list "Sales Order" --filters '{"status": "Pending"}' --json > pending_orders.json

# Import processed data
frappecli bulk-upload ./processed/*.csv --folder "Imports"

# Webhook automation
frappecli call custom.webhook.handler --args '{"event": "order_received"}'
```

### Custom Frappe Apps

Works with any Frappe app:
- ERPNext (business management)
- Healthcare (hospital management)
- Education (school management)
- Custom applications

```bash
# List doctypes from specific module
frappecli doctypes --module "Healthcare"
frappecli doctypes --module "Custom App"

# Work with app-specific doctypes
frappecli list "Patient"
frappecli get "Appointment" "APT-001"
```

## Development

### Setup

```bash
git clone https://github.com/pasogott/frappecli.git
cd frappecli
uv sync
```

### Run Tests

```bash
uv run pytest tests/ -v
uv run pytest tests/ --cov=frappecli
```

### Code Quality

```bash
uv run ruff check src/
uv run ruff format src/
```

### Run Locally

```bash
uv run frappecli --help
uv run frappecli doctypes
```

## Troubleshooting

### Authentication Errors

```bash
# Verify credentials
curl -H "Authorization: token api_key:api_secret" https://site.com/api/method/frappe.auth.get_logged_user

# Check site configuration
frappecli sites
```

### Connection Issues

```bash
# Test site connectivity
curl https://your-frappe-site.com/api/method/version

# Check site status
frappecli status
```

### File Upload Failures

- Check max file size: `frappecli call frappe.core.api.file.get_max_file_size`
- Verify file permissions
- Check disk space on Frappe server

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Add tests for new features
4. Run `uv run pytest` and `uv run ruff check`
5. Submit a pull request

See [AGENTS.md](AGENTS.md) for development guidelines.

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- [Frappe Framework](https://github.com/frappe/frappe)
- [Frappe Documentation](https://docs.frappe.io/framework)
- [Frappe API Documentation](https://docs.frappe.io/framework/user/en/api)
- [frappecli GitHub Repository](https://github.com/pasogott/frappecli)
- [Issue Tracker](https://github.com/pasogott/frappecli/issues)

## Author

**pasogott - Pascal Schott**

---

**Note:** This is a community tool and is not officially affiliated with Frappe Technologies.
