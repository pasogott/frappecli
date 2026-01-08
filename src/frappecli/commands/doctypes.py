"""Document CRUD commands."""

import click
from rich.table import Table

from frappecli.helpers import console, get_client, load_data, output_json


@click.group(name="doc")
def doc_group() -> None:
    """Document CRUD operations."""


@doc_group.command(name="list")
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
    client = get_client(ctx)
    output_json_flag = ctx.obj.get("output_json", False)

    # Build query params
    params = {"limit_page_length": limit, "limit_start": offset}

    if filters:
        params["filters"] = load_data(filters)

    if fields:
        params["fields"] = fields.split(",")

    if order_by:
        params["order_by"] = order_by

    # Fetch documents
    result = client.get(f"/api/resource/{doctype}", params=params)

    if output_json_flag:
        output_json(result)
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


@doc_group.command(name="get")
@click.argument("doctype")
@click.argument("name")
@click.pass_context
def get_document(ctx: click.Context, doctype: str, name: str) -> None:
    """Get a single document."""
    client = get_client(ctx)
    output_json_flag = ctx.obj.get("output_json", False)

    # Get document
    result = client.get(f"/api/resource/{doctype}/{name}")

    if output_json_flag:
        output_json(result)
    else:
        console.print(f"\n[bold cyan]{doctype}: {result.get('name')}[/bold cyan]\n")
        for key, value in result.items():
            if not key.startswith("_") and value:
                console.print(f"[green]{key}:[/green] {value}")


@doc_group.command(name="create")
@click.argument("doctype")
@click.option("--data", required=True, help="Document data as JSON or @file.json")
@click.option("--dry-run", is_flag=True, help="Show what would be created")
@click.pass_context
def create_document(
    ctx: click.Context, doctype: str, data: str, dry_run: bool
) -> None:
    """Create a new document."""
    client = get_client(ctx)
    output_json_flag = ctx.obj.get("output_json", False)

    # Parse data
    doc_data = load_data(data)

    if dry_run:
        console.print("[yellow]DRY RUN - Would create:[/yellow]")
        output_json(doc_data)
        return

    # Create document
    result = client.post(f"/api/resource/{doctype}", data=doc_data)

    if output_json_flag:
        output_json(result)
    else:
        console.print(
            f"[green]✓[/green] Created {doctype}: [bold]{result.get('name')}[/bold]"
        )


@doc_group.command(name="update")
@click.argument("doctype")
@click.argument("name")
@click.option("--data", required=True, help="Update data as JSON or @file.json")
@click.option("--dry-run", is_flag=True, help="Show what would be updated")
@click.pass_context
def update_document(
    ctx: click.Context, doctype: str, name: str, data: str, dry_run: bool
) -> None:
    """Update an existing document."""
    client = get_client(ctx)
    output_json_flag = ctx.obj.get("output_json", False)

    # Parse data
    update_data = load_data(data)

    if dry_run:
        console.print(f"[yellow]DRY RUN - Would update {doctype} {name}:[/yellow]")
        output_json(update_data)
        return

    # Update document
    result = client.put(f"/api/resource/{doctype}/{name}", data=update_data)

    if output_json_flag:
        output_json(result)
    else:
        console.print(f"[green]✓[/green] Updated {doctype}: [bold]{name}[/bold]")


@doc_group.command(name="delete")
@click.argument("doctype")
@click.argument("name")
@click.option("--yes", is_flag=True, help="Skip confirmation")
@click.pass_context
def delete_document(ctx: click.Context, doctype: str, name: str, yes: bool) -> None:
    """Delete a document."""
    client = get_client(ctx)

    # Confirm deletion
    if not yes and not click.confirm(f"Delete {doctype} '{name}'?"):
        console.print("[yellow]Cancelled[/yellow]")
        return

    # Delete document
    client.delete(f"/api/resource/{doctype}/{name}")

    console.print(f"[green]✓[/green] Deleted {doctype}: [bold]{name}[/bold]")
