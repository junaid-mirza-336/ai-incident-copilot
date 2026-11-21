from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class LogEvent(BaseModel):
    """Represents a single parsed log event or alert line."""
    timestamp: Optional[str] = Field(None, description="Timestamp extracted from the log, if available")
    level: str = Field("INFO", description="Log severity level (INFO, WARN, ERROR, CRITICAL, etc.)")
    source: Optional[str] = Field(None, description="Component, service, or server name generating the log")
    message: str = Field(..., description="Raw or cleaned log message")
    raw_line: str = Field(..., description="Original raw log line")


class IncidentPayload(BaseModel):
    """Container for raw and parsed log events submitted for analysis."""
    raw_input: str = Field(..., description="Original raw input text or logs")
    events: List[LogEvent] = Field(default_factory=list, description="Parsed individual log events")
    detected_severity: str = Field("UNKNOWN", description="Overall detected severity of the incident")


class RemediationStep(BaseModel):
    """A single suggested remediation or troubleshooting step."""
    step_number: int
    action: str
    description: str
    command_example: Optional[str] = None


class AnalysisResult(BaseModel):
    """Structured AI analysis output for an incident."""
    summary: str = Field(..., description="Brief summary of the incident")
    root_cause: str = Field(..., description="Likely root cause of the problem")
    severity: str = Field(..., description="Assessed severity level")
    remediation_steps: List[RemediationStep] = Field(default_factory=list, description="Step-by-step fix guide")
    preventative_measures: List[str] = Field(default_factory=list, description="Tips to prevent recurrence")
