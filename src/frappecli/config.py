"""Configuration management for frappecli."""

import os
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import yaml


class ConfigError(Exception):
    """Configuration error exception."""

    pass


class Config:
    """Configuration manager for frappecli.
    
    Loads configuration from YAML file and provides access to site configurations.
    Supports environment variable substitution in config values.
    """

    def __init__(self, config_path: Path | str | None = None) -> None:
        """Initialize configuration.
        
        Args:
            config_path: Path to configuration file. If None, uses default location.
            
        Raises:
            ConfigError: If configuration file not found or invalid.
        """
        if config_path is None:
            config_path = self._get_default_config_path()
        else:
            config_path = Path(config_path)
        
        self.config_path = config_path
        self.data = self._load_config()

    def _get_default_config_path(self) -> Path:
        """Get default configuration file path.
        
        Returns:
            Path to default config file (~/.config/frappecli/config.yaml)
        """
        return Path.home() / ".config" / "frappecli" / "config.yaml"

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from YAML file.
        
        Returns:
            Configuration dictionary.
            
        Raises:
            ConfigError: If file not found or invalid YAML.
        """
        if not self.config_path.exists():
            msg = f"Configuration file not found: {self.config_path}"
            raise ConfigError(msg)
        
        try:
            with open(self.config_path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            msg = f"Invalid YAML in configuration file: {e}"
            raise ConfigError(msg) from e
        
        if not isinstance(data, dict):
            msg = "Configuration file must contain a dictionary"
            raise ConfigError(msg)
        
        return data

    def _substitute_env_vars(self, value: str) -> str:
        """Substitute environment variables in string.
        
        Replaces ${VAR_NAME} with environment variable value.
        
        Args:
            value: String potentially containing ${VAR} placeholders.
            
        Returns:
            String with environment variables substituted.
            
        Raises:
            ConfigError: If environment variable is not set.
        """
        pattern = re.compile(r'\$\{([^}]+)\}')
        
        def replace_var(match: re.Match[str]) -> str:
            var_name = match.group(1)
            var_value = os.environ.get(var_name)
            if var_value is None:
                msg = f"Environment variable '{var_name}' is not set"
                raise ConfigError(msg)
            return var_value
        
        return pattern.sub(replace_var, value)

    def _process_site_config(self, site_config: dict[str, Any]) -> dict[str, Any]:
        """Process site configuration with environment variable substitution.
        
        Args:
            site_config: Raw site configuration dictionary.
            
        Returns:
            Processed configuration with environment variables substituted.
        """
        processed = {}
        for key, value in site_config.items():
            if isinstance(value, str) and "${" in value:
                processed[key] = self._substitute_env_vars(value)
            else:
                processed[key] = value
        return processed

    def validate_site_config(self, site_config: dict[str, Any]) -> None:
        """Validate site configuration has required fields.
        
        Args:
            site_config: Site configuration to validate.
            
        Raises:
            ConfigError: If required fields are missing or invalid.
        """
        required_fields = ["url", "api_key", "api_secret"]
        for field in required_fields:
            if field not in site_config:
                msg = f"Missing required field: {field}"
                raise ConfigError(msg)
        
        # Validate URL format
        url = site_config["url"]
        parsed = urlparse(url)
        if not parsed.scheme or not parsed.netloc:
            msg = f"Invalid URL format: {url}"
            raise ConfigError(msg)

    def get_site_config(self, site_name: str) -> dict[str, Any]:
        """Get configuration for a specific site.
        
        Args:
            site_name: Name of the site.
            
        Returns:
            Site configuration dictionary.
            
        Raises:
            ConfigError: If site not found or configuration invalid.
        """
        if "sites" not in self.data:
            msg = "No sites configured"
            raise ConfigError(msg)
        
        sites = self.data["sites"]
        if site_name not in sites:
            msg = f"Site '{site_name}' not found in configuration"
            raise ConfigError(msg)
        
        site_config = sites[site_name]
        processed_config = self._process_site_config(site_config)
        self.validate_site_config(processed_config)
        
        return processed_config

    def get_default_site_config(self) -> dict[str, Any]:
        """Get configuration for the default site.
        
        Returns:
            Default site configuration dictionary.
            
        Raises:
            ConfigError: If no default site configured.
        """
        if "default_site" not in self.data:
            msg = "No default site configured"
            raise ConfigError(msg)
        
        default_site = self.data["default_site"]
        return self.get_site_config(default_site)

    def list_sites(self) -> list[str]:
        """List all configured sites.
        
        Returns:
            List of site names.
        """
        if "sites" not in self.data:
            return []
        return list(self.data["sites"].keys())
