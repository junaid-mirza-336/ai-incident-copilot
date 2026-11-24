import pytest
from pathlib import Path
from typer.testing import CliRunner

from incident_copilot.interfaces.cli.main import app
from incident_copilot.config import settings
from incident_copilot.models.incident import AnalysisResult, RemediationStep, IncidentPayload

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


def test_cli_skip_na_command(monkeypatch, tmp_path: Path):
    """Test that commands containing 'N/A', 'None', or empty strings are omitted from CLI display."""
    log_file = tmp_path / "test_na_command.log"
    log_file.write_text("2026-11-23 18:00:00 [INFO] test: Connection reset")

    mock_result = AnalysisResult(
        summary="Test summary",
        root_cause="Test root cause",
        severity="INFO",
        remediation_steps=[
            RemediationStep(step_number=1, action="Step With Valid Command", description="Desc 1", command_example="ping 127.0.0.1"),
            RemediationStep(step_number=2, action="Step With NA Command", description="Desc 2", command_example="N/A"),
            RemediationStep(step_number=3, action="Step With Empty Command", description="Desc 3", command_example="  ")
        ]
    )

    async def mock_analyze(self, payload: IncidentPayload):
        return mock_result

    from incident_copilot.ai.client import AIClient
    monkeypatch.setattr(AIClient, "analyze_incident", mock_analyze)

    result = runner.invoke(app, [str(log_file)])
    assert result.exit_code == 0
    assert "ping 127.0.0.1" in result.output
    assert "Desc 2" in result.output
    assert "Desc 3" in result.output
    # Count occurrences of "Command:" - should only be 1 (for step 1)
    assert result.output.count("Command:") == 1
