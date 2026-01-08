"""Doctype CRUD commands."""

import json
from pathlib import Path

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


def _load_data(data_str: str) -> dict:
    """Load data from JSON string or file.

    Args:
        data_str: JSON string or @file.json

    Returns:
        Parsed data dictionary
    """
    if data_str.startswith("@"):
        # Load from file
        file_path = Path(data_str[1:])
        with file_path.open() as f:
            return json.load(f)
    return json.loads(data_str)


@click.command(name="list")
@click.argument("doctype")
@click.option("--filters", help="Filter as JSON")
@click.option("--fields", help="Fields to return (comma-separated)")
@click.option("--limit", default=20, help="Limit results")
@click.option("--offset", default=0, help="Offset for pagination")
@click.option("--order-by", help="Order by field")
@click.pass_context
def list_documents(
    ctx: click.Context,
    doctype: str,
    filters: str | None,
    fields: str | None,
    limit: int,
    offset: int,
    order_by: str | None,
) -> None:
    """List documents of a doctype."""
    client = _get_client(ctx)
    output_json = ctx.obj.get("output_json", False)

    # Build query params
    params = {"limit_page_length": limit, "limit_start": offset}

    if filters:
        params["filters"] = _load_data(filters)

    if fields:
        params["fields"] = fields.split(",")

    if order_by:
        params["order_by"] = order_by

    # Fetch documents
    result = client.get(f"/api/resource/{doctype}", params=params)

    if output_json:
        click.echo(json.dumps(result, indent=2))
    else:
        # Display as table
        if not result:
            console.print("[yellow]No documents found[/yellow]")
            return

        # Get field names from first document
        field_names = list(result[0].keys())[:5]  # Show first 5 fields

        table = Table(title=f"{doctype} Documents")
        for field in field_names:
            table.add_column(field, style="cyan")

        for doc in result:
            table.add_row(*[str(doc.get(f, "")) for f in field_names])

        console.print(table)
        console.print(f"\n[bold]Total:[/bold] {len(result)} documents")


@click.command(name="get")
@click.argument("doctype")
@click.argument("name")
@click.pass_context
def get_document(ctx: click.Context, doctype: str, name: str) -> None:
    """Get a single document."""
    client = _get_client(ctx)
    output_json = ctx.obj.get("output_json", False)

    # Get document
    result = client.get(f"/api/resource/{doctype}/{name}")

    if output_json:
        click.echo(json.dumps(result, indent=2))
    else:
        console.print(f"\n[bold cyan]{doctype}: {result.get('name')}[/bold cyan]\n")
        for key, value in result.items():
            if not key.startswith("_") and value:
                console.print(f"[green]{key}:[/green] {value}")


@click.command(name="create")
@click.argument("doctype")
@click.option("--data", required=True, help="Document data as JSON or @file.json")
@click.option("--dry-run", is_flag=True, help="Show what would be created")
@click.pass_context
def create_document(ctx: click.Context, doctype: str, data: str, dry_run: bool) -> None:
    """Create a new document."""
    client = _get_client(ctx)
    output_json = ctx.obj.get("output_json", False)

    # Parse data
    doc_data = _load_data(data)

    if dry_run:
        console.print("[yellow]DRY RUN - Would create:[/yellow]")
        console.print(json.dumps(doc_data, indent=2))
        return

    # Create document
    result = client.post(f"/api/resource/{doctype}", data=doc_data)

    if output_json:
        click.echo(json.dumps(result, indent=2))
    else:
        console.print(f"[green]✓[/green] Created {doctype}: [bold]{result.get('name')}[/bold]")


@click.command(name="update")
@click.argument("doctype")
@click.argument("name")
@click.option("--data", required=True, help="Update data as JSON or @file.json")
@click.option("--dry-run", is_flag=True, help="Show what would be updated")
@click.pass_context
def update_document(ctx: click.Context, doctype: str, name: str, data: str, dry_run: bool) -> None:
    """Update an existing document."""
    client = _get_client(ctx)
    output_json = ctx.obj.get("output_json", False)

    # Parse data
    update_data = _load_data(data)

    if dry_run:
        console.print(f"[yellow]DRY RUN - Would update {doctype} {name}:[/yellow]")
        console.print(json.dumps(update_data, indent=2))
        return

    # Update document
    result = client.put(f"/api/resource/{doctype}/{name}", data=update_data)

    if output_json:
        click.echo(json.dumps(result, indent=2))
    else:
        console.print(f"[green]✓[/green] Updated {doctype}: [bold]{name}[/bold]")


@click.command(name="delete")
@click.argument("doctype")
@click.argument("name")
@click.option("--yes", is_flag=True, help="Skip confirmation")
@click.pass_context
def delete_document(ctx: click.Context, doctype: str, name: str, yes: bool) -> None:
    """Delete a document."""
    client = _get_client(ctx)

    # Confirm deletion
    if not yes and not click.confirm(f"Delete {doctype} '{name}'?"):
        console.print("[yellow]Cancelled[/yellow]")
        return

    # Delete document
    client.delete(f"/api/resource/{doctype}/{name}")

    console.print(f"[green]✓[/green] Deleted {doctype}: [bold]{name}[/bold]")
