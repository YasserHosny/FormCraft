# Implementation Plan: Authentication & User Management

**Branch**: `01-auth-users` | **Date**: 2026-02-21 | **Spec**: [spec.md](./spec.md)

## Summary

Implement JWT-based authentication via Supabase Auth with four roles (Admin, Designer, Operator, Viewer), user profile management with language preference, and role-based API guards on both frontend and backend.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: FastAPI, supabase-py, @supabase/supabase-js, Angular Material
**Storage**: Supabase Auth (users) + Supabase DB (profiles, audit_logs)
**Testing**: pytest (backend), Jasmine/Karma (frontend)
**Target Platform**: Web (Bunny Magic Containers)
**Project Type**: Web application (polyrepo)

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Arabic-First | ✅ Pass | Language preference defaults to "ar" |
| V. Test-First | ✅ Pass | Contract tests for all auth endpoints planned |
| VI. Normalized Data | ✅ Pass | Users + Profiles as separate normalized tables |
| VII. Translation-Key | ✅ Pass | Auth UI uses i18n keys (depends on 02-i18n-rtl) |
| VIII. Security | ✅ Pass | JWT, RLS, audit trail are core deliverables |
| IX. YAGNI | ✅ Pass | No SSO, no OAuth providers |

## Project Structure

### Backend (formcraft-backend)

```text
app/
├── api/
│   ├── routes/
│   │   └── auth.py              # POST /auth/login, POST /auth/register, POST /auth/refresh
│   └── deps.py                  # get_current_user, require_role dependencies
├── models/
│   └── user.py                  # User, UserProfile Pydantic models
├── schemas/
│   ├── auth.py                  # LoginRequest, LoginResponse, RegisterRequest
│   └── user.py                  # UserProfileResponse, UpdateProfileRequest
├── core/
│   ├── security.py              # JWT verification, role extraction
│   └── supabase.py              # Supabase client singleton
└── services/
    └── user_service.py          # User CRUD via Supabase

supabase/
├── migrations/
│   ├── 001_create_profiles.sql  # User profiles table with language, role
│   └── 002_create_audit_logs.sql # Audit log table
└── seed.sql                     # Initial Admin user
```

### Frontend (formcraft-frontend)

```text
src/app/
├── core/
│   ├── auth/
│   │   ├── auth.service.ts      # Login, logout, refresh, token storage
│   │   ├── auth.guard.ts        # Route guard checking authentication
│   │   ├── role.guard.ts        # Route guard checking role
│   │   └── auth.interceptor.ts  # HTTP interceptor adding JWT to requests
│   └── models/
│       └── user.model.ts        # User interface, Role enum
└── features/
    └── auth/
        ├── login/               # Login page component
        ├── register/            # Register page (admin only)
        └── profile/             # User profile/settings page
```

### Database Schema

```sql
-- profiles table (extends Supabase auth.users)
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT NOT NULL DEFAULT 'viewer' CHECK (role IN ('admin', 'designer', 'operator', 'viewer')),
    language TEXT NOT NULL DEFAULT 'ar' CHECK (language IN ('ar', 'en')),
    display_name TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID REFERENCES auth.users(id)
);

-- RLS policies
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
-- Admin: full access
-- Designer/Operator/Viewer: read own profile, update own language/display_name
```

## Research Notes

- **Supabase Auth** handles email/password authentication, JWT issuance, and refresh tokens natively. No custom JWT signing needed.
- **Role storage**: Stored in `profiles.role` column, not in JWT custom claims (avoids Supabase Edge Function dependency). Backend reads role from DB on each request via `get_current_user` dependency.
- **Alternative rejected**: Storing role in JWT custom claims — would require Supabase Edge Functions or webhooks to keep claims in sync, adding complexity.

## Complexity Tracking

No constitution violations.
