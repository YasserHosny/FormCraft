# Tasks: Security & Audit Logging

**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Format: `[ID] [Priority] [Story] Description`

## Phase 1: Audit Logger

- [ ] **T08-001** P1 S1 — Create `app/core/audit.py` — AuditLogger class with async `log_event()`, fire-and-forget via asyncio.create_task, failure silently caught
- [ ] **T08-002** P1 S1 — Create `app/schemas/audit.py` — AuditLogEntry Pydantic model, AuditLogQueryParams (date range, action, user_id, pagination)

## Phase 2: Integrate Audit Logging

- [ ] **T08-010** P1 S1 — Add audit logging to template routes: create, update, delete, publish, version (before/after metadata for updates)
- [ ] **T08-011** P1 S2 — Add audit logging to AI suggestion route: log request payload, response payload
- [ ] **T08-012** P1 S2 — Add audit logging to AI suggestion accept/dismiss events (frontend sends action to backend)
- [ ] **T08-013** P1 S3 — Add audit logging to auth events: login success, login failure, logout, role change (hook into Supabase Auth events or middleware)

## Phase 3: Supabase RLS Policies

- [ ] **T08-020** P1 S4 — Create `supabase/migrations/007_rls_templates.sql` — Admin full access, Designer own+published, Operator+Viewer published-only read
- [ ] **T08-021** P1 S4 — Create `supabase/migrations/008_rls_pages.sql` — Inherit access from parent template via JOIN
- [ ] **T08-022** P1 S4 — Create `supabase/migrations/009_rls_elements.sql` — Inherit access from parent page → template via JOIN
- [ ] **T08-023** P1 S4 — Create `supabase/migrations/010_rls_profiles.sql` — Admin full access, others read own + update own language/display_name
- [ ] **T08-024** P1 S4 — Run all RLS migrations via `supabase db push`

## Phase 4: API Security

- [ ] **T08-030** P2 S5 — Install slowapi: add to requirements.txt
- [ ] **T08-031** P2 S5 — Create `app/core/middleware/rate_limit.py` — Configure slowapi limiter, apply 30/min to AI suggestion endpoint
- [ ] **T08-032** P2 S5 — Create `app/core/middleware/security_headers.py` — Middleware adding X-Content-Type-Options, X-Frame-Options, HSTS, CSP, X-XSS-Protection
- [ ] **T08-033** P2 S5 — Configure CORS in main.py: allow `formcraft.iron-sys.com` + `localhost:4200` (dev)

## Phase 5: Admin Audit Query Endpoint

- [ ] **T08-040** P1 S1 — Create `app/api/routes/admin.py` — GET /api/admin/audit-logs (admin only), supports filter by date range, action type, user_id, resource_type, pagination

## Phase 6: Tests

- [ ] **T08-050** P1 S1 — Write `tests/unit/test_audit_logger.py` — log_event creates entry, failure doesn't raise, metadata serialization
- [ ] **T08-051** P1 S4 — Write `tests/integration/test_rls_policies.py` — Query templates/pages/elements with different role tokens, verify correct visibility
- [ ] **T08-052** P2 S5 — Write `tests/integration/test_rate_limiting.py` — Exceed 30 requests/min, verify 429 response
- [ ] **T08-053** P2 S5 — Write `tests/unit/test_security_headers.py` — Verify all expected headers present in responses
- [ ] **T08-054** P1 S1-S3 — Write `tests/integration/test_audit_trail.py` — Create template → update → delete, verify 3 audit entries; trigger AI suggestion → accept, verify 3 entries

## Dependencies & Execution Order

```
T08-001 → T08-002 (audit logger first)
T08-001 → T08-010, T08-011, T08-012, T08-013 (integrate after logger ready)
T08-020 → T08-021 → T08-022 (RLS cascade: templates → pages → elements)
T08-023 (profiles RLS, independent)
T08-030 → T08-031 (install → configure)
T08-032, T08-033 (parallel: headers + CORS)
T08-040 (admin endpoint, after audit logger)
```

## Parallel Opportunities

- Audit integration (T08-010 through T08-013) all in parallel after logger
- RLS migrations (T08-020 through T08-023) can be written in parallel (applied sequentially)
- Security middleware (T08-031, T08-032, T08-033) in parallel
- Tests (T08-050 through T08-054) in parallel after implementation
