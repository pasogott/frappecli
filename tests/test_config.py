"""Tests for configuration management."""

from pathlib import Path

import pytest

from frappecli.config import Config, ConfigError


@pytest.fixture
def test_config_path():
    """Path to test configuration file."""
    return Path(__file__).parent / "fixtures" / "test_config.yaml"


@pytest.fixture
def empty_config_path(tmp_path):
    """Path to non-existent config file."""
    return tmp_path / "nonexistent.yaml"


@pytest.fixture
def invalid_yaml_path(tmp_path):
    """Path to invalid YAML file."""
    invalid_file = tmp_path / "invalid.yaml"
    invalid_file.write_text("invalid: yaml: content: [")
    return invalid_file


class TestConfigLoading:
    """Test configuration file loading."""

    def test_load_config_success(self, test_config_path):
        """Test loading a valid configuration file."""
        config = Config(test_config_path)
        assert config.data is not None
        assert "sites" in config.data
        assert "default_site" in config.data

    def test_load_config_missing_file(self, empty_config_path):
        """Test loading non-existent configuration file."""
        with pytest.raises(ConfigError, match="Configuration file not found"):
            Config(empty_config_path)

    def test_load_config_invalid_yaml(self, invalid_yaml_path):
        """Test loading invalid YAML file."""
        with pytest.raises(ConfigError, match="Invalid YAML"):
            Config(invalid_yaml_path)


class TestSiteConfiguration:
    """Test site configuration access."""

    def test_get_site_config(self, test_config_path):
        """Test retrieving site configuration."""
        config = Config(test_config_path)
        site_config = config.get_site_config("production")

        assert site_config is not None
        assert site_config["url"] == "https://erp.example.com"
        assert site_config["api_key"] == "prod_key_123"
        assert site_config["api_secret"] == "prod_secret_456"

    def test_get_site_config_not_found(self, test_config_path):
        """Test retrieving non-existent site configuration."""
        config = Config(test_config_path)
        with pytest.raises(ConfigError, match="Site 'nonexistent' not found"):
            config.get_site_config("nonexistent")

    def test_get_default_site_config(self, test_config_path):
        """Test retrieving default site configuration."""
        config = Config(test_config_path)
        site_config = config.get_default_site_config()

        assert site_config is not None
        assert site_config["url"] == "https://erp.example.com"

    def test_list_sites(self, test_config_path):
        """Test listing all configured sites."""
        config = Config(test_config_path)
        sites = config.list_sites()

        assert len(sites) == 3
        assert "production" in sites
        assert "staging" in sites
        assert "localhost" in sites


class TestEnvironmentVariableSubstitution:
    """Test environment variable substitution in config values."""

    def test_env_var_substitution(self, test_config_path, monkeypatch):
        """Test environment variable substitution."""
        monkeypatch.setenv("FRAPPE_STAGING_KEY", "staging_key_from_env")
        monkeypatch.setenv("FRAPPE_STAGING_SECRET", "staging_secret_from_env")

        config = Config(test_config_path)
        site_config = config.get_site_config("staging")

        assert site_config["api_key"] == "staging_key_from_env"
        assert site_config["api_secret"] == "staging_secret_from_env"

    def test_env_var_missing(self, test_config_path, monkeypatch):
        """Test missing environment variable."""
        monkeypatch.delenv("FRAPPE_STAGING_KEY", raising=False)
        monkeypatch.delenv("FRAPPE_STAGING_SECRET", raising=False)

        config = Config(test_config_path)
        with pytest.raises(ConfigError, match="Environment variable.*not set"):
            config.get_site_config("staging")


class TestConfigValidation:
    """Test configuration validation."""

    def test_validate_site_config_success(self, test_config_path):
        """Test validation of valid site configuration."""
        config = Config(test_config_path)
        site_config = config.get_site_config("production")
        # Should not raise
        config.validate_site_config(site_config)

    def test_validate_missing_url(self, tmp_path):
        """Test validation fails for missing URL."""
        invalid_config = tmp_path / "invalid.yaml"
        invalid_config.write_text("""
sites:
  test:
    api_key: key
    api_secret: secret
default_site: test
""")
        config = Config(invalid_config)
        with pytest.raises(ConfigError, match="Missing required field: url"):
            config.get_site_config("test")

    def test_validate_missing_api_key(self, tmp_path):
        """Test validation fails for missing API key."""
        invalid_config = tmp_path / "invalid.yaml"
        invalid_config.write_text("""
sites:
  test:
    url: https://example.com
    api_secret: secret
default_site: test
""")
        config = Config(invalid_config)
        with pytest.raises(ConfigError, match="Missing required field: api_key"):
            config.get_site_config("test")

    def test_validate_missing_api_secret(self, tmp_path):
        """Test validation fails for missing API secret."""
        invalid_config = tmp_path / "invalid.yaml"
        invalid_config.write_text("""
sites:
  test:
    url: https://example.com
    api_key: key
default_site: test
""")
        config = Config(invalid_config)
        with pytest.raises(ConfigError, match="Missing required field: api_secret"):
            config.get_site_config("test")

    def test_validate_invalid_url_format(self, tmp_path):
        """Test validation fails for invalid URL format."""
        invalid_config = tmp_path / "invalid.yaml"
        invalid_config.write_text("""
sites:
  test:
    url: not-a-valid-url
    api_key: key
    api_secret: secret
default_site: test
""")
        config = Config(invalid_config)
        with pytest.raises(ConfigError, match="Invalid URL format"):
            config.get_site_config("test")
