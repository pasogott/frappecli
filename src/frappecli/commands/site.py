"""Site-related commands."""

import click
from rich.console import Console
from rich.table import Table

from frappecli.client import FrappeClient
from frappecli.config import Config

console = Console()


@click.command()
@click.option("--module", "-m", help="Filter by module")
@click.option("--custom", is_flag=True, help="Show only custom doctypes")
@click.option("--standard", is_flag=True, help="Show only standard doctypes")
@click.pass_context
def doctypes(
    ctx: click.Context,
    module: str | None,
    custom: bool,
    standard: bool,
) -> None:
    """List all available doctypes."""
    config_path = ctx.obj.get("config")
    site_name = ctx.obj.get("site")
    output_json = ctx.obj.get("output_json", False)

    # Load config and get site
    config = Config(config_path) if config_path else Config()
    site_config = (
        config.get_site_config(site_name)
        if site_name
        else config.get_default_site_config()
    )

    # Create client
    client = FrappeClient(
        base_url=site_config["url"],
        api_key=site_config["api_key"],
        api_secret=site_config["api_secret"],
    )

    # Fetch doctypes
    filters = {}
    if module:
        filters["module"] = module
    if custom:
        filters["custom"] = 1
    if standard:
        filters["custom"] = 0

    result = client.post(
        "/api/method/frappe.client.get_list",
        data={
            "doctype": "DocType",
            "fields": ["name", "module", "custom", "issingle"],
            "filters": filters,
            "limit_page_length": 0,
        },
    )

    if output_json:
        import json

        click.echo(json.dumps(result, indent=2))
    else:
        # Display as table
        table = Table(title="Doctypes")
        table.add_column("Name", style="cyan")
        table.add_column("Module", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Single", style="magenta")

        for dt in result:
            dt_type = "Custom" if dt.get("custom") else "Standard"
            is_single = "Yes" if dt.get("issingle") else "No"
            table.add_row(dt["name"], dt.get("module", ""), dt_type, is_single)

        console.print(table)
        console.print(f"\n[bold]Total:[/bold] {len(result)} doctypes")
