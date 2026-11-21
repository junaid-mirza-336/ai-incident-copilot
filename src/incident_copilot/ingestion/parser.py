import re
from typing import List
from incident_copilot.models.incident import LogEvent, IncidentPayload


class LogParser:
    """Parses raw log text or files into structured LogEvents and IncidentPayload."""

    # Common regex pattern for standard log formats
    # Updated to support YYYY-MM-DD and Syslog (Month Day Time) formats
    TIMESTAMP_PATTERN = r'(?P<timestamp>\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}:\d{2}(?:\.\d+)?|[A-Z][a-z]{2}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})'

    LOG_PATTERN = re.compile(
        f'^{TIMESTAMP_PATTERN}?\\s*' +
        r'(?:\[(?P<level>[A-Z]+)\]|(?P<level_direct>ERROR|WARN|INFO|CRITICAL|FATAL|DEBUG):)?\s*' +
        r'(?:(?P<source>[\w\-./]+):\s*)?(?P<message>.*)$'
    )

    @classmethod
    def parse_line(cls, line: str) -> LogEvent:
        """Parses a single log line into a LogEvent object."""
        line_stripped = line.strip()
        if not line_stripped:
            return LogEvent(level="INFO", message="", raw_line=line)

        match = cls.LOG_PATTERN.match(line_stripped)

        # Determine initial data from regex
        data = match.groupdict() if match else {}

        level_str = data.get("level") or data.get("level_direct")
        timestamp = data.get("timestamp")
        source = data.get("source")
        message = data.get("message") or line_stripped

        # Severity ranking for keywords
        upper_line = line_stripped.upper()
        detected_level = "INFO"

        if level_str:
            detected_level = level_str.upper()
        else:
            # Keyword detection if no explicit level found in structured format
            if any(k in upper_line for k in ["CRITICAL", "FATAL", "CRIT"]):
                detected_level = "CRITICAL"
            elif "ERROR" in upper_line or "ERR" in upper_line or "FAIL" in upper_line:
                detected_level = "ERROR"
            elif "WARN" in upper_line or "WARNING" in upper_line:
                detected_level = "WARN"

        # Special case: if source was caught as a keyword level, fix it
        if source and source.upper() in ["ERROR", "WARN", "INFO", "CRITICAL", "FATAL"]:
            if detected_level == "INFO":
                detected_level = source.upper()
            source = None

        # Clean up FATAL -> CRITICAL
        if detected_level == "FATAL":
            detected_level = "CRITICAL"

        return LogEvent(
            timestamp=timestamp,
            level=detected_level,
            source=source,
            message=message,
            raw_line=line
        )

    @classmethod
    def parse_text(cls, raw_text: str) -> IncidentPayload:
        """Parses multi-line raw text or log content into an IncidentPayload."""
        lines = raw_text.splitlines()
        events: List[LogEvent] = []

        current_event: Optional[LogEvent] = None

        # Keywords that indicate the start of a new log entry
        # If a line doesn't have a timestamp and doesn't start with these, it might be a continuation
        new_entry_indicators = [r'^\d{4}-', r'^[A-Z][a-z]{2}\s+\d', r'^\[?[A-Z]+\]?:?', r'^Traceback']

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                if current_event:
                    events.append(current_event)
                    current_event = None
                continue

            # Check if this line looks like a new entry
            is_new_entry = any(re.match(pattern, line_stripped) for pattern in new_entry_indicators)

            # Special check for common stack trace markers and continuation
            is_stack_continuation = (
                line.startswith('  ') or
                line.startswith('\t') or
                line_stripped.startswith('at ') or
                (current_event and current_event.message.startswith('Traceback'))
            )

            if (is_new_entry or not current_event) and not is_stack_continuation:
                if current_event:
                    events.append(current_event)
                current_event = cls.parse_line(line)
            else:
                # Append to current event (Stack trace or multi-line grouping)
                if current_event:
                    current_event.message += "\n" + line_stripped
                    current_event.raw_line += "\n" + line

                    # Re-check level if message changed
                    if current_event.level == "INFO":
                        temp_event = cls.parse_line(line)
                        if temp_event.level != "INFO":
                            current_event.level = temp_event.level
                else:
                    current_event = cls.parse_line(line)

        if current_event:
            events.append(current_event)

        # Calculate overall severity
        severity_rank = {"INFO": 1, "WARN": 2, "ERROR": 3, "CRITICAL": 4}
        highest_severity = "INFO"
        for event in events:
            current_rank = severity_rank.get(event.level, 1)
            highest_rank = severity_rank.get(highest_severity, 1)
            if current_rank > highest_rank:
                highest_severity = event.level

        return IncidentPayload(
            raw_input=raw_text,
            events=events,
            detected_severity=highest_severity
        )
