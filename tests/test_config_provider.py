import os
from incident_copilot.config import settings

print(f"Current Settings:")
print(f"  LLM_BASE_URL : {settings.llm_base_url}")
print(f"  LLM_MODEL    : {settings.llm_model}")
print(f"  MOCK_MODE    : {settings.mock_mode}")
print(f"  API Key set? : {bool(settings.llm_api_key and settings.llm_api_key != 'sk-placeholder')}")
