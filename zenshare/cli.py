"""Command line interface for ZenShare."""

from __future__ import annotations

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from .app import ZenShareApp
from .constants import APP_NAME

console = Console()


def _build_app() -> ZenShareApp:
    """Create the default ZenShare application object."""

    return ZenShareApp.default()


def _print_header(title: str) -> None:
    console.print(Panel.fit(title, title=APP_NAME))


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def main() -> None:
    """ZenShare command line entry point."""


@main.command()
def start() -> None:
    """Start presentation mode."""

    app = _build_app()
    _print_header("Preparing Presentation Mode...")
    result = app.start()
    console.print(f"[green]✓[/green] {result.message}")


@main.command()
def stop() -> None:
    """Stop presentation mode and restore the previous state."""

    app = _build_app()
    _print_header("Restoring Desktop State...")
    result = app.stop()
    console.print(f"[green]✓[/green] {result.message}")


@main.command()
def status() -> None:
    """Display the current ZenShare state."""

    app = _build_app()
    snapshot = app.status()
    table = Table(title=f"{APP_NAME} Status")
    table.add_column("Field", style="cyan")
    table.add_column("Value", style="white")
    table.add_row("State file present", str(snapshot["state_exists"]))
    table.add_row("State data", str(snapshot["state"]))
    table.add_row("Configuration", str(snapshot["config"]))
    console.print(table)


@main.command()
def config() -> None:
    """Show the active configuration."""

    app = _build_app()
    console.print(app.config().model_dump_json(indent=2))


@main.command()
@click.option("--tail", default=50, show_default=True, help="Number of log lines to display.")
def logs(tail: int) -> None:
    """Display recent log entries."""

    app = _build_app()
    log_path = app.logs_path()
    if not log_path.exists():
        console.print("No log file has been created yet.")
        return

    lines = log_path.read_text(encoding="utf-8").splitlines()
    recent_lines = lines[-tail:]
    console.print(Panel("\n".join(recent_lines) if recent_lines else "No log entries found.", title=str(log_path)))


if __name__ == "__main__":
    main()