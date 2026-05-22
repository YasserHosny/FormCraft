# Tasks: AI Smart Control Suggestion

**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Format: `[ID] [Priority] [Story] Description`

## Phase 1: Setup

- [ ] **T05-001** P1 Setup — Install dependencies: `boto3`, `cachetools`, add to requirements.txt
- [ ] **T05-002** P1 Setup — Add env vars to config.py: `AWS_REGION`, `AWS_BEDROCK_MODEL_ID`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

## Phase 2: Backend — Schemas & Provider

- [ ] **T05-010** P1 S1 — Create `app/schemas/ai.py` — SuggestionRequest, SuggestionResponse, ValidationSchema, FormattingSchema Pydantic models with Literal types for controlType and direction
- [ ] **T05-011** P1 S1 — Create `app/services/ai/provider.py` — Abstract `LLMProvider` class with `classify_field()` method
- [ ] **T05-012** P1 S1 — Create `app/services/ai/bedrock.py` — `BedrockProvider` implementation: boto3 bedrock-runtime client, invoke_model with system prompt, parse JSON response, 5s timeout
- [ ] **T05-013** P1 S1 — Create `app/services/ai/prompts.py` — System prompt constant (exact text from spec)

## Phase 3: Backend — Suggestion Pipeline

- [ ] **T05-020** P1 S1 — Create `app/services/ai/cache.py` — TTLCache wrapper (max 1000 entries, 5min TTL), key = `{label}:{language}:{country}`
- [ ] **T05-021** P1 S4 — Create `app/services/ai/suggestion.py` — Orchestrator: cache check → validator registry check → LLM call → Pydantic validation → cache store → return
- [ ] **T05-022** P1 S1 — Implement fallback logic: timeout → `{ controlType: "text", confidence: 0.0 }`, invalid response → `{ controlType: "text", confidence: 0.5 }`
- [ ] **T05-023** P1 S1 — Integrate audit logging: log request, response, and accept/dismiss events via AuditLogger

## Phase 4: Backend — API Route

- [ ] **T05-030** P1 S1 — Create `app/api/routes/ai.py` — POST /api/ai/suggest-control, requires Designer or Admin role
- [ ] **T05-031** P2 S3 — Add batch endpoint: POST /api/ai/suggest-control/batch — accepts array of labels, max 20, returns array of suggestions

## Phase 5: Backend — Tests

- [ ] **T05-040** P1 S1 — Write `tests/unit/test_suggestion_schema.py` — Valid/invalid SuggestionResponse parsing, all 16 controlTypes accepted, unknown types rejected
- [ ] **T05-041** P1 S1 — Write `tests/unit/test_fallback.py` — Timeout produces fallback, malformed JSON produces fallback, invalid controlType produces fallback
- [ ] **T05-042** P1 S4 — Write `tests/unit/test_deterministic_override.py` — Label "رقم الهوية الوطنية" + country "EG" → national_id with confidence 1.0, IBAN labels → iban override
- [ ] **T05-043** P1 S1 — Write `tests/unit/test_cache.py` — Cache hit returns same response, TTL expiry triggers new call, LRU eviction works
- [ ] **T05-044** P1 S1-S4 — Write `tests/integration/test_ai_endpoint.py` — End-to-end with mocked LLM provider, verify response schema, audit log entries

## Phase 6: Frontend — Suggestion UI

- [ ] **T05-050** P1 S1 — Create `src/app/features/designer/services/ai-suggestion.service.ts` — HTTP call to POST /api/ai/suggest-control, RxJS debounceTime(300), error handling with fallback
- [ ] **T05-051** P1 S1 — Create `ai-suggestion-chip/ai-suggestion-chip.component.ts` — Display suggestion: controlType badge, confidence percentage, Accept button, Dismiss button
- [ ] **T05-052** P1 S1 — Integrate with property panel: trigger suggestion on label_ar or label_en valueChanges, show chip below label field
- [ ] **T05-053** P1 S1 — Implement Accept: update element's controlType, validation, formatting, direction from suggestion, log accept event
- [ ] **T05-054** P1 S1 — Implement Dismiss: hide chip, log dismiss event
- [ ] **T05-055** P1 S2 — Trigger suggestion on new element creation when label is first set

## Phase 7: Frontend — Tests

- [ ] **T05-060** P1 — Write unit tests: ai-suggestion.service.spec.ts — debounce, HTTP call, error handling
- [ ] **T05-061** P1 — Write unit tests: ai-suggestion-chip.component.spec.ts — accept/dismiss actions, display values

## Dependencies & Execution Order

```
T05-001 → T05-002 (setup)
T05-010 → T05-011 → T05-012 (schemas → provider)
T05-013 (parallel with provider)
T05-020 → T05-021 → T05-022 → T05-023 (pipeline chain)
T05-021 depends on spec 07 (ValidatorRegistry) — can stub initially
T05-030 (route, after pipeline)
T05-040-044 (tests, after implementation)
T05-050 → T05-051 → T05-052 → T05-053, T05-054 (frontend chain)
```

## Parallel Opportunities

- Schemas (T05-010) and prompts (T05-013) in parallel
- Backend tests (T05-040 through T05-044) all in parallel
- Frontend service (T05-050) and backend route (T05-030) in parallel (different repos)
