"""Site-related commands."""

import json

import click
from rich.console import Console
from rich.table import Table

from frappecli.client import FrappeClient
from frappecli.config import Config

console = Console()


def _get_client(ctx: click.Context) -> FrappeClient:
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
    client = _get_client(ctx)
    output_json = ctx.obj.get("output_json", False)

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


@click.command()
@click.argument("doctype")
@click.option("--fields", is_flag=True, help="Show only field list")
@click.pass_context
def doctype_info(ctx: click.Context, doctype: str, fields: bool) -> None:
    """Get detailed information about a doctype."""
    client = _get_client(ctx)
    output_json = ctx.obj.get("output_json", False)

    # Get doctype metadata
    result = client.get(f"/api/resource/DocType/{doctype}")

    if output_json:
        click.echo(json.dumps(result, indent=2))
    elif fields:
        # Show only fields
        table = Table(title=f"Fields in {doctype}")
        table.add_column("Fieldname", style="cyan")
        table.add_column("Label", style="green")
        table.add_column("Type", style="yellow")
        table.add_column("Options", style="magenta")

        for field in result.get("fields", []):
            table.add_row(
                field.get("fieldname", ""),
                field.get("label", ""),
                field.get("fieldtype", ""),
                field.get("options", ""),
            )

        console.print(table)
        console.print(f"\n[bold]Total:[/bold] {len(result.get('fields', []))} fields")
    else:
        # Show full doctype info
        console.print(f"\n[bold cyan]{result.get('name')}[/bold cyan]")
        console.print(f"[green]Module:[/green] {result.get('module', 'N/A')}")
        console.print(f"[green]Type:[/green] {'Custom' if result.get('custom') else 'Standard'}")
        console.print(f"[green]Single:[/green] {'Yes' if result.get('issingle') else 'No'}")
        console.print(
            f"[green]Submittable:[/green] {'Yes' if result.get('is_submittable') else 'No'}"
        )
        console.print(
            f"[green]Track Changes:[/green] {'Yes' if result.get('track_changes') else 'No'}"
        )

        # Show fields summary
        fields_data = result.get("fields", [])
        console.print(f"\n[bold]Fields:[/bold] {len(fields_data)}")

        # Show permissions summary
        permissions = result.get("permissions", [])
        console.print(f"[bold]Permissions:[/bold] {len(permissions)} roles")
