# Implementation Plan: Security & Audit Logging

**Branch**: `08-security-audit` | **Date**: 2026-02-21 | **Spec**: [spec.md](./spec.md)

## Summary

Implement async audit logging for template operations, AI suggestions, and auth events; Supabase RLS policies for four roles; API rate limiting; CORS; security headers; and an admin audit log query endpoint.

## Technical Context

**Language/Version**: Python 3.12 (backend)
**Primary Dependencies**: FastAPI, slowapi (rate limiting), supabase-py
**Storage**: Supabase `audit_logs` table
**Testing**: pytest (unit + integration)

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| VIII. Security | ✅ Pass | Core deliverable of this spec |
| V. Test-First | ✅ Pass | RLS policies tested with different role tokens |

## Project Structure

### Backend (formcraft-backend)

```text
app/
├── core/
│   ├── audit.py                    # AuditLogger class, log_event() async helper
│   ├── middleware/
│   │   ├── security_headers.py     # X-Content-Type-Options, X-Frame-Options, HSTS, CSP
│   │   └── rate_limit.py           # slowapi rate limiter configuration
│   └── config.py                   # CORS_ORIGINS env var
├── api/routes/
│   └── admin.py                    # GET /api/admin/audit-logs (admin only)
└── schemas/
    └── audit.py                    # AuditLogEntry, AuditLogQueryParams

supabase/migrations/
├── 002_create_audit_logs.sql       # (already referenced in 01-auth-users)
├── 007_rls_templates.sql           # RLS for templates table
├── 008_rls_pages.sql               # RLS for pages table
├── 009_rls_elements.sql            # RLS for elements table
└── 010_rls_profiles.sql            # RLS for profiles table
```

### AuditLogger

```python
# audit.py
import asyncio
from datetime import datetime, timezone

class AuditLogger:
    def __init__(self, supabase_client):
        self.client = supabase_client

    async def log_event(
        self,
        user_id: str,
        action: str,
        resource_type: str,
        resource_id: str | None = None,
        metadata: dict | None = None,
        ip_address: str | None = None,
    ):
        """Non-blocking audit log write."""
        entry = {
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "metadata": metadata or {},
            "ip_address": ip_address,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            # Fire-and-forget: don't await in the request path
            asyncio.create_task(self._write(entry))
        except Exception:
            pass  # Audit failure must not block primary operation

    async def _write(self, entry: dict):
        self.client.table("audit_logs").insert(entry).execute()
```

### RLS Policy Design

```sql
-- templates RLS
ALTER TABLE public.templates ENABLE ROW LEVEL SECURITY;

-- Admin: full access
CREATE POLICY "admin_all" ON public.templates
    FOR ALL USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
    );

-- Designer: own drafts + all published
CREATE POLICY "designer_select" ON public.templates
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'designer')
        AND (created_by = auth.uid() OR status = 'published')
    );

CREATE POLICY "designer_insert" ON public.templates
    FOR INSERT WITH CHECK (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'designer')
        AND created_by = auth.uid()
    );

CREATE POLICY "designer_update" ON public.templates
    FOR UPDATE USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'designer')
        AND created_by = auth.uid() AND status = 'draft'
    );

CREATE POLICY "designer_delete" ON public.templates
    FOR DELETE USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'designer')
        AND created_by = auth.uid() AND status = 'draft'
    );

-- Operator + Viewer: published only, read-only
CREATE POLICY "readonly_published" ON public.templates
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role IN ('operator', 'viewer'))
        AND status = 'published'
    );
```

### Rate Limiting

```python
# rate_limit.py
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

# Applied to AI suggestion endpoint
@app.post("/api/ai/suggest-control")
@limiter.limit("30/minute")
async def suggest_control(request: SuggestionRequest):
    ...
```

### Security Headers Middleware

```python
# security_headers.py
class SecurityHeadersMiddleware:
    async def __call__(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response
```

## Research Notes

- **slowapi** is the standard FastAPI rate limiting library. Uses in-memory storage by default (sufficient for Phase 1 single-instance deployment).
- **Async audit logging**: Uses `asyncio.create_task()` so the audit write happens after the response is sent. No latency impact on the primary operation.
- **RLS cascade**: Pages and Elements inherit access from their parent template via JOINs in RLS policies.

## Complexity Tracking

No constitution violations.
