import sys
from incident_copilot.ingestion.parser import LogParser

sample_logs = """2026-11-21 14:10:05 [INFO] auth-service: User authentication successful for user_id=4821
2026-11-21 14:11:32 [WARN] database-pool: Connection pool reached 85% capacity (42/50 connections active)
2026-11-21 14:12:00 [ERROR] payment-gateway: Timeout connecting to upstream provider https://api.paygateway.com/v1/charge
2026-11-21 14:12:01 [CRITICAL] payment-gateway: Transaction processing halted due to upstream failure. System entering degraded mode."""

if __name__ == "__main__":
    print("=== Testing LogParser with Sample Logs ===")
    payload = LogParser.parse_text(sample_logs)

    print(f"\nDetected Overall Severity: {payload.detected_severity}")
    print(f"Total Log Events Parsed: {len(payload.events)}\n")

    for i, event in enumerate(payload.events, 1):
        print(f"[{i}] Level: {event.level:<8} | Time: {event.timestamp or 'N/A'} | Source: {event.source or 'N/A'}")
        print(f"    Message: {event.message}")
    print("\nParser test completed successfully!")
