"""CLI entry point for frappecli."""

import sys
from pathlib import Path

import click
from rich.console import Console

from frappecli.commands.doctypes import doc_group
from frappecli.commands.files import bulk_upload, download_file, files_group, upload_file
from frappecli.commands.reports import call_rpc, execute_report, reports_group
from frappecli.commands.site import site_group

console = Console()


@click.group()
@click.option(
    "--site",
    "-s",
    help="Site name from config (overrides default)",
    type=str,
)
@click.option(
    "--config",
    "-c",
    help="Path to config file",
    type=click.Path(exists=False, path_type=Path),
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output as JSON",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Verbose output",
)
@click.version_option(version="0.1.0", prog_name="frappecli")
@click.pass_context
def cli(
    ctx: click.Context,
    site: str | None,
    config: Path | None,
    output_json: bool,
    verbose: bool,
) -> None:
    """frappecli - Frappe REST API CLI tool.

    Manage Frappe instances via REST API from the command line.

    Examples:
      frappecli site doctypes
      frappecli doc list "User" --limit 10
      frappecli files upload document.pdf
      frappecli reports list

    Documentation: https://github.com/pasogott/frappecli
    """
    # Store global options in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["site"] = site
    ctx.obj["config"] = config
    ctx.obj["output_json"] = output_json
    ctx.obj["verbose"] = verbose


# Register command groups
cli.add_command(site_group)
cli.add_command(doc_group)
cli.add_command(files_group)
cli.add_command(reports_group)

# Register standalone commands
cli.add_command(upload_file)
cli.add_command(download_file)
cli.add_command(bulk_upload)
cli.add_command(execute_report)
cli.add_command(call_rpc)


def main() -> None:
    """Main entry point."""
    cli(obj={})


if __name__ == "__main__":
    sys.exit(main())
