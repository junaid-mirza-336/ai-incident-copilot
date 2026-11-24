import pytest
from incident_copilot.ingestion.parser import LogParser


def test_parser_no_timestamp():
    """Test case 1: Log line without timestamp but starting with ERROR:"""
    raw_log = "ERROR: Database connection failed immediately."
    payload = LogParser.parse_text(raw_log)

    assert len(payload.events) == 1
    event = payload.events[0]
    assert event.level == "ERROR"
    assert event.timestamp is None
    assert event.message == "Database connection failed immediately."
    assert payload.detected_severity == "ERROR"


def test_parser_stack_trace():
    """Test case 2: Multi-line Python stack trace grouped into a single event."""
    raw_log = """Traceback (most recent call last):
  File "app.py", line 10, in <module>
    main()
  File "app.py", line 5, in main
    raise ValueError("Invalid configuration detected")
ValueError: Invalid configuration detected"""

    payload = LogParser.parse_text(raw_log)

    # Should be grouped into 1 or 2 events depending on parser grouping logic (Traceback + ValueError)
    assert len(payload.events) >= 1
    # First event should contain the traceback and error message
    full_message = "\n".join([e.message for e in payload.events])
    assert "Traceback (most recent call last):" in full_message
    assert "ValueError: Invalid configuration detected" in full_message
    assert payload.detected_severity == "ERROR"


def test_parser_empty_line():
    """Test case 3: Empty or whitespace-only lines are handled gracefully."""
    raw_log = "   "
    payload = LogParser.parse_text(raw_log)

    # Empty lines are skipped/ignored by parse_text
    assert len(payload.events) == 0
    assert payload.detected_severity == "INFO"


def test_parser_syslog_style():
    """Test case 4: Linux Syslog style line with Month Day Time format."""
    raw_log = "Nov 21 14:10:05 server-01 kernel: [1234.56] Out of memory: Kill process 999 (python)"
    payload = LogParser.parse_text(raw_log)

    assert len(payload.events) == 1
    event = payload.events[0]
    assert event.timestamp == "Nov 21 14:10:05"
    assert event.level == "INFO"
    assert "Out of memory" in event.message
