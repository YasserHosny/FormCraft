# Feature Specification: Performance Optimization & Production Hardening

**Feature Branch**: `09-perf-hardening`
**Created**: 2026-02-21
**Status**: Draft
**Input**: FormCraft PRD Phase 8 & 9 – Performance + Production Hardening

## User Scenarios & Testing

### User Story 1 - AI Suggestion Caching (Priority: P1)

Frequently used field labels return cached AI suggestions instead of making redundant LLM calls. The cache key is `{label}:{language}:{country}`. Cache TTL is 5 minutes. Cache is invalidated when the system prompt or LLM model is updated.

**Why this priority**: LLM calls are expensive and slow. Caching reduces cost and improves UX.

**Independent Test**: Can be tested by sending the same label twice and verifying the second call returns instantly from cache.

**Acceptance Scenarios**:

1. **Given** label "رقم الهوية" was suggested 30 seconds ago, **When** the same label is sent again, **Then** the response returns from cache within 10ms.
2. **Given** a cached entry is 6 minutes old, **When** the same label is sent, **Then** the cache miss triggers a new LLM call.
3. **Given** the cache is full (1000 entries), **When** a new label is sent, **Then** the oldest entry is evicted (LRU).

---

### User Story 2 - Label Change Debounce (Priority: P1)

When the Designer types in the label field, the frontend debounces changes by 300ms before calling the AI suggestion endpoint. This prevents rapid-fire API calls during typing.

**Why this priority**: Without debounce, every keystroke triggers an LLM call, wasting resources.

**Independent Test**: Can be tested by typing 10 characters rapidly and verifying only 1 API call is made (after 300ms of idle).

**Acceptance Scenarios**:

1. **Given** the Designer types "ر" then "رق" then "رقم" within 300ms, **When** 300ms passes after the last keystroke, **Then** one API call is made with label "رقم".
2. **Given** the Designer types "الاسم" and waits 500ms, then adds " الكامل", **When** 300ms passes after the second edit, **Then** two API calls total are made.

---

### User Story 3 - LLM Timeout Fallback (Priority: P1)

If the LLM does not respond within 5 seconds, the system returns a fallback suggestion with controlType "text" and confidence 0.0. The user sees a warning indicator that the AI was unable to process the request.

**Why this priority**: The UI must never hang waiting for AI. Graceful degradation is required.

**Independent Test**: Can be tested by simulating LLM timeout and verifying fallback response within 5.1 seconds.

**Acceptance Scenarios**:

1. **Given** the LLM takes 6 seconds to respond, **When** the 5-second timeout is reached, **Then** the endpoint returns `{ controlType: "text", confidence: 0.0 }` and the UI shows a warning icon.
2. **Given** the LLM returns in 2 seconds, **When** the response is received, **Then** the normal suggestion is displayed (no fallback).

---

### User Story 4 - Production Deployment on Bunny (Priority: P1)

The application deploys to Bunny Magic Containers with separate containers for frontend and backend. Environment-specific configuration (dev/staging/prod) is managed via environment variables. Health check endpoints are available.

**Why this priority**: Without production deployment, the application is not accessible at formcraft.iron-sys.com.

**Independent Test**: Can be tested by deploying to Bunny and hitting health check endpoints.

**Acceptance Scenarios**:

1. **Given** the frontend Docker image is built, **When** deployed to Bunny, **Then** the Angular app is served at `formcraft.iron-sys.com`.
2. **Given** the backend Docker image is built, **When** deployed to Bunny, **Then** the API is accessible at `formcraft.iron-sys.com/api/`.
3. **Given** the backend is running, **When** `GET /api/health` is called, **Then** it returns `{ status: "ok", version: "1.0.0" }` with 200 status.
4. **Given** the backend cannot connect to Supabase, **When** `GET /api/health` is called, **Then** it returns `{ status: "degraded", checks: { supabase: "unreachable" } }` with 503 status.

---

### User Story 5 - Error Boundaries and Graceful Degradation (Priority: P2)

Frontend errors are caught by Angular error boundaries. API errors return structured JSON error responses. The canvas editor recovers from rendering errors without losing user data.

**Why this priority**: Production stability requires error handling, but can be layered on after core features.

