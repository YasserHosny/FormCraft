# Quickstart: Data Retention and Archival

## Local Development Setup

### 1. Database Migrations

Run the Supabase migration to create new tables and the archive schema:

```bash
cd formcraft-backend
supabase db diff --use-migra -f add_retention_tables
# Review the generated migration, then:
supabase db push
```

Migration files are located in:
- `formcraft-backend/migrations/044_add_retention_tables.sql`

### 2. Backend Dependencies

No new Python dependencies required. APScheduler is already installed (from 033-operational-reports).

Verify in `formcraft-backend/requirements.txt`:
```
APScheduler>=3.10.0
```

### 3. Start the Scheduler

Ensure the APScheduler retention job is registered at startup:

```python
# app/core/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from app.services.retention_job_service import RetentionJobService

scheduler = BackgroundScheduler()

# Run retention job evaluator every 5 minutes
scheduler.add_job(
    RetentionJobService.process_pending_jobs,
    'interval',
    minutes=5,
    id='retention_job_processor',
    replace_existing=True
)
```

### 4. Frontend Feature Module

Generate the retention admin module:

```bash
cd formcraft-frontend
ng generate module features/admin/retention --routing
ng generate service features/admin/retention/services/retention
ng generate interface features/admin/retention/models/retention

# Components
ng generate component features/admin/retention/components/policy-list
ng generate component features/admin/retention/components/policy-form
ng generate component features/admin/retention/components/policy-preview
ng generate component features/admin/retention/components/job-list
ng generate component features/admin/retention/components/job-detail
ng generate component features/admin/retention/components/legal-hold-list
ng generate component features/admin/retention/components/legal-hold-form
ng generate component features/admin/retention/components/archive-manifest-list
ng generate component features/admin/retention/components/archive-restore-dialog
```

### 5. Add Routes

In `formcraft-frontend/src/app/features/admin/admin.module.ts`, add the retention admin route:

```typescript
{ path: 'retention', loadChildren: () => import('./retention/retention-routing.module').then(m => m.RetentionRoutingModule) },
```

### 6. i18n Keys

Add the following translation keys to both `ar.json` and `en.json`:

```json
{
  "RETENTION": {
    "TITLE": "Data Retention",
    "POLICIES": "Retention Policies",
    "JOBS": "Retention Jobs",
    "LEGAL_HOLDS": "Legal Holds",
    "ARCHIVE_MANIFESTS": "Archive Manifests",
    "PREVIEW": "Preview Impact",
    "CREATE_POLICY": "Create Policy",
    "RUN_JOB": "Run Job",
    "PLACE_HOLD": "Place Legal Hold",
    "RESTORE": "Restore from Archive"
  }
}
```

## Testing Quickstart

### Backend Tests

```bash
cd formcraft-backend
pytest tests/unit/services/test_retention_policy_service.py -v
pytest tests/unit/services/test_retention_job_service.py -v
pytest tests/unit/services/test_preview_service.py -v
pytest tests/integration/test_retention_api.py -v
```

### Frontend Tests

```bash
cd formcraft-frontend
ng test --include='**/retention/**' --watch=false
```

## First-Time Usage

1. Log in as an Admin.
2. Navigate to **Admin > Data Retention**.
3. Create a retention policy:
   - Data Class: `submission`
   - Action: `archive`
   - Period: 365 days
   - Scope: All branches
4. Click **Preview** to see affected record count.
5. Save and activate the policy.
6. The next scheduled retention job will pick up the policy and create an archive manifest.
