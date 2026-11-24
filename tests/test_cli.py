import pytest
from pathlib import Path
from typer.testing import CliRunner

from incident_copilot.interfaces.cli.main import app
from incident_copilot.config import settings

runner = CliRunner()


def test_cli_file_not_found():
    """Test CLI behavior when the provided log file does not exist."""
    result = runner.invoke(app, ["non_existent_file.txt"])
    assert result.exit_code != 0
    assert "Log file not found" in result.output


def test_cli_success_mock_mode(tmp_path: Path):
    """Test CLI successful analysis using MOCK_MODE = True and a temporary log file."""
    settings.mock_mode = True

    # Create a temporary log file
    log_file = tmp_path / "test_incident.log"
    log_file.write_text("2026-11-23 18:00:00 [ERROR] test-service: Database timeout error occurred.")

    result = runner.invoke(app, [str(log_file)])

    assert result.exit_code == 0
    assert "Parsed 1 log events" in result.output
    assert "Detected Severity: ERROR" in result.output
    assert "AI Incident Analysis Report" in result.output
    assert "AI-suggested commands hain" in result.output
