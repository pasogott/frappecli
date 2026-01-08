"""Shared helper functions for frappecli."""

import json
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any, Literal

import click
from rich.console import Console
from rich.table import Table

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


def output_as_json(data: dict | list | Any) -> None:
    """Output data as JSON.

    Args:
        data: Data to output as JSON
    """
    click.echo(json.dumps(data, indent=2))


def get_output_format(ctx: click.Context) -> Literal["json", "table"]:
    """Get output format from context.

    Args:
        ctx: Click context with output_json flag

    Returns:
        Output format: "json" or "table"
    """
    return "json" if ctx.obj.get("output_json", False) else "table"


def output_data(
    data: Any,
    output_format: Literal["json", "table"],
    render_table: Callable[[Any], None] | None = None,
) -> None:
    """Output data in requested format.

    Args:
        data: Data to output
        output_format: Output format ("json" or "table")
        render_table: Optional function to render table format
    """
    if output_format == "json":
        output_as_json(data)
    elif render_table:
        render_table(data)
    else:
        console.print(data)


def create_simple_table(
    title: str,
    data: list[dict],
    columns: list[tuple[str, str]],
    max_columns: int | None = None,
) -> Table:
    """Create a simple Rich table from data.

    Args:
        title: Table title
        data: List of dictionaries to display
        columns: List of (field_name, column_title) tuples
        max_columns: Optional limit on number of columns to show

    Returns:
        Configured Rich Table
    """
    table = Table(title=title)

    # Limit columns if needed
    display_columns = columns[:max_columns] if max_columns else columns

    for _, column_title in display_columns:
        table.add_column(column_title, style="cyan")

    for row in data:
        values = [str(row.get(field, "")) for field, _ in display_columns]
        table.add_row(*values)

    return table


def with_client(f: Callable) -> Callable:
    """Decorator to inject Frappe client into command.

    Automatically gets client from context and passes as 'client' kwarg.

    Usage:
        @click.command()
        @click.pass_context
        @with_client
        def my_command(ctx, client, ...):
            # client is automatically injected
            result = client.get("/api/resource/User")
    """

    @wraps(f)
    def wrapper(ctx: click.Context, *args: Any, **kwargs: Any) -> Any:
        client = get_client(ctx)
        kwargs["client"] = client
        return f(ctx, *args, **kwargs)

    return wrapper
