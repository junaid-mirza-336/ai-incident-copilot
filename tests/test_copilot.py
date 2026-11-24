import pytest
from incident_copilot.ingestion.parser import LogParser
from incident_copilot.ai.client import AIClient
from incident_copilot.config import settings

def test_parser_basic():
    log_line = "2026-11-23 12:00:00 [ERROR] db-service: Connection timeout"
    event = LogParser.parse_line(log_line)
    assert event.level == "ERROR"
    assert event.source == "db-service"
    assert event.timestamp == "2026-11-23 12:00:00"

@pytest.mark.asyncio
async def test_ai_client_mock_mode():
    settings.mock_mode = True
    client = AIClient()
    payload = LogParser.parse_text("2026-11-23 12:00:00 [CRITICAL] test: Out of memory")
    result = await client.analyze_incident(payload)
    assert result.severity == "CRITICAL"
    assert len(result.remediation_steps) > 0
