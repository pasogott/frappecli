"""Report and RPC commands."""

import csv
import json
import time
from pathlib import Path

import click
from rich.table import Table

from frappecli.helpers import console, get_client, get_output_format, load_data, output_data


@click.group(name="reports")
def reports_group() -> None:
    """Report management commands."""


@reports_group.command(name="list")
@click.option("--module", "-m", help="Filter by module")
@click.pass_context
def list_reports(ctx: click.Context, module: str | None) -> None:
    """List all available reports."""
    client = get_client(ctx)
    output_format = get_output_format(ctx)

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

    def render_table(data: list[dict]) -> None:
        if not data:
            console.print("[yellow]No reports found[/yellow]")
            return

        table = Table(title="Available Reports")
        table.add_column("Name", style="cyan")
        table.add_column("Module", style="green")
        table.add_column("Type", style="yellow")

        for report in data:
            table.add_row(
                report.get("name", ""),
                report.get("module", ""),
                report.get("report_type", ""),
            )

        console.print(table)
        console.print(f"\n[bold]Total:[/bold] {len(data)} reports")

    output_data(result, output_format, render_table)


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
    client = get_client(ctx)
    output_format = get_output_format(ctx)

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
                # CSV export - collect all unique fieldnames from all rows
                if result and "result" in result:
                    data = result["result"]
                    if data:
                        # Collect all unique field names from all rows
                        all_fieldnames = set()
                        for row in data:
                            all_fieldnames.update(row.keys())
                        fieldnames = sorted(all_fieldnames)

                        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
                        writer.writeheader()
                        writer.writerows(data)
            else:
                json.dump(result, f, indent=2)

        console.print(f"[green]✓[/green] Saved to: [bold]{output}[/bold]")

    # Display results
    def render_table(data: dict) -> None:
        console.print(f"\n[bold cyan]{report_name}[/bold cyan]")
        console.print(f"[green]Execution time:[/green] {elapsed:.2f}s")

        # Show data summary
        if data.get("result"):
            console.print(f"[green]Rows:[/green] {len(data['result'])}")
        else:
            console.print("[yellow]No data returned[/yellow]")

    output_data(result, output_format, render_table)


@click.command(name="call")
@click.argument("method")
@click.option("--args", help="Method arguments as JSON or @file.json")
@click.pass_context
def call_rpc(ctx: click.Context, method: str, args: str | None) -> None:
    """Call a custom RPC method."""
    client = get_client(ctx)
    output_format = get_output_format(ctx)

    # Parse arguments
    method_args = {}
    if args:
        method_args = load_data(args)

    # Call method
    result = client.post(f"/api/method/{method}", data=method_args)

    def render_table(data: any) -> None:
        console.print(f"\n[bold cyan]Result from {method}:[/bold cyan]\n")
        if data is None:
            console.print("[yellow]No return value[/yellow]")
        elif isinstance(data, dict | list):
            console.print(json.dumps(data, indent=2))
        else:
            console.print(str(data))

    output_data(result, output_format, render_table)
