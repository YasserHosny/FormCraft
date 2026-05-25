# FormCraft Development Guidelines

Auto-generated from all feature plans. Last updated: 2026-05-25

## Active Technologies
- Python 3.12 (backend), TypeScript / Angular 19 (frontend) + FastAPI, Supabase (PostgreSQL + Auth), Angular Material, WeasyPrint (PDF export), ng2-charts / Chart.js (frontend charting) (027-analytics-reporting)
- Supabase PostgreSQL — live aggregation queries against existing tables (submissions, templates, profiles, departments, branches) (027-analytics-reporting)
- Python 3.12 (backend), TypeScript / Angular 19 (frontend) + FastAPI, Supabase (PostgreSQL + Auth), Angular Material, WeasyPrint (timeline PDF export) (028-approval-workflow)
- Supabase PostgreSQL — extends existing `template_reviews` table, adds `department_default_reviewers` table (028-approval-workflow)
- Python 3.12 backend; TypeScript / Angular 19 frontend + FastAPI, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, ngx-translate, RxJS, Python CSV/JSON libraries, `openpyxl` for workbook export, existing notification/email delivery infrastructure (032-data-export-integration)
- Supabase PostgreSQL; extend existing `templates`, `pages`, `elements`, `form_submissions`, `profiles`, `departments`, `branches`, `audit_logs`; add export schedule/delivery, integration credential, webhook subscription/delivery tables (032-data-export-integration)
- Python 3.12 backend; TypeScript / Angular 19 frontend + FastAPI, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, ngx-translate, RxJS, Zod, Pydantic, existing validation/condition/tafqeet services, existing PDF renderer, existing notification/email infrastructure, pluggable SMS provider adapter, hCaptcha/reCAPTCHA adapter (034-external-form-portal-plan)
- Supabase PostgreSQL; extend existing `organizations`, `org_settings`, `templates`, `pages`, `elements`, `submissions`, `profiles`, `audit_logs`; add portal configuration/session/OTP/rate-limit/public-submission metadata tables (034-external-form-portal-plan)

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
- 034-external-form-portal-plan: Added Python 3.12 backend; TypeScript / Angular 19 frontend + FastAPI, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, ngx-translate, RxJS, Zod, Pydantic, existing validation/condition/tafqeet services, existing PDF renderer, existing notification/email infrastructure, pluggable SMS provider adapter, hCaptcha/reCAPTCHA adapter
- 032-data-export-integration: Added Python 3.12 backend; TypeScript / Angular 19 frontend + FastAPI, Supabase PostgreSQL/Auth/RLS/Storage, Angular Material, ngx-translate, RxJS, Python CSV/JSON libraries, `openpyxl` for workbook export, existing notification/email delivery infrastructure
- 028-approval-workflow: Added Python 3.12 (backend), TypeScript / Angular 19 (frontend) + FastAPI, Supabase (PostgreSQL + Auth), Angular Material, WeasyPrint (timeline PDF export)
- 027-analytics-reporting: Added Python 3.12 (backend), TypeScript / Angular 19 (frontend) + FastAPI, Supabase (PostgreSQL + Auth), Angular Material, WeasyPrint (PDF export), ng2-charts / Chart.js (frontend charting)


<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
