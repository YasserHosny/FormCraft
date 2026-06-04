# FormCraft Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-05-26

## Active Technologies
- Python 3.12 (backend), TypeScript / Angular 19 (frontend) + FastAPI, Supabase (PostgreSQL + Auth), Angular Material, WeasyPrint (PDF export), ng2-charts / Chart.js (frontend charting) (027-analytics-reporting)
- Supabase PostgreSQL — live aggregation queries against existing tables (submissions, templates, profiles, departments, branches) (027-analytics-reporting)
- Python 3.12 (backend), TypeScript / Angular 19 (frontend) + FastAPI, Supabase (PostgreSQL + Auth), Angular Material, WeasyPrint (timeline PDF export) (028-approval-workflow)
- Supabase PostgreSQL — extends existing `template_reviews` table, adds `department_default_reviewers` table (028-approval-workflow)
- Python 3.12 backend; TypeScript / Angular 19 frontend + FastAPI, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, ngx-translate, RxJS, Python CSV/JSON libraries, `openpyxl` for workbook export, existing notification/email delivery infrastructure (032-data-export-integration)
- Supabase PostgreSQL; extend existing `templates`, `pages`, `elements`, `form_submissions`, `profiles`, `departments`, `branches`, `audit_logs`; add export schedule/delivery, integration credential, webhook subscription/delivery tables (032-data-export-integration)
- Python 3.12 backend; TypeScript / Angular 19 frontend + FastAPI, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, openpyxl, WeasyPrint, APScheduler, matplotlib, ng2-charts/Chart.js (033-operational-reports)
- Supabase PostgreSQL; extend existing `templates`, `pages`, `elements`, `submissions`, `profiles`, `departments`, `branches`; add `report_templates`, `report_schedules`, `report_archives` tables (033-operational-reports)
- Python 3.12 backend; TypeScript / Angular 19 frontend + FastAPI, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, ngx-translate, RxJS, Zod, Pydantic, existing validation/condition/tafqeet services, existing PDF renderer, existing notification/email infrastructure, pluggable SMS provider adapter, hCaptcha/reCAPTCHA adapter (034-external-form-portal-plan)
- Supabase PostgreSQL; extend existing `organizations`, `org_settings`, `templates`, `pages`, `elements`, `submissions`, `profiles`, `audit_logs`; add portal configuration/session/OTP/rate-limit/public-submission metadata tables (034-external-form-portal-plan)
- Python 3.12 backend; TypeScript / Angular 19 frontend + FastAPI, Pydantic, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, ngx-translate, RxJS, existing template/PDF/reference-data services (035-template-marketplace-codex)
- Supabase PostgreSQL with versioned migration for marketplace listing/import/review/transaction tables and RLS policies (035-template-marketplace-codex)
- Python 3.12 backend; TypeScript / Angular 19 frontend remains unchanged for this increment + FastAPI, Pydantic, Supabase PostgreSQL/Auth/RLS/Storage, existing AuditLogger (043-granular-template-permissions)
- Supabase PostgreSQL with versioned SQL migration in `formcraft-backend/migrations/041_granular_template_permissions.sql` (043-granular-template-permissions)
- Python 3.12 backend; TypeScript / Angular 19 frontend + FastAPI, Pydantic, Supabase PostgreSQL/Auth/Storage/RLS, existing OCR services (`AzureOCRClient`, `FieldClassifier`, `BoundingBoxConverter`), Angular Material, ngx-translate, RxJS (045-batch-ocr-onboarding)
- Supabase PostgreSQL plus Storage; add OCR onboarding batch/item/detection/decision tables and links to existing templates/pages/elements/form_detections/audit_logs (045-batch-ocr-onboarding)
- Python 3.12 backend; TypeScript / Angular 19 frontend + FastAPI, Pydantic, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, ngx-translate, RxJS, WeasyPrint (057-overlay-control-font-insets)
- Supabase PostgreSQL; no schema migration — extends existing `element.formatting` JSON dict with per-control font, line layout, and overflow policy (057-overlay-control-font-insets)

- Python 3.12 (backend), TypeScript / Angular 19 (frontend) + FastAPI, Supabase (PostgreSQL + Storage + Auth), Angular Material (001-customer-feedback)

## Project Structure

```text
src/
tests/
formcraft-specs/
└── specs/
```

## Specs Generation

- **Specs Location**: All specification files MUST be generated in `formcraft-specs/specs/` directory
- **Root Folder**: DO NOT generate or fetch specs in the project root folder `/FormCraft/`
- **Force Generation**: Always force generate specs at `formcraft-specs/specs/` location

## Commands

cd src [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] pytest [ONLY COMMANDS FOR ACTIVE TECHNOLOGIES][ONLY COMMANDS FOR ACTIVE TECHNOLOGIES] ruff check .

## Code Style

Python 3.12 (backend), TypeScript / Angular 19 (frontend): Follow standard conventions

## Recent Changes
- 057-overlay-control-font-insets: Added Python 3.12 backend; TypeScript / Angular 19 frontend + FastAPI, Pydantic, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, ngx-translate, RxJS, WeasyPrint — per-control font styling, generic line insets, and overflow/fit policy for overlay printing
- 043-granular-template-permissions: Added Python 3.12 backend; TypeScript / Angular 19 frontend remains unchanged for this increment + FastAPI, Pydantic, Supabase PostgreSQL/Auth/RLS/Storage, existing AuditLogger
- 045-batch-ocr-onboarding: Added Python 3.12 backend; TypeScript / Angular 19 frontend + FastAPI, Pydantic, Supabase PostgreSQL/Auth/Storage/RLS, existing OCR services (`AzureOCRClient`, `FieldClassifier`, `BoundingBoxConverter`), Angular Material, ngx-translate, RxJS
- 039-platform-admin-console: Added Python 3.12 backend; TypeScript / Angular 19 frontend + FastAPI, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, ngx-translate, RxJS, Pydantic, ng2-charts/Chart.js, APScheduler
- 035-template-marketplace-codex: Added Python 3.12 backend; TypeScript / Angular 19 frontend + FastAPI, Pydantic, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, ngx-translate, RxJS, existing template/PDF/reference-data services
- 033-operational-reports: Added Python 3.12 backend; TypeScript / Angular 19 frontend + FastAPI, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, openpyxl, WeasyPrint, APScheduler, matplotlib, ng2-charts/Chart.js
- 034-external-form-portal-plan: Added Python 3.12 backend; TypeScript / Angular 19 frontend + FastAPI, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, ngx-translate, RxJS, Zod, Pydantic, existing validation/condition/tafqeet services, existing PDF renderer, existing notification/email infrastructure, pluggable SMS provider adapter, hCaptcha/reCAPTCHA adapter
- 032-data-export-integration: Added Python 3.12 backend; TypeScript / Angular 19 frontend + FastAPI, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, ngx-translate, RxJS, Python CSV/JSON libraries, `openpyxl` for workbook export, existing notification/email delivery infrastructure
- 028-approval-workflow: Added Python 3.12 (backend), TypeScript / Angular 19 (frontend) + FastAPI, Supabase (PostgreSQL + Auth), Angular Material, WeasyPrint (timeline PDF export)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
