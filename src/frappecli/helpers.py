"""Shared helper functions for frappecli."""

import json
from pathlib import Path

import click
from rich.console import Console

from frappecli.client import FrappeClient
from frappecli.config import Config

# Single shared console instance
console = Console()


def get_client(ctx: click.Context) -> FrappeClient:
    """Get configured Frappe client from context.

    Args:
        ctx: Click context with config options

    Returns:
        Configured FrappeClient instance
    """
    config_path = ctx.obj.get("config")
    site_name = ctx.obj.get("site")

    config = Config(config_path) if config_path else Config()
    site_config = (
        config.get_site_config(site_name) if site_name else config.get_default_site_config()
    )

    return FrappeClient(
        base_url=site_config["url"],
        api_key=site_config["api_key"],
        api_secret=site_config["api_secret"],
    )


def load_data(data_str: str) -> dict:
    """Load data from JSON string or file.

    Supports:
    - Inline JSON: '{"key": "value"}'
    - File reference: @data.json

    Args:
        data_str: JSON string or @file.json

    Returns:
        Parsed data dictionary
    """
    if data_str.startswith("@"):
        file_path = Path(data_str[1:])
        with file_path.open() as f:
            return json.load(f)
    return json.loads(data_str)


def output_json(data: dict | list) -> None:
    """Output data as JSON.

    Args:
        data: Data to output as JSON
    """
    click.echo(json.dumps(data, indent=2))
