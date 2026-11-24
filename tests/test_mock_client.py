import asyncio
from incident_copilot.ingestion.parser import LogParser
from incident_copilot.ai.client import AIClient
from incident_copilot.config import settings

async def main():
    print(f"Testing AIClient with MOCK_MODE = {settings.mock_mode}")

    # Force mock mode for this test script if desired, or test current config
    # settings.mock_mode = True

    sample_log = "2026-11-23 16:00:00 [CRITICAL] database: Connection reset by peer during transaction."
    payload = LogParser.parse_text(sample_log)

    client = AIClient()
    # Temporarily enable mock mode for verification if no live server running
    client.mock_mode = True

    result = await client.analyze_incident(payload)
    print("\n=== Mock Analysis Result ===")
    print(f"Summary: {result.summary}")
    print(f"Root Cause: {result.root_cause}")
    print(f"Severity: {result.severity}")
    print(f"Remediation Steps Count: {len(result.remediation_steps)}")
    for step in result.remediation_steps:
        print(f"  - [{step.step_number}] {step.action}: {step.description}")

if __name__ == "__main__":
    asyncio.run(main())
