import json
import httpx
from typing import Optional
from incident_copilot.config import settings
from incident_copilot.models.incident import IncidentPayload, AnalysisResult


class AIClient:
    """Client for interacting with FreeLLMAPI (OpenAI-compatible) for incident analysis."""

    def __init__(self):
        self.base_url = settings.freellmapi_base_url.rstrip("/")
        self.api_key = settings.freellmapi_api_key
        self.model = settings.default_model
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

    async def analyze_incident(self, payload: IncidentPayload) -> AnalysisResult:
        """
        Sends the parsed incident data to the LLM and returns a structured AnalysisResult.
        """
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
                raise Exception("Authentication failed: Invalid FREELLMAPI_API_KEY.")
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
            raise Exception(f"Could not connect to FreeLLMAPI at {self.base_url}. Is the service running?")
        except httpx.TimeoutException:
            raise Exception("The request to FreeLLMAPI timed out.")
        except Exception as e:
            raise Exception(f"An unexpected error occurred: {str(e)}")
