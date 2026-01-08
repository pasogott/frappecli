"""Site-related commands."""

import json

import click
from rich.console import Console
from rich.table import Table

from frappecli.client import FrappeClient
from frappecli.config import Config

console = Console()


def _get_client(ctx: click.Context) -> FrappeClient:
    """Get configured Frappe client from context."""
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


def _show_field_details(result: dict, doctype: str) -> None:
    """Show detailed field list with all attributes."""
    table = Table(title=f"Fields in {doctype}", show_lines=True)
    table.add_column("Fieldname", style="cyan", no_wrap=True)
    table.add_column("Label", style="green")
    table.add_column("Type", style="yellow")
    table.add_column("Required", style="red", justify="center")
    table.add_column("Options/Link", style="magenta")
    table.add_column("Read Only", style="dim", justify="center")

    max_select_options = 3
    for field in result.get("fields", []):
        fieldtype = field.get("fieldtype", "")
        options = field.get("options", "")

        # Format options based on field type
        if fieldtype == "Link" and options:
            options = f"→ {options}"
        elif fieldtype == "Select" and options:
            # Show first few select options
            opts = options.split("\n")[:max_select_options]
            options = ", ".join(opts)
            if len(options.split("\n")) > max_select_options:
                options += "..."

        # Required and read-only indicators
        required = "✓" if field.get("reqd") else ""
        read_only = "✓" if field.get("read_only") else ""

        table.add_row(
            field.get("fieldname", ""),
            field.get("label", ""),
            fieldtype,
            required,
            options,
            read_only,
        )

    console.print(table)
    console.print(f"\n[bold]Total:[/bold] {len(result.get('fields', []))} fields")

    # Show field type summary
    field_types: dict[str, int] = {}
    for field in result.get("fields", []):
        ft = field.get("fieldtype", "Unknown")
        field_types[ft] = field_types.get(ft, 0) + 1

    console.print("\n[bold]Field Types:[/bold]")
    for ft, count in sorted(field_types.items(), key=lambda x: -x[1]):
        console.print(f"  • {ft}: {count}")


def _show_doctype_summary(result: dict) -> None:
    """Show doctype summary with key information."""
    console.print(f"\n[bold cyan]{result.get('name')}[/bold cyan]")
    console.print(f"[green]Module:[/green] {result.get('module', 'N/A')}")
    console.print(f"[green]Type:[/green] {'Custom' if result.get('custom') else 'Standard'}")
    console.print(f"[green]Single:[/green] {'Yes' if result.get('issingle') else 'No'}")
    console.print(f"[green]Submittable:[/green] {'Yes' if result.get('is_submittable') else 'No'}")
    console.print(f"[green]Track Changes:[/green] {'Yes' if result.get('track_changes') else 'No'}")

    # Analyze fields
    fields_data = result.get("fields", [])
    required_fields = [f for f in fields_data if f.get("reqd")]
    link_fields = [f for f in fields_data if f.get("fieldtype") == "Link"]

    console.print(f"\n[bold]Fields:[/bold] {len(fields_data)} total")
    console.print(f"  • Required: {len(required_fields)}")
    console.print(f"  • Links to other doctypes: {len(link_fields)}")

    # Show required fields
    max_required_show = 5
    if required_fields:
        console.print("\n[bold yellow]Required Fields:[/bold yellow]")
        for field in required_fields[:max_required_show]:
            fieldtype = field.get("fieldtype", "")
            label = field.get("label", field.get("fieldname", ""))
            options = field.get("options", "")

            if fieldtype == "Link" and options:
                console.print(f"  • {label} ({fieldtype} → {options})")
            else:
                console.print(f"  • {label} ({fieldtype})")

        if len(required_fields) > max_required_show:
            remaining = len(required_fields) - max_required_show
            console.print(f"  ... and {remaining} more")

    # Show link fields (if not too many)
    max_links_show = 10
    if link_fields and len(link_fields) <= max_links_show:
        console.print("\n[bold cyan]Links to other Doctypes:[/bold cyan]")
        for field in link_fields:
            label = field.get("label", field.get("fieldname", ""))
            target = field.get("options", "")
            console.print(f"  • {label} → {target}")

    # Show permissions summary
    permissions = result.get("permissions", [])
    console.print(f"\n[bold]Permissions:[/bold] {len(permissions)} roles")

    console.print("\n[dim]💡 Use --fields flag for detailed field list[/dim]")


@click.command()
@click.argument("doctype")
@click.option("--fields", is_flag=True, help="Show detailed field list")
@click.pass_context
def doctype_info(ctx: click.Context, doctype: str, fields: bool) -> None:
    """Get detailed information about a doctype.

    Shows:
    - Basic doctype metadata (module, type, etc.)
    - Required fields with their types
    - Links to other doctypes
    - Field type summary (with --fields flag)
    """
    client = _get_client(ctx)
    output_json = ctx.obj.get("output_json", False)

    # Get doctype metadata
    result = client.get(f"/api/resource/DocType/{doctype}")

    if output_json:
        click.echo(json.dumps(result, indent=2))
    elif fields:
        _show_field_details(result, doctype)
    else:
        _show_doctype_summary(result)
