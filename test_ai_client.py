import asyncio
from incident_copilot.ingestion.parser import LogParser
from incident_copilot.ai.client import AIClient
import os

async def main():
    # 1. Read sample logs
    log_file_path = "data/sample_logs.txt"
    if not os.path.exists(log_file_path):
        print(f"Error: {log_file_path} not found.")
        return

    with open(log_file_path, "r") as f:
        raw_logs = f.read()

    # 2. Parse logs
    print("--- Parsing Logs ---")
    payload = LogParser.parse_text(raw_logs)
    print(f"Detected Severity: {payload.detected_severity}")

    # 3. Analyze with AI
    print("\n--- Sending to AI for Analysis ---")
    client = AIClient()
    try:
        result = await client.analyze_incident(payload)

        print("\n=== AI Analysis Result ===")
        print(f"Summary: {result.summary}")
        print(f"Root Cause: {result.root_cause}")
        print(f"Severity: {result.severity}")
        print("\nRemediation Steps:")
        for step in result.remediation_steps:
            print(f"{step.step_number}. {step.action} - {step.description}")
            if step.command_example:
                print(f"   Command: {step.command_example}")
    except Exception as e:
        print(f"\nAI Analysis Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
