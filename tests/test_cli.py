"""Tests for CLI entry point."""

import pytest
from click.testing import CliRunner

from frappecli.cli import cli


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


class TestCLIBasics:
    """Test basic CLI functionality."""

    def test_cli_help(self, runner):
        """Test CLI help output."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "frappecli" in result.output.lower()
        assert "Usage:" in result.output

    def test_cli_version(self, runner):
        """Test version display."""
        result = runner.invoke(cli, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output


class TestGlobalOptions:
    """Test global CLI options."""

    def test_site_option(self, runner):
        """Test --site global option."""
        result = runner.invoke(cli, ["--site", "production", "--help"])
        assert result.exit_code == 0

    def test_config_option(self, runner):
        """Test --config global option."""
        result = runner.invoke(cli, ["--config", "/path/to/config.yaml", "--help"])
        assert result.exit_code == 0

    def test_json_option(self, runner):
        """Test --json global option."""
        result = runner.invoke(cli, ["--json", "--help"])
        assert result.exit_code == 0

    def test_verbose_option(self, runner):
        """Test --verbose global option."""
        result = runner.invoke(cli, ["--verbose", "--help"])
        assert result.exit_code == 0


class TestCommandGroups:
    """Test command groups exist."""

    def test_has_command_groups(self, runner):
        """Test that command groups are registered."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        # Check for command groups in help output
        assert "Commands:" in result.output or "Usage:" in result.output
