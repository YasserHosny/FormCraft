# Implementation Plan: Mobile and Offline Form Desk

**Branch**: `047-mobile-offline-desk` | **Date**: 2026-05-26 | **Spec**: `/media/yasserhosny/My Passport/Work/Projects/FormCraft/formcraft-specs/specs/047-mobile-offline-desk/spec.md`

## Summary

Add mobile-ready Form Desk controls, encrypted IndexedDB offline drafts and queued submissions, and FastAPI/Supabase endpoints for offline device registration, manifest retrieval, idempotent sync, conflict resolution, revocation, and audit-ready metadata.

## Technical Context

**Language/Version**: Python 3.12 backend; TypeScript / Angular 19 frontend
**Primary Dependencies**: FastAPI, Pydantic, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, ngx-translate, RxJS, WebCrypto, IndexedDB
**Storage**: Supabase PostgreSQL for policy/device/sync metadata; encrypted browser IndexedDB for local offline payloads
**Testing**: pytest backend tests; Angular unit/build checks; RTL/LTR responsive smoke checks
**Target Platform**: Web app on tablets and phones
**Constraints**: No plaintext local draft storage; template-version pinning; authenticated API only; translation keys for UI text

## Constitution Check

PASS: Arabic-first RTL, deterministic validation reuse, TDD tasks, normalized schema migration, translation keys, authenticated audit-ready backend, and scoped offline desk behavior.

## Project Structure

```text
formcraft-backend/app/api/routes/offline_desk.py
formcraft-backend/app/schemas/offline_desk.py
formcraft-backend/app/services/offline_desk_service.py
formcraft-backend/migrations/047_mobile_offline_desk.sql
formcraft-frontend/src/app/core/services/offline-desk.service.ts
formcraft-frontend/src/app/features/desk/offline/
formcraft-frontend/src/app/features/desk/fill/
```
