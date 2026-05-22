# Implementation Plan: AI Smart Control Suggestion

**Branch**: `05-ai-suggestion` | **Date**: 2026-02-21 | **Spec**: [spec.md](./spec.md)

## Summary

Implement the `POST /api/ai/suggest-control` endpoint with AWS Bedrock LLM integration (behind an abstract provider interface), Pydantic response validation with fallback, deterministic validator override, in-memory caching, and frontend suggestion chip UI in the Design Studio property panel.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, boto3 (AWS Bedrock), Pydantic v2, cachetools (backend), Zod, RxJS (frontend)
**Storage**: In-memory LRU cache (backend), Supabase audit_logs table
**Testing**: pytest + moto (AWS mock) for backend, Jasmine/Karma for frontend
**Target Platform**: Web
**Constraints**: LLM response < 5s, fallback to "text" on timeout/error

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| III. AI Suggest Only | ✅ Pass | Never auto-applied; accept/dismiss UI required |
| IV. Deterministic Over Probabilistic | ✅ Pass | ValidatorRegistry checked before LLM |
| V. Test-First | ✅ Pass | Schema validation, fallback, and override all tested |
| VIII. Security | ✅ Pass | All requests/responses logged to audit trail |

## Project Structure

### Backend (formcraft-backend)

```text
app/
├── api/routes/
│   └── ai.py                       # POST /api/ai/suggest-control
├── services/
│   └── ai/
│       ├── __init__.py
│       ├── provider.py              # Abstract LLMProvider interface
│       ├── bedrock.py               # AWS Bedrock implementation
│       ├── suggestion.py            # Orchestrator: cache → validators → LLM → validate → respond
│       ├── cache.py                 # LRU cache wrapper (cachetools TTLCache)
│       └── prompts.py              # System prompt constant
├── schemas/
│   └── ai.py                       # SuggestionRequest, SuggestionResponse, ValidationSchema, FormattingSchema
└── core/
    └── audit.py                     # log_ai_suggestion() helper

tests/
├── unit/
│   ├── test_suggestion_schema.py    # Pydantic validation of LLM responses
│   ├── test_fallback.py             # Invalid/timeout responses produce fallback
│   └── test_deterministic_override.py # Validator overrides AI for known fields
└── integration/
    └── test_ai_endpoint.py          # End-to-end with mocked LLM
```

### Frontend (formcraft-frontend)

```text
src/app/features/designer/
├── property-panel/
│   └── ai-suggestion-chip/
│       ├── ai-suggestion-chip.component.ts    # Suggestion display + accept/dismiss
│       ├── ai-suggestion-chip.component.html
│       └── ai-suggestion-chip.component.scss
└── services/
    └── ai-suggestion.service.ts               # HTTP call with debounce, caching, error handling
```

### LLM Provider Interface

```python
# provider.py
from abc import ABC, abstractmethod
from app.schemas.ai import SuggestionRequest, SuggestionResponse

class LLMProvider(ABC):
    @abstractmethod
    async def classify_field(self, request: SuggestionRequest) -> dict:
        """Send label + context to LLM, return raw JSON dict."""
        ...

# bedrock.py
class BedrockProvider(LLMProvider):
    def __init__(self, model_id: str, region: str):
        self.client = boto3.client("bedrock-runtime", region_name=region)
        self.model_id = model_id

    async def classify_field(self, request: SuggestionRequest) -> dict:
        # Build messages with system prompt + user message
        # Call invoke_model with 5s timeout
        # Parse JSON response
        ...
```

### Suggestion Pipeline Flow

```
Request arrives at POST /api/ai/suggest-control
  │
  ├─ 1. Check cache (label:language:country key)
  │     └─ Hit → return cached response (skip steps 2-4)
  │
  ├─ 2. Check ValidatorRegistry (from spec 07)
  │     └─ Match → return deterministic response (confidence: 1.0)
  │
  ├─ 3. Call LLM via provider.classify_field()
  │     └─ Timeout (5s) → return fallback { controlType: "text", confidence: 0.0 }
  │     └─ Success → raw JSON dict
  │
  ├─ 4. Validate with Pydantic SuggestionResponse
  │     └─ Invalid → return fallback { controlType: "text", confidence: 0.5 }
  │     └─ Valid → cache + return
  │
  └─ 5. Log to audit trail (async, non-blocking)
```

## Research Notes

- **AWS Bedrock**: Using `boto3` `bedrock-runtime` client with `invoke_model`. Model ID configurable via env var (e.g., `anthropic.claude-3-haiku-20240307-v1:0`). Supports JSON mode.
- **Provider abstraction**: If Bedrock is unavailable or user switches to OpenAI, only a new `OpenAIProvider` class is needed. No other code changes.
- **cachetools TTLCache**: In-memory, thread-safe, supports TTL and max size. No Redis dependency in Phase 1.
- **Debounce**: Frontend uses RxJS `debounceTime(300)` on the label input `valueChanges` observable before calling the suggestion service.

## Complexity Tracking

No constitution violations.