**Independent Test**: Can be tested by injecting errors and verifying recovery behavior.

**Acceptance Scenarios**:

1. **Given** a canvas rendering error occurs, **When** the error boundary catches it, **Then** the user sees "An error occurred in the editor. Your changes are saved." and the canvas reloads.
2. **Given** the API returns a 500 error, **When** the frontend receives it, **Then** a toast notification shows "Server error. Please try again." with the request ID.
3. **Given** auto-save fails due to network error, **When** connectivity is restored, **Then** the pending changes are retried automatically.

---

### User Story 6 - SSL/TLS and Domain Configuration (Priority: P1)

The domain `formcraft.iron-sys.com` is configured with SSL/TLS. All HTTP traffic is redirected to HTTPS. HSTS headers are set.

**Why this priority**: SSL is a hard requirement for production web applications.

**Independent Test**: Can be tested by accessing `http://formcraft.iron-sys.com` and verifying redirect to HTTPS.

**Acceptance Scenarios**:

1. **Given** a user navigates to `http://formcraft.iron-sys.com`, **When** the request is processed, **Then** they are redirected to `https://formcraft.iron-sys.com` with a 301 status.
2. **Given** the site is accessed via HTTPS, **When** headers are inspected, **Then** `Strict-Transport-Security: max-age=31536000; includeSubDomains` is present.

---

### Edge Cases

- What happens when Bunny container runs out of memory? → Container restarts automatically; health check detects and reports.
- What happens when environment variables are missing? → App fails to start with a clear error message listing missing required variables.
- What happens with zero-downtime deployment? → Bunny rolling deployment (if supported) or brief downtime with maintenance page.

## Requirements

### Functional Requirements

- **FR-001**: Backend MUST cache AI suggestion responses in-memory (LRU cache, max 1000 entries, 5-minute TTL).
- **FR-002**: Frontend MUST debounce label changes by 300ms before calling AI suggestion endpoint.
- **FR-003**: Backend MUST timeout LLM calls after 5 seconds and return fallback suggestion.
- **FR-004**: Backend MUST expose `GET /api/health` endpoint with service dependency checks.
- **FR-005**: Frontend and backend MUST each have a `Dockerfile` for containerized deployment.
- **FR-006**: Each repo MUST have a `bunny.yaml` for Bunny Magic Container deployment configuration.
- **FR-007**: Environment-specific config MUST be managed via environment variables (no hardcoded secrets).
- **FR-008**: Required environment variables: `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_KEY`, `AWS_REGION`, `AWS_BEDROCK_MODEL_ID`, `CORS_ORIGINS`, `LOG_LEVEL`.
- **FR-009**: Application MUST fail fast on startup if required environment variables are missing.
- **FR-010**: Frontend MUST implement Angular `ErrorHandler` for global error catching.
- **FR-011**: API errors MUST return structured JSON: `{ error: string, detail: string, request_id: string }`.
- **FR-012**: Auto-save MUST retry failed saves up to 3 times with exponential backoff.
- **FR-013**: SSL/TLS MUST be configured on the domain with HSTS headers.
- **FR-014**: HTTP to HTTPS redirect MUST be enforced.
- **FR-015**: Frontend build MUST be optimized: tree-shaking, lazy loading of feature modules, AOT compilation.
- **FR-016**: Backend MUST use `uvicorn` with multiple workers (configurable, default 4).

### Key Entities

- **HealthCheckResponse**: status (ok/degraded/down), version, checks (map of dependency → status).
- **CacheEntry**: key (label:language:country), value (SuggestionResponse), created_at, ttl.
- **ErrorResponse**: error (string), detail (string), request_id (UUID).

## Success Criteria

### Measurable Outcomes

- **SC-001**: Cached AI suggestions return within 10ms (p99).
- **SC-002**: LLM timeout fallback triggers within 5.1 seconds (p99).
- **SC-003**: Health check endpoint responds within 100ms.
- **SC-004**: Frontend initial load (gzipped) is under 500KB.
- **SC-005**: Application starts within 10 seconds in production.
- **SC-006**: Zero unhandled exceptions in production (all caught by error boundaries).
- **SC-007**: SSL Labs score of A or higher for formcraft.iron-sys.com.
