import asyncio
from incident_copilot.ingestion.parser import LogParser
from incident_copilot.ai.client import AIClient
from incident_copilot.config import settings
import os

async def run_test(mock_mode_val: bool):
    print(f"\n==============================================")
    print(f" RUNNING WITH MOCK_MODE = {mock_mode_val}")
    print(f"==============================================")

    settings.mock_mode = mock_mode_val

    log_file_path = "data/sample_logs.txt"
    if not os.path.exists(log_file_path):
        print(f"Error: {log_file_path} not found.")
        return

    with open(log_file_path, "r") as f:
        raw_logs = f.read()

    payload = LogParser.parse_text(raw_logs)
    print(f"Parsed Detected Severity: {payload.detected_severity}")

    client = AIClient()
    try:
        result = await client.analyze_incident(payload)
        print("\nAnalysis Result Received:")
        print(f"  Summary    : {result.summary}")
        print(f"  Root Cause : {result.root_cause}")
        print(f"  Severity   : {result.severity}")
        print("  Remediation Steps:")
        for step in result.remediation_steps:
            print(f"    {step.step_number}. {step.action} - {step.description}")
            if step.command_example:
                print(f"       Command: {step.command_example}")
    except Exception as e:
        print(f"\nCaught Expected/Unexpected Error: {e}")

async def main():
    # 1. Test with MOCK_MODE = True
    await run_test(True)

    # 2. Test with MOCK_MODE = False (will attempt live API connection or show connection error)
    await run_test(False)

if __name__ == "__main__":
    asyncio.run(main())
