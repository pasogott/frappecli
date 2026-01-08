"""Report and RPC commands."""

import csv
import json
import time
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


@click.group(name="reports")
def reports_group() -> None:
    """Report management commands."""


@reports_group.command(name="list")
@click.option("--module", "-m", help="Filter by module")
@click.pass_context
def list_reports(ctx: click.Context, module: str | None) -> None:
    """List all available reports."""
    client = _get_client(ctx)
    output_json = ctx.obj.get("output_json", False)

    # Fetch reports
    filters = {}
    if module:
        filters["module"] = module

    result = client.get(
        "/api/resource/Report",
        params={
            "fields": json.dumps(["name", "module", "report_type"]),
            "filters": json.dumps(filters),
        },
    )

    if output_json:
        click.echo(json.dumps(result, indent=2))
    else:
        if not result:
            console.print("[yellow]No reports found[/yellow]")
            return

        table = Table(title="Available Reports")
        table.add_column("Name", style="cyan")
        table.add_column("Module", style="green")
        table.add_column("Type", style="yellow")

        for report in result:
            table.add_row(
                report.get("name", ""),
                report.get("module", ""),
                report.get("report_type", ""),
            )

        console.print(table)
        console.print(f"\n[bold]Total:[/bold] {len(result)} reports")


@click.command(name="report")
@click.argument("report_name")
@click.option("--filters", help="Report filters as JSON")
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Save to file")
@click.pass_context
def execute_report(
    ctx: click.Context,
    report_name: str,
    filters: str | None,
    output: Path | None,
) -> None:
    """Execute a report and show results."""
    client = _get_client(ctx)
    output_json = ctx.obj.get("output_json", False)

    # Parse filters
    report_filters = json.loads(filters) if filters else {}

    # Execute report
    start_time = time.time()
    result = client.post(
        "/api/method/frappe.desk.query_report.run",
        data={"report_name": report_name, "filters": report_filters},
    )
    elapsed = time.time() - start_time

    # Save to file if requested
    if output:
        with output.open("w") as f:
            if output.suffix == ".json":
                json.dump(result, f, indent=2)
            elif output.suffix == ".csv":
                # Simple CSV export
                if result and "result" in result:
                    data = result["result"]
                    if data:
                        fieldnames = data[0].keys()
                        writer = csv.DictWriter(f, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(data)
            else:
                json.dump(result, f, indent=2)

        console.print(f"[green]✓[/green] Saved to: [bold]{output}[/bold]")

    # Display results
    if output_json or not result:
        click.echo(json.dumps(result, indent=2))
    else:
        console.print(f"\n[bold cyan]{report_name}[/bold cyan]")
        console.print(f"[green]Execution time:[/green] {elapsed:.2f}s")

        # Show data summary
        if result.get("result"):
            console.print(f"[green]Rows:[/green] {len(result['result'])}")
        else:
            console.print("[yellow]No data returned[/yellow]")


@click.command(name="call")
@click.argument("method")
@click.option("--args", help="Method arguments as JSON or @file.json")
@click.pass_context
def call_rpc(ctx: click.Context, method: str, args: str | None) -> None:
    """Call a custom RPC method."""
    client = _get_client(ctx)
    output_json = ctx.obj.get("output_json", False)

    # Parse arguments
    method_args = {}
    if args:
        if args.startswith("@"):
            # Load from file
            file_path = Path(args[1:])
            with file_path.open() as f:
                method_args = json.load(f)
        else:
            method_args = json.loads(args)

    # Call method
    result = client.post(f"/api/method/{method}", data=method_args)

    if output_json:
        click.echo(json.dumps(result, indent=2))
    else:
        console.print(f"\n[bold cyan]Result from {method}:[/bold cyan]\n")
        if result is None:
            console.print("[yellow]No return value[/yellow]")
        elif isinstance(result, (dict, list)):
            console.print(json.dumps(result, indent=2))
        else:
            console.print(str(result))


@click.command(name="status")
@click.option("--detailed", is_flag=True, help="Show detailed information")
@click.pass_context
def site_status(ctx: click.Context, detailed: bool) -> None:
    """Show site status and version information."""
    client = _get_client(ctx)
    output_json = ctx.obj.get("output_json", False)

    # Get version info
    result = client.get("/api/method/version")

    if output_json:
        click.echo(json.dumps(result, indent=2))
    else:
        console.print("\n[bold cyan]Site Status[/bold cyan]\n")

        # Show Frappe version
        if "message" in result:
            console.print(
                f"[green]Frappe Version:[/green] {result['message'].get('frappe_version', 'N/A')}"
            )

        # Show app versions
        if detailed and "message" in result:
            apps = result["message"].get("apps", [])
            if apps:
                console.print("\n[bold]Installed Apps:[/bold]")
                for app in apps:
                    console.print(f"  • {app}")

        # Test connectivity
        console.print(f"\n[green]✓[/green] Site is reachable at: {client.base_url}")
