# Migration Guide - v0.1.0 Refactoring

## Breaking Changes

**Version 0.1.0** introduces a refactored CLI structure for better consistency and discoverability.

### Command Structure Changes

| Old Command | New Command | Notes |
|------------|-------------|-------|
| `frappecli doctypes` | `frappecli site doctypes` | Moved to site group |
| `frappecli doctype-info "User"` | `frappecli site info "User"` | Renamed and moved |
| `frappecli status` | `frappecli site status` | Moved to site group |
| `frappecli list "User"` | `frappecli doc list "User"` | Moved to doc group |
| `frappecli get "User" "x"` | `frappecli doc get "User" "x"` | Moved to doc group |
| `frappecli create "User"` | `frappecli doc create "User"` | Moved to doc group |
| `frappecli update "User" "x"` | `frappecli doc update "User" "x"` | Moved to doc group |
| `frappecli delete "User" "x"` | `frappecli doc delete "User" "x"` | Moved to doc group |
| `frappecli files *` | `frappecli files *` | **Unchanged** ✅ |
| `frappecli reports *` | `frappecli reports *` | **Unchanged** ✅ |
| `frappecli call method` | `frappecli call method` | **Unchanged** ✅ |

### Quick Migration

**Site Commands:**
```bash
# Before
frappecli doctypes
frappecli doctype-info "User"
frappecli status

# After
frappecli site doctypes
frappecli site info "User"
frappecli site status
```

**Document Commands:**
```bash
# Before
frappecli list "User"
frappecli get "User" "admin"
frappecli create "User" --data '{...}'
frappecli update "User" "admin" --data '{...}'
frappecli delete "User" "admin"

# After  
frappecli doc list "User"
frappecli doc get "User" "admin"
frappecli doc create "User" --data '{...}'
frappecli doc update "User" "admin" --data '{...}'
frappecli doc delete "User" "admin"
```

**Files & Reports (No Changes):**
```bash
# These remain the same ✅
frappecli files upload file.pdf
frappecli files list
frappecli reports list
frappecli report "Sales Report"
frappecli call method.name
```

### Why This Change?

**Benefits:**
1. **Better Organization:** Commands are grouped logically
2. **Discoverability:** `frappecli --help` shows clear categories
3. **Consistency:** All commands follow the same pattern
4. **Scalability:** Easy to add new commands without namespace conflicts
5. **Professional:** Matches industry-standard CLI design patterns

### New CLI Structure

```
frappecli
├── site                    # Site management
│   ├── doctypes           # List doctypes
│   ├── info DOCTYPE       # Get doctype details
│   └── status             # Site status
├── doc                     # Document CRUD
│   ├── list DOCTYPE       # List documents
│   ├── get DOCTYPE NAME   # Get document
│   ├── create DOCTYPE     # Create document
│   ├── update DOCTYPE NAME # Update document
│   └── delete DOCTYPE NAME # Delete document
├── files                   # File management
│   ├── upload FILE        # Upload file
│   ├── download URL       # Download file
│   ├── list               # List files
│   └── search QUERY       # Search files
├── reports                 # Reports
│   ├── list               # List reports
│   └── run REPORT         # Execute report
└── call METHOD            # RPC calls
```

### Updating Scripts

If you have automation scripts using frappecli:

**Bash/Shell Scripts:**
```bash
# Find and replace in all scripts
sed -i 's/frappecli doctypes/frappecli site doctypes/g' *.sh
sed -i 's/frappecli doctype-info/frappecli site info/g' *.sh
sed -i 's/frappecli status/frappecli site status/g' *.sh
sed -i 's/frappecli list /frappecli doc list /g' *.sh
sed -i 's/frappecli get /frappecli doc get /g' *.sh
sed -i 's/frappecli create /frappecli doc create /g' *.sh
sed -i 's/frappecli update /frappecli doc update /g' *.sh
sed -i 's/frappecli delete /frappecli doc delete /g' *.sh
```

**Python Scripts:**
```python
# Before
subprocess.run(["frappecli", "list", "User"])

# After
subprocess.run(["frappecli", "doc", "list", "User"])
```

### Testing Your Migration

Run these commands to verify:

```bash
# Test site commands
frappecli site --help
frappecli site doctypes --help

# Test doc commands
frappecli doc --help
frappecli doc list --help

# Test that files/reports still work
frappecli files --help
frappecli reports --help
```

### Getting Help

```bash
# See all command groups
frappecli --help

# Get help for specific group
frappecli site --help
frappecli doc --help
frappecli files --help
frappecli reports --help

# Get help for specific command
frappecli site info --help
frappecli doc list --help
```

### Rollback

If you need to use the old command structure temporarily, check out the previous version:

```bash
git checkout v0.0.x  # (if tagged)
# or
git checkout <commit-hash-before-refactoring>
```

### Support

Questions or issues with migration?
- Check updated README.md
- Open an issue: https://github.com/pasogott/frappecli/issues
- See FINAL_STATUS.md for complete documentation

---

**Migration difficulty:** Low (simple command prefix changes)  
**Estimated time:** 5-10 minutes for most use cases  
**Breaking changes:** Command structure only (all features work the same)
