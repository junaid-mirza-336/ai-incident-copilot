import asyncio
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from incident_copilot.ingestion.parser import LogParser
from incident_copilot.ai.client import AIClient

app = typer.Typer(
    help="AI Incident Copilot - Analyze IT logs and get AI-powered root cause analysis.",
    no_args_is_help=True
)
console = Console()


def get_severity_color(severity: str) -> str:
    """Returns rich color tag based on severity level."""
    sev = severity.upper()
    if sev == "CRITICAL":
        return "bold red"
    elif sev == "ERROR":
        return "red"
    elif sev == "WARN" or sev == "WARNING":
        return "yellow"
    else:
        return "green"


@app.command()
def main(
    file_path: Path = typer.Argument(..., help="Path to the log file to analyze"),
):
    """Analyze an IT incident log file using AI and display a rich formatted report."""
    if not file_path.exists():
        console.print(f"[bold red]Error:[/bold red] Log file not found at '{file_path}'. Please check the path and try again.")
        raise typer.Exit(code=1)

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            raw_content = f.read()
    except Exception as e:
        console.print(f"[bold red]Error reading file:[/bold red] {e}")
        raise typer.Exit(code=1)

    # 1. Parse logs
    console.print(f"[bold cyan]Parsing log file:[/bold cyan] {file_path} ...")
    payload = LogParser.parse_text(raw_content)
    sev_color = get_severity_color(payload.detected_severity)

    console.print(f"[green]Parsed {len(payload.events)} log events.[/green]")
    console.print(f"Detected Severity: [{sev_color}]{payload.detected_severity}[/{sev_color}]\n")

    # 2. Call AI Client
    console.print("[bold cyan]Sending incident data to AI for analysis...[/bold cyan]")

    client = AIClient()
    try:
        result = asyncio.run(client.analyze_incident(payload))
    except Exception as e:
        console.print(f"\n[bold red]AI Analysis Error:[/bold red] {e}")
        raise typer.Exit(code=1)

    # 3. Render Rich Report
    console.print("\n")
    report_sev_color = get_severity_color(result.severity)

    # Header Panel
    console.print(
        Panel(
            f"[bold]{result.summary}[/bold]",
            title="[bold blue]AI Incident Analysis Report[/bold blue]",
            subtitle=f"Severity: [{report_sev_color}]{result.severity}[/{report_sev_color}]",
            expand=False,
        )
    )

    # Root Cause Section
    console.print("\n[bold underline yellow]Root Cause Analysis:[/bold underline yellow]")
    console.print(result.root_cause)

    # Remediation Steps Section
    console.print("\n[bold underline green]Recommended Remediation Steps:[/bold underline green]")
    for step in result.remediation_steps:
        console.print(f"  [bold cyan]{step.step_number}. {step.action}[/bold cyan]")
        console.print(f"     {step.description}")
        if step.command_example and step.command_example.strip().upper() not in ["N/A", "NONE", "NULL", ""]:
            console.print(f"     [dim]Command:[/dim] [code]{step.command_example}[/code]")

    # Preventative Measures Section (if any)
    if result.preventative_measures:
        console.print("\n[bold underline magenta]Preventative Measures:[/bold underline magenta]")
        for measure in result.preventative_measures:
            console.print(f"  * {measure}")

    # Warning Footer
    console.print(
        "\n[italic yellow]! AI-suggested commands hain, run karne se pehle verify karo.[/italic yellow]\n"
    )


if __name__ == "__main__":
    app()
