# Authentication Design for frappecli

**Author:** pasogott - Pascal Schott  
**Date:** 2026-01-08  
**Status:** Design Document

## Overview

This document describes how authentication works in frappecli and how to implement it securely.

## Frappe Authentication Methods

Frappe supports multiple authentication methods:

1. **API Token (Recommended for CLI)** ✅
2. Session Cookie (Web browser)
3. OAuth2 (Third-party apps)
4. Basic Auth (Legacy, not recommended)

**For frappecli, we use API Token authentication** because:
- ✅ Simple and secure
- ✅ Ideal for automation and scripts
- ✅ No session management needed
- ✅ Per-user access control
- ✅ Can be revoked easily

## API Token Authentication

### Format

```
Authorization: token {api_key}:{api_secret}
```

**Example:**
```http
GET /api/resource/User/admin@example.com HTTP/1.1
Host: erp.company.com
Authorization: token 1234567890abcdef:fedcba0987654321
```

### How It Works

1. **User generates API credentials** in Frappe UI
2. **CLI stores credentials** securely (config file + env vars)
3. **Every request** includes the Authorization header
4. **Frappe validates** the token and authenticates the user

### Generating API Keys in Frappe

Users must generate API keys in the Frappe UI:

1. Login to Frappe site
2. Go to: **User → [Your User] → API Access**
3. Click **"Generate Keys"**
4. Copy both:
   - **API Key** (public identifier)
   - **API Secret** (private, shown only once)
5. Store securely

## Implementation in frappecli

### 1. Configuration Storage

**Primary method:** YAML config file with environment variable substitution

```yaml
# ~/.config/frappecli/config.yaml
sites:
  production:
    url: https://erp.company.com
    api_key: ${FRAPPE_PROD_API_KEY}
    api_secret: ${FRAPPE_PROD_API_SECRET}
```

**Environment variables:**
```bash
export FRAPPE_PROD_API_KEY="1234567890abcdef"
export FRAPPE_PROD_API_SECRET="fedcba0987654321"
```

**Why this approach?**
- ✅ Secrets not stored in plain text
- ✅ Config can be version-controlled (without secrets)
- ✅ Easy to rotate credentials
- ✅ Works in CI/CD pipelines
- ✅ Standard practice for sensitive data

### 2. Client Implementation

```python
# src/frappecli/client.py

import os
import requests
from typing import Optional

class FrappeClient:
    """Frappe REST API client with token authentication."""
    
    def __init__(
        self, 
        base_url: str, 
        api_key: str, 
        api_secret: str,
        verify_ssl: bool = True
    ):
        """Initialize Frappe API client.
        
        Args:
            base_url: Frappe site URL (e.g., https://erp.company.com)
            api_key: User's API key
            api_secret: User's API secret
            verify_ssl: Verify SSL certificates (default: True)
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.api_secret = api_secret
        
        # Create session with authentication
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'token {api_key}:{api_secret}',
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        })
        self.session.verify = verify_ssl
    
    def _make_request(
        self, 
        method: str, 
        endpoint: str, 
        **kwargs
    ) -> requests.Response:
        """Make authenticated request to Frappe API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., /api/resource/User)
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
            
        Raises:
            AuthenticationError: If credentials are invalid
            APIError: For other API errors
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Handle authentication errors
            if response.status_code == 401:
                raise AuthenticationError(
                    "Invalid API credentials. Please check your api_key and api_secret."
                )
            
            # Handle forbidden
            if response.status_code == 403:
                raise PermissionError(
                    f"Permission denied. User does not have access to this resource."
                )
            
            # Raise for other HTTP errors
            response.raise_for_status()
            
            return response
            
        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to {self.base_url}: {e}")
        except requests.exceptions.Timeout as e:
            raise TimeoutError(f"Request timed out: {e}")
    
    def get(self, doctype: str, name: str) -> dict:
        """Get a single document."""
        response = self._make_request(
            'GET', 
            f'/api/resource/{doctype}/{name}'
        )
        return response.json()['message']
    
    def test_connection(self) -> bool:
        """Test if credentials are valid.
        
        Returns:
            True if connection and auth successful
            
        Raises:
            AuthenticationError: If credentials invalid
            ConnectionError: If cannot connect
        """
        try:
            response = self._make_request(
                'GET',
                '/api/method/frappe.auth.get_logged_user'
            )
            return response.status_code == 200
        except (AuthenticationError, ConnectionError):
            raise


class AuthenticationError(Exception):
    """Raised when API credentials are invalid."""
    pass
```

### 3. Configuration Loading

```python
# src/frappecli/config.py

import os
import re
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

class Config:
    """Configuration manager for frappecli."""
    
    DEFAULT_CONFIG_PATH = Path.home() / ".config" / "frappecli" / "config.yaml"
    
    def __init__(self, config_path: Optional[Path] = None):
        """Load configuration from file.
        
        Args:
            config_path: Path to config file (default: ~/.config/frappecli/config.yaml)
        """
        self.config_path = config_path or self.DEFAULT_CONFIG_PATH
        self.data = self._load_config()
    
    def _load_config(self) -> dict:
        """Load and parse config file with env var substitution."""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Config file not found: {self.config_path}\n"
                f"Please create it using config.example.yaml as a template."
            )
        
        with open(self.config_path, 'r') as f:
            raw_config = f.read()
        
        # Substitute environment variables
        config_text = self._substitute_env_vars(raw_config)
        
        return yaml.safe_load(config_text)
    
    def _substitute_env_vars(self, text: str) -> str:
        """Replace ${VAR_NAME} with environment variable values.
        
        Args:
            text: Text containing ${VAR} placeholders
            
        Returns:
            Text with variables substituted
            
        Raises:
            ValueError: If environment variable not found
        """
        def replacer(match):
            var_name = match.group(1)
            value = os.environ.get(var_name)
            
            if value is None:
                raise ValueError(
                    f"Environment variable '{var_name}' not set.\n"
                    f"Please set it: export {var_name}='your-value'"
                )
            
            return value
        
        # Match ${VAR_NAME} pattern
        return re.sub(r'\$\{([^}]+)\}', replacer, text)
    
    def get_site_config(self, site_name: Optional[str] = None) -> Dict[str, Any]:
        """Get configuration for a specific site.
        
        Args:
            site_name: Name of site (uses default_site if None)
            
        Returns:
            Site configuration dict with url, api_key, api_secret
            
        Raises:
            ValueError: If site not found in config
        """
        site = site_name or self.data.get('default_site')
        
        if not site:
            raise ValueError(
                "No site specified and no default_site configured."
            )
        
        if site not in self.data.get('sites', {}):
            available = ', '.join(self.data.get('sites', {}).keys())
            raise ValueError(
                f"Site '{site}' not found in config.\n"
                f"Available sites: {available}"
            )
        
        return self.data['sites'][site]
    
    def list_sites(self) -> list[str]:
        """List all configured sites."""
        return list(self.data.get('sites', {}).keys())
```

### 4. CLI Integration

```python
# src/frappecli/cli.py

import click
from pathlib import Path
from rich.console import Console

from frappecli.config import Config
from frappecli.client import FrappeClient, AuthenticationError

console = Console()

# Global options
@click.group()
@click.option(
    '--site', 
    help='Site name from config (default: uses default_site)'
)
@click.option(
    '--config',
    type=click.Path(exists=True, path_type=Path),
    help='Path to config file (default: ~/.config/frappecli/config.yaml)'
)
@click.pass_context
def cli(ctx, site, config):
    """frappecli - Frappe Framework CLI Tool"""
    # Store in context for commands to access
    ctx.ensure_object(dict)
    ctx.obj['site'] = site
    ctx.obj['config_path'] = config

def get_client(ctx) -> FrappeClient:
    """Get authenticated Frappe client from context.
    
    Args:
        ctx: Click context
        
    Returns:
        Authenticated FrappeClient instance
        
    Raises:
        AuthenticationError: If credentials invalid
    """
    # Load config
    config = Config(ctx.obj.get('config_path'))
    
    # Get site config
    site_name = ctx.obj.get('site')
    site_config = config.get_site_config(site_name)
    
    # Create client
    try:
        client = FrappeClient(
            base_url=site_config['url'],
            api_key=site_config['api_key'],
            api_secret=site_config['api_secret']
        )
        
        # Test connection on first use
        client.test_connection()
        
        return client
        
    except AuthenticationError as e:
        console.print(f"[red]Authentication failed:[/red] {e}")
        console.print("\n[yellow]Troubleshooting:[/yellow]")
        console.print("1. Check your API key and secret are correct")
        console.print("2. Verify the user exists in Frappe")
        console.print("3. Ensure API Access is enabled for the user")
        raise click.Abort()
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise click.Abort()


@cli.command()
@click.pass_context
def test_auth(ctx):
    """Test authentication with configured site."""
    try:
        client = get_client(ctx)
        console.print("[green]✓ Authentication successful![/green]")
        
        # Get current user info
        response = client.session.get(
            f"{client.base_url}/api/method/frappe.auth.get_logged_user"
        )
        user = response.json()['message']
        console.print(f"Logged in as: [cyan]{user}[/cyan]")
        
    except Exception as e:
        console.print(f"[red]✗ Authentication failed:[/red] {e}")
        raise click.Abort()
```

## Security Best Practices

### 1. Never Hardcode Credentials

❌ **Bad:**
```yaml
sites:
  production:
    api_key: 1234567890abcdef  # DON'T DO THIS
    api_secret: fedcba0987654321
```

✅ **Good:**
```yaml
sites:
  production:
    api_key: ${FRAPPE_PROD_API_KEY}
    api_secret: ${FRAPPE_PROD_API_SECRET}
```

