# AI Incident Copilot

AI-powered assistant that helps analyze and respond to IT/network incidents faster by parsing server logs, determining root causes, and suggesting remediation steps.

## Features
- **Provider-Independent (OpenAI-Compatible):** Works with any OpenAI-compatible LLM backend (e.g., FreeLLMAPI, OpenAI, OpenRouter, LM Studio, Ollama).
- **Mock Mode:** Test and develop without network calls using `MOCK_MODE=true`.
- **Robust Log Parser:** Handles standard timestamps, syslog formats, and multi-line Python stack traces.
- **Structured Pydantic Models & CLI:** Clean architecture with typed models and rich terminal output.

---

## Configuration Examples

Create a `.env` file in the root directory (you can copy `.env.example`).

### Example 1: FreeLLMAPI / Local OpenAI-Compatible Server
```env
LLM_API_KEY=your_freellmapi_key_here
LLM_BASE_URL=http://127.0.0.1:31415/v1
LLM_MODEL=auto
MOCK_MODE=false
```

### Example 2: OpenAI API
```env
LLM_API_KEY=sk-proj-your_openai_api_key_here
LLM_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o-mini
MOCK_MODE=false
```

### Example 3: Mock Mode (Offline / Testing)
```env
LLM_API_KEY=dummy
LLM_BASE_URL=http://localhost:31415/v1
LLM_MODEL=auto
MOCK_MODE=true
```
