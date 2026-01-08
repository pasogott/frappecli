"""File management commands."""

import json
from pathlib import Path

import click
from rich.console import Console
from rich.progress import Progress
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


@click.command(name="upload")
@click.argument("file_path", type=click.Path(exists=True, path_type=Path))
@click.option("--public", is_flag=True, help="Upload as public file (default: private)")
@click.option("--folder", default="Home", help="Target folder")
@click.option("--attach", nargs=2, help="Attach to doctype and docname")
@click.option("--field", help="Field name for attachment")
@click.option("--optimize", is_flag=True, help="Optimize images")
@click.pass_context
def upload_file(
    ctx: click.Context,
    file_path: Path,
    public: bool,
    folder: str,
    attach: tuple[str, str] | None,
    field: str | None,
    optimize: bool,
) -> None:
    """Upload a file to Frappe."""
    client = _get_client(ctx)

    # Prepare multipart data
    files = {"file": (file_path.name, file_path.open("rb"))}

    data = {
        "is_private": "0" if public else "1",
        "folder": folder,
    }

    if attach:
        doctype, docname = attach
        data["doctype"] = doctype
        data["docname"] = docname
        if field:
            data["fieldname"] = field

    if optimize:
        data["optimize"] = "1"

    # Upload
    console.print(f"[cyan]Uploading {file_path.name}...[/cyan]")

    # Use raw session request for multipart upload
    response = client.session.post(
        f"{client.base_url}/api/method/upload_file",
        files=files,
        data=data,
        timeout=client.timeout,
    )

    if response.ok:
        result = response.json().get("message", {})
        console.print(f"[green]✓[/green] Uploaded: [bold]{result.get('file_url')}[/bold]")
        if attach:
            console.print(f"[green]  Attached to {attach[0]}: {attach[1]}[/green]")
    else:
        console.print(f"[red]✗ Upload failed: {response.text}[/red]")


@click.command(name="download")
@click.argument("file_url")
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output file path")
@click.pass_context
def download_file(ctx: click.Context, file_url: str, output: Path | None) -> None:
    """Download a file from Frappe."""
    client = _get_client(ctx)

    # Determine output path
    if output is None:
        output = Path(file_url.split("/")[-1])

    console.print(f"[cyan]Downloading {file_url}...[/cyan]")

    # Download file
    response = client.session.get(
        f"{client.base_url}{file_url}",
        timeout=client.timeout,
        stream=True,
    )

    if response.ok:
        with output.open("wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        console.print(f"[green]✓[/green] Downloaded to: [bold]{output}[/bold]")
    else:
        console.print(f"[red]✗ Download failed: {response.status_code}[/red]")


@click.group(name="files")
def files_group() -> None:
    """File management commands."""


@files_group.command(name="list")
@click.option("--folder", default="Home", help="Folder to list")
@click.option("--attached-to", nargs=2, help="Filter by doctype and docname")
@click.pass_context
def list_files(
    ctx: click.Context,
    folder: str,
    attached_to: tuple[str, str] | None,
) -> None:
    """List files in a folder."""
    client = _get_client(ctx)
    output_json = ctx.obj.get("output_json", False)

    if attached_to:
        # List files attached to a document
        doctype, docname = attached_to
        filters = {"attached_to_doctype": doctype, "attached_to_name": docname}
        result = client.get("/api/resource/File", params={"filters": json.dumps(filters)})
    else:
        # List files in folder
        result = client.post(
            "/api/method/frappe.core.api.file.get_files_in_folder",
            data={"folder": folder, "start": 0, "page_length": 100},
        )

    if output_json:
        click.echo(json.dumps(result, indent=2))
    else:
        if not result:
            console.print("[yellow]No files found[/yellow]")
            return

        table = Table(title=f"Files in {folder}")
        table.add_column("Name", style="cyan")
        table.add_column("Size", style="green")
        table.add_column("Modified", style="yellow")

        for file in result:
            table.add_row(
                file.get("file_name", ""),
                str(file.get("file_size", "")),
                str(file.get("modified", "")),
            )

        console.print(table)
        console.print(f"\n[bold]Total:[/bold] {len(result)} files")


@files_group.command(name="search")
@click.argument("query")
@click.pass_context
def search_files(ctx: click.Context, query: str) -> None:
    """Search for files by name."""
    client = _get_client(ctx)
    output_json = ctx.obj.get("output_json", False)

    result = client.post(
        "/api/method/frappe.core.api.file.get_files_by_search_text",
        data={"text": query},
    )

    if output_json:
        click.echo(json.dumps(result, indent=2))
    else:
        if not result:
            console.print("[yellow]No files found[/yellow]")
            return

        table = Table(title=f'Search results for "{query}"')
        table.add_column("Name", style="cyan")
        table.add_column("URL", style="green")

        for file in result:
            table.add_row(file.get("name", ""), file.get("file_url", ""))

        console.print(table)
        console.print(f"\n[bold]Total:[/bold] {len(result)} files")


@click.command(name="bulk-upload")
@click.argument("pattern")
@click.option("--folder", default="Home", help="Target folder")
@click.option("--public", is_flag=True, help="Upload as public files")
@click.option("--recursive", "-r", is_flag=True, help="Recursive directory search")
@click.pass_context
def bulk_upload(
    ctx: click.Context,
    pattern: str,
    folder: str,
    public: bool,
    recursive: bool,
) -> None:
    """Bulk upload files matching pattern."""
    client = _get_client(ctx)

    # Find files
    files = list(Path().rglob(pattern)) if recursive else list(Path().glob(pattern))

    if not files:
        console.print("[yellow]No files found matching pattern[/yellow]")
        return

    console.print(f"[cyan]Found {len(files)} files to upload[/cyan]")

    success = 0
    failed = 0

    with Progress() as progress:
        task = progress.add_task("[cyan]Uploading...", total=len(files))

        for file_path in files:
            try:
                files_data = {"file": (file_path.name, file_path.open("rb"))}
                data = {"is_private": "0" if public else "1", "folder": folder}

                response = client.session.post(
                    f"{client.base_url}/api/method/upload_file",
                    files=files_data,
                    data=data,
                    timeout=client.timeout,
                )

                if response.ok:
                    success += 1
                else:
                    failed += 1
                    console.print(f"[red]✗ Failed: {file_path.name}[/red]")

            except Exception as e:
                failed += 1
                console.print(f"[red]✗ Error uploading {file_path.name}: {e}[/red]")

            progress.update(task, advance=1)

    console.print(f"\n[bold]Summary:[/bold] {success} successful, {failed} failed")