### 2. Use Environment Variables

```bash
# Add to ~/.bashrc or ~/.zshrc
export FRAPPE_PROD_API_KEY="1234567890abcdef"
export FRAPPE_PROD_API_SECRET="fedcba0987654321"
```

### 3. Restrict Config File Permissions

```bash
chmod 600 ~/.config/frappecli/config.yaml
```

### 4. Use Different Credentials Per Environment

```yaml
sites:
  production:
    url: https://erp.company.com
    api_key: ${FRAPPE_PROD_API_KEY}
    api_secret: ${FRAPPE_PROD_API_SECRET}
    
  staging:
    url: https://staging.company.com
    api_key: ${FRAPPE_STAGING_API_KEY}
    api_secret: ${FRAPPE_STAGING_API_SECRET}
```

### 5. Verify SSL Certificates

Always use HTTPS and verify certificates:

```python
session.verify = True  # Default
```

Only disable for local development:
```yaml
http:
  verify_ssl: false  # Only for localhost testing
```

### 6. Rotate Credentials Regularly

- Generate new API keys periodically
- Revoke old keys in Frappe UI
- Update environment variables

### 7. Use Minimal Permissions

- Create dedicated API users
- Grant only required permissions
- Use role-based access control

## Error Handling

### Authentication Errors

```python
try:
    client = FrappeClient(url, key, secret)
    client.test_connection()
except AuthenticationError:
    console.print("[red]Invalid credentials[/red]")
    console.print("Please check:")
    console.print("1. API key and secret are correct")
    console.print("2. User exists and has API access enabled")
    console.print("3. Keys haven't been revoked")
except ConnectionError:
    console.print("[red]Cannot connect to Frappe site[/red]")
    console.print("Please check:")
    console.print("1. Site URL is correct")
    console.print("2. Site is accessible")
    console.print("3. Network connection")
```

### Permission Errors

```python
try:
    doc = client.get("User", "admin@example.com")
except PermissionError:
    console.print("[yellow]Permission denied[/yellow]")
    console.print("Your user does not have access to this resource")
```

## CI/CD Integration

For GitHub Actions and other CI environments:

```yaml
# .github/workflows/ci.yml
env:
  FRAPPE_TEST_URL: ${{ secrets.FRAPPE_TEST_URL }}
  FRAPPE_TEST_API_KEY: ${{ secrets.FRAPPE_TEST_API_KEY }}
  FRAPPE_TEST_API_SECRET: ${{ secrets.FRAPPE_TEST_API_SECRET }}

- name: Run integration tests
  run: |
    export FRAPPE_TEST_URL="${{ secrets.FRAPPE_TEST_URL }}"
    uv run pytest tests/integration/
```

## Alternative: Session-Based Auth (Future)

While not recommended for CLI, Frappe also supports session cookies:

```python
# Login to get session cookie
response = requests.post(
    f"{base_url}/api/method/login",
    data={"usr": "user@example.com", "pwd": "password"}
)

# Use session cookie for subsequent requests
cookies = response.cookies
```

**Not used in frappecli because:**
- ❌ Requires password (less secure)
- ❌ Sessions expire
- ❌ More complex state management
- ❌ Not ideal for automation

## Testing Authentication

```python
# tests/test_auth.py

import pytest
import responses
from frappecli.client import FrappeClient, AuthenticationError

@responses.activate
def test_valid_credentials():
    """Test successful authentication."""
    responses.add(
        responses.GET,
        "https://example.com/api/method/frappe.auth.get_logged_user",
        json={"message": "test@example.com"},
        status=200
    )
    
    client = FrappeClient(
        "https://example.com",
        "valid_key",
        "valid_secret"
    )
    
    assert client.test_connection() == True

@responses.activate
def test_invalid_credentials():
    """Test authentication failure."""
    responses.add(
        responses.GET,
        "https://example.com/api/method/frappe.auth.get_logged_user",
        json={"exc": "Invalid API credentials"},
        status=401
    )
    
    client = FrappeClient(
        "https://example.com",
        "invalid_key",
        "invalid_secret"
    )
    
    with pytest.raises(AuthenticationError):
        client.test_connection()
```

## Summary

**frappecli uses API Token authentication:**

1. ✅ **Simple**: One Authorization header
2. ✅ **Secure**: Credentials in environment variables
3. ✅ **Standard**: Same as Frappe official clients
4. ✅ **Flexible**: Per-user access control
5. ✅ **Automation-friendly**: Perfect for CI/CD

**Format:**
```
Authorization: token {api_key}:{api_secret}
```

**Storage:**
```yaml
# Config file with env vars
api_key: ${FRAPPE_PROD_API_KEY}
api_secret: ${FRAPPE_PROD_API_SECRET}
```

**Implementation:**
- All requests include Authorization header
- Test connection on first use
- Clear error messages for auth failures
- Support for multiple sites

This approach is secure, simple, and follows Frappe best practices!
