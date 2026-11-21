import sys
from incident_copilot.ingestion.parser import LogParser

# Test cases defined by the user
edge_cases = {
    "No Timestamp": "ERROR: Database connection failed immediately.",
    "Python Stack Trace": """Traceback (most recent call last):
  File "app.py", line 10, in <module>
    main()
  File "app.py", line 5, in main
    raise ValueError("Invalid configuration detected")
ValueError: Invalid configuration detected""",
    "Empty Line": "   ",
    "Linux Syslog Style": "Nov 21 14:10:05 server-01 kernel: [1234.56] Out of memory: Kill process 999 (python)"
}

if __name__ == "__main__":
    print("=== Testing LogParser Edge Cases ===\n")

    for case_name, raw_text in edge_cases.items():
        print(f"--- Case: {case_name} ---")
        print(f"Input:\n{raw_text}")

        # Using parse_text for multi-line support
        payload = LogParser.parse_text(raw_text)

        for i, event in enumerate(payload.events, 1):
            print(f"Result [{i}]:")
            print(f"  Level: {event.level}")
            print(f"  Time:  {event.timestamp or 'None'}")
            print(f"  Src:   {event.source or 'None'}")
            print(f"  Msg:   {event.message}")
        print("\n")

    print("=== Edge Case Test Completed ===")
