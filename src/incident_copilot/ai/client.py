import json
import httpx
from typing import Optional
from incident_copilot.config import settings
from incident_copilot.models.incident import IncidentPayload, AnalysisResult, RemediationStep


class AIClient:
    """Client for interacting with any OpenAI-compatible LLM provider or Mock mode for incident analysis."""

    def __init__(self):
        self.base_url = settings.llm_base_url.rstrip("/")
        self.api_key = settings.llm_api_key
        self.model = settings.llm_model
        self.mock_mode = settings.mock_mode
        self.timeout = 30.0  # Seconds

    def _get_system_prompt(self) -> str:
        """Returns the system prompt for incident analysis."""
        return (
            "You are an expert IT Incident Response Engineer. Your task is to analyze the provided server logs "
            "and determine the root cause, severity, and provide clear remediation steps.\n\n"
            "CRITICAL: You must respond ONLY with a valid JSON object. Do not include any conversational text "
            "before or after the JSON.\n\n"
            "The JSON structure must match this exactly:\n"
            "{\n"
            "  \"summary\": \"Brief summary of the incident\",\n"
            "  \"root_cause\": \"Detailed explanation of why this happened\",\n"
            "  \"severity\": \"INFO | WARN | ERROR | CRITICAL\",\n"
            "  \"remediation_steps\": [\n"
            "    {\n"
            "      \"step_number\": 1,\n"
            "      \"action\": \"Action title\",\n"
            "      \"description\": \"Detailed explanation\",\n"
            "      \"command_example\": \"Optional command to run\"\n"
            "    }\n"
            "  ],\n"
            "  \"preventative_measures\": [\"Tip 1\", \"Tip 2\"]\n"
            "}"
        )

    def _get_mock_result(self, payload: IncidentPayload) -> AnalysisResult:
        """Returns a realistic mock AnalysisResult without making network calls."""
        return AnalysisResult(
            summary=f"[MOCK] Incident analyzed with severity {payload.detected_severity}.",
            root_cause="[MOCK] Simulated root cause: Connection timeout or resource exhaustion detected in logs.",
            severity=payload.detected_severity,
            remediation_steps=[
                RemediationStep(
                    step_number=1,
                    action="Check Service Status",
                    description="Verify if the affected service container or process is running.",
                    command_example="systemctl status incident-service"
                ),
                RemediationStep(
                    step_number=2,
                    action="Inspect Logs",
                    description="Check recent application error logs for stack traces.",
                    command_example="tail -n 100 /var/log/app.log"
                )
            ],
            preventative_measures=[
                "Implement automatic service health checks and restarts.",
                "Set up alerts for connection pool thresholds."
            ]
        )

    async def analyze_incident(self, payload: IncidentPayload) -> AnalysisResult:
        """
        Sends the parsed incident data to the LLM (or returns mock data if mock_mode is True)
        and returns a structured AnalysisResult.
        """
        if self.mock_mode:
            return self._get_mock_result(payload)

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # Format logs for the prompt
        log_snippet = "\n".join([f"[{e.level}] {e.message}" for e in payload.events])
        user_message = f"Please analyze these logs:\n\n{log_snippet}"

        request_body = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": user_message}
            ],
            "response_format": {"type": "json_object"}
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=headers,
                    json=request_body
                )

            if response.status_code == 401:
                raise Exception("Authentication failed: Invalid LLM_API_KEY.")
            elif response.status_code != 200:
                raise Exception(f"API Error ({response.status_code}): {response.text}")

            data = response.json()
            content = data["choices"][0]["message"]["content"]

            # Parse JSON content from LLM
            try:
                analysis_dict = json.loads(content)
                return AnalysisResult(**analysis_dict)
            except json.JSONDecodeError:
                raise Exception("The AI returned invalid JSON. Please try again.")
            except Exception as e:
                raise Exception(f"Error mapping AI response to model: {str(e)}")

        except httpx.ConnectError:
            raise Exception(f"Could not connect to LLM provider at {self.base_url}. Is the service running or URL correct?")
        except httpx.TimeoutException:
            raise Exception("The request to the LLM provider timed out.")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {str(e)}")
