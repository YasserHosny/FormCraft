# Quickstart: Feature 054 Development Setup

**Feature**: New-Theme Admin Console Analytics — Real Data Integration
**Branch**: `054-analytics-real-data`

---

## Prerequisites

- Python 3.12 + venv active in `formcraft-backend/`
- Node 20 + Angular CLI 19 in `formcraft-frontend/`
- Supabase local or cloud project with `SUPABASE_URL` + `SUPABASE_KEY` set

---

## Backend

```bash
cd formcraft-backend

# Run tests first (TDD — write before implementing)
pytest tests/integration/test_dashboard_analytics_routes.py -v

# Start dev server
uvicorn app.main:app --reload --port 8000

# Verify new endpoints are registered
curl -s http://localhost:8000/openapi.json | python3 -c \
  "import sys,json; paths=json.load(sys.stdin)['paths']; \
   [print(p) for p in paths if 'dashboard' in p]"
```

Expected output:
```
/api/analytics/dashboard/summary
/api/analytics/dashboard/submissions-over-time
/api/analytics/dashboard/department-distribution
/api/analytics/dashboard/top-templates
```

---

## Frontend

```bash
cd formcraft-frontend

# Start dev server (new theme route)
ng serve

# Navigate to: http://localhost:4200/ui/admin/analytics
# Must be logged in as admin role

# Run lint
ng lint

# Type check
npx tsc --noEmit
```

---

## Smoke Test Checklist

After both servers are running and you are logged in as admin:

1. Open `/ui/admin/analytics` — KPI cards should show real numbers (not 7,284 / 47 / 3:42 / 2,841 hardcoded values)
2. Click "٧ أيام" — line chart refreshes to 7 bars
3. Click "سنوي" — line chart shows 12 monthly bars (Jan–current month)
4. Click the "الإدارة" filter pill — a dropdown appears listing real departments
5. Select a department — all widgets update
6. Open DevTools Network tab — confirm 4 parallel requests to `/api/analytics/dashboard/*`
7. Reload within 5 minutes — confirm requests return cached data (same `cache_expires_at`)
8. Log in as non-admin (operator/designer) and navigate to `/ui/admin/analytics` — should be redirected

---

## Key Files Modified / Created

### Backend
| File | Change |
|------|--------|
| `app/services/analytics/dashboard_analytics.py` | **NEW** — `DashboardAnalyticsService` with 4 methods |
| `app/schemas/analytics.py` | **EXTEND** — 7 new Pydantic models |
| `app/api/routes/analytics.py` | **EXTEND** — 4 new routes under `/dashboard/` |
| `tests/integration/test_dashboard_analytics_routes.py` | **NEW** — contract tests (write first) |

### Frontend
| File | Change |
|------|--------|
| `src/app/features/analytics/models/analytics.model.ts` | **EXTEND** — 8 new interfaces |
| `src/app/features/analytics/services/analytics.service.ts` | **EXTEND** — 4 new methods |
| `src/app/features/ui-redesign/admin/analytics.component.ts` | **REPLACE** — remove all hardcoded data; add reactive filter state |
| `src/app/features/ui-redesign/admin/analytics.component.html` | **BIND** — add Angular bindings (no structural changes) |
| `src/assets/i18n/en.json` | **EXTEND** — new keys for loading/error/empty states |
| `src/assets/i18n/ar.json` | **EXTEND** — Arabic translations for the same keys |

---

## Translation Keys to Add

```json
// en.json additions under "analytics" key:
"dashboard": {
  "loading": "Loading...",
  "error": "Failed to load. Retry?",
  "empty": "No data for selected period.",
  "retry": "Retry",
  "filter": {
    "period": "Period",
    "department": "Department",
    "branch": "Branch",
    "all_departments": "All Departments",
    "all_branches": "All Branches"
  },
  "periods": {
    "7d": "7 Days",
    "30d": "30 Days",
    "90d": "90 Days",
    "yearly": "Yearly"
  }
}
```
