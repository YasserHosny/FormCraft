# Implementation Plan: Operator Dashboard

**Branch**: `015-operator-dashboard` | **Date**: 2026-05-16 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/015-operator-dashboard/spec.md`

## Summary

Build the Form Desk operator dashboard (`/desk`) — the landing page operators see after login. Displays a searchable grid of published templates, a "Recently Used" section, a "Pinned Forms" section, a "Saved Drafts" section, and template version notifications. Requires a new aggregated backend endpoint, a new `operator_pins` table, and a new Angular feature module under the `/desk` route prefix.

## Technical Context

**Language/Version**: TypeScript / Angular 17 (frontend), Python 3.12 / FastAPI (backend)
**Primary Dependencies**: Angular Material (MatCard, MatPaginator, MatFormField, MatChip, MatIcon), @ngx-translate/core, Angular Router
**Storage**: Supabase PostgreSQL (new `operator_pins` table, queries against `templates`, `submissions`, `drafts`)
**Testing**: Jasmine + Karma (frontend), pytest (backend)
**Target Platform**: Modern browsers (Chrome, Firefox, Safari, Edge)
**Project Type**: Web application (SPA)
**Performance Goals**: Dashboard load < 1s, search < 500ms, pin action < 300ms
**Constraints**: Must work within the mode-switching route structure from feature 014; `/desk` route prefix already exists
**Scale/Scope**: Up to 200 published templates per org, up to 50 operators per org

## Constitution Check

| Principle | Status | Notes |
|-----------|:------:|-------|
| I. Arabic-First, RTL-Native | PASS | All dashboard text uses i18n JSON; card layout respects `[dir]` attribute; search supports Arabic input |
| II. mm-Precision Guarantee | N/A | No PDF or canvas work |
| III. Deterministic-First Validation | N/A | No validation logic in dashboard |
| IV. Two-Mode Architecture | PASS | Dashboard lives under `/desk` mode prefix; only accessible to permitted roles |
| V. Data Sovereignty & Multi-Tenancy | PASS | All queries scoped by org_id via Supabase RLS; operator_pins table requires org_id + RLS policy |
| VI. Audit Everything | PASS | Pin/unpin actions logged via existing audit middleware; draft deletion logged |
| VII. Template Versioning | PASS | Template cards show version number; notifications triggered on version increment |

## Project Structure

### Documentation (this feature)

```text
specs/015-operator-dashboard/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── api.md
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
formcraft-backend/
├── app/
│   ├── api/routes/
│   │   └── desk.py                    # NEW: /api/desk/* endpoints
│   ├── models/
│   │   └── desk.py                    # NEW: OperatorPin, DraftSummary models
│   ├── schemas/
│   │   └── desk.py                    # NEW: DashboardResponse, PinRequest schemas
│   └── services/
│       └── desk_service.py            # NEW: Dashboard aggregation service
└── migrations/
    └── 016_operator_pins.sql          # NEW: operator_pins table + RLS

formcraft-frontend/
├── src/app/
│   ├── features/
│   │   └── desk/
│   │       ├── desk.module.ts               # NEW: DeskModule
│   │       ├── desk-routing.module.ts        # UPDATE: add dashboard route
│   │       ├── dashboard/
│   │       │   ├── dashboard.component.ts    # NEW: main dashboard container
│   │       │   ├── dashboard.component.html  # NEW: dashboard template
│   │       │   └── dashboard.component.scss  # NEW: dashboard styles
│   │       ├── components/
│   │       │   ├── template-card/            # NEW: reusable template card
│   │       │   ├── recent-templates/         # NEW: recently used section
│   │       │   ├── pinned-templates/         # NEW: pinned forms section
│   │       │   ├── draft-list/               # NEW: saved drafts section
│   │       │   └── version-notifications/    # NEW: update notifications
│   │       └── services/
│   │           └── desk.service.ts           # NEW: dashboard API client
│   └── shared/
│       └── components/
│           └── template-card/                # Alternative: shared card component
└── src/assets/i18n/
    ├── ar.json                               # ADD: desk.* keys
    └── en.json                               # ADD: desk.* keys
```

**Structure Decision**: New `features/desk/` module owns the dashboard and all its sub-components. The desk module already exists as a route placeholder from feature 014 — we extend it with the actual dashboard. Template card component lives inside desk (not shared) since it has desk-specific behavior (pin toggle, recent badge).

## Phase 0: Research

**Decision 1**: Single aggregated dashboard endpoint vs. multiple API calls.
- **Chosen**: Single `GET /api/desk/dashboard` returning all sections in one response.
- **Rationale**: NFR-004 requires no N+1 calls. A single endpoint lets the backend optimize queries (parallel database calls, single RLS check). The response is structured into sections (`templates`, `recent`, `pinned`, `drafts`, `notifications`).
- **Alternatives rejected**: Separate endpoints per section (slower, N+1); GraphQL (not in tech stack); BFF pattern (over-engineering for one page).

**Decision 2**: Where to store operator pins.
- **Chosen**: New `operator_pins` table (operator_id, template_id, org_id, created_at) with unique constraint.
- **Rationale**: Server-side persistence works across devices (per spec SC-004). Lightweight join table — no complex data. RLS by org_id.
- **Alternatives rejected**: localStorage (doesn't sync); user preferences JSONB column (array manipulation in SQL is fragile); separate preferences service (over-engineered).

**Decision 3**: Where to derive "Recently Used" from.
- **Chosen**: Query `submissions` table grouped by template_id, ordered by max(created_at), limited to 10.
- **Rationale**: Submissions already exist (from Form Filler feature). No new table needed. The query is a simple GROUP BY with RLS.
- **Alternatives rejected**: Separate `recent_usage` tracking table (redundant with submissions); client-side tracking (doesn't sync cross-device).

**Decision 4**: How to handle template search.
- **Chosen**: Server-side search via `GET /api/desk/dashboard?search=KYC` with PostgreSQL `ILIKE` on name + description.
- **Rationale**: All filtering happens server-side for consistency with RLS. `ILIKE` is sufficient for the expected scale (< 200 templates). Full-text search is unnecessary complexity for this scale.
- **Alternatives rejected**: Client-side filtering (breaks pagination); PostgreSQL full-text search (over-engineering); Elasticsearch (not in tech stack).

**Decision 5**: Draft display on dashboard.
- **Chosen**: Dashboard displays draft metadata from a `drafts` table. The `drafts` table and actual save/resume CRUD will be created in the Form Filler feature (016+). For this feature, we create the dashboard UI that reads from the drafts table, and provide a stub response if the table doesn't exist yet.
- **Rationale**: The dashboard spec calls for displaying drafts, but the draft creation mechanism belongs to Form Filler. Decoupling lets us ship the dashboard first.
- **Alternatives rejected**: Skip drafts section entirely (violates spec); implement full draft CRUD now (scope creep).

## Phase 1: Design

### Data Model

**New Table**: `operator_pins`

```sql
CREATE TABLE operator_pins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operator_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (operator_id, template_id)
);

CREATE INDEX idx_operator_pins_operator ON operator_pins(operator_id);

ALTER TABLE operator_pins ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own pins"
ON operator_pins
FOR ALL
USING (operator_id = auth.uid())
WITH CHECK (operator_id = auth.uid());
```

No modifications to existing tables. Recent usage derived from `submissions`. Draft display depends on future `drafts` table.

### Contracts

**New Endpoint**: `GET /api/desk/dashboard`

Request query parameters:
| Param | Type | Required | Default | Notes |
|-------|------|----------|---------|-------|
| search | string | no | null | Filters templates by name/description (ILIKE) |
| category | string | no | null | Filter by template category |
| country | string | no | null | Filter by country code (EG, SA, AE) |
| language | string | no | null | Filter by template language |
| page | int | no | 1 | Templates grid pagination |
| limit | int | no | 20 | Templates per page (max 100) |

Response (200 OK):
```json
{
  "templates": {
    "items": [
      {
        "id": "uuid",
        "name": "KYC Form",
        "description": "Know Your Customer form",
        "category": "banking",
        "status": "published",
        "version": 3,
        "language": "ar",
        "country": "EG",
        "updated_at": "2026-05-16T10:00:00Z",
        "is_pinned": true
      }
    ],
    "total": 45,
    "page": 1,
    "limit": 20
  },
  "recent": [
    {
      "template_id": "uuid",
      "template_name": "KYC Form",
      "category": "banking",
      "version": 3,
      "last_used_at": "2026-05-16T09:30:00Z"
    }
  ],
  "pinned": [
    {
      "template_id": "uuid",
      "template_name": "KYC Form",
      "category": "banking",
      "version": 3,
      "is_published": true,
      "pinned_at": "2026-05-10T08:00:00Z"
    }
  ],
  "drafts": [],
  "notifications": [
    {
      "id": "uuid",
      "template_id": "uuid",
      "template_name": "KYC Form",
      "old_version": 2,
      "new_version": 3,
      "updated_at": "2026-05-16T08:00:00Z"
    }
  ]
}
```

**New Endpoint**: `POST /api/desk/pins`

Request:
```json
{
  "template_id": "uuid"
}
```

Response (201 Created):
```json
{
  "id": "uuid",
  "template_id": "uuid",
  "created_at": "2026-05-16T10:00:00Z"
}
```

Error (409 Conflict): Pin already exists.
Error (422): Pin limit (20) exceeded.

**New Endpoint**: `DELETE /api/desk/pins/:templateId`

Response (204 No Content)

**New Endpoint**: `DELETE /api/desk/notifications/:notificationId`

Response (204 No Content) — dismisses a version notification.

### i18n Keys

```json
// en.json additions
{
  "desk": {
    "title": "Form Desk",
    "search_placeholder": "Search forms...",
    "filter_category": "Category",
    "filter_country": "Country",
    "filter_language": "Language",
    "clear_filters": "Clear filters",
    "section_pinned": "Pinned Forms",
    "section_recent": "Recently Used",
    "section_drafts": "Saved Drafts",
    "section_all": "All Forms",
    "section_notifications": "Updates",
    "empty_no_templates": "No forms available. Contact your administrator.",
    "empty_no_results": "No forms match your search.",
    "pin": "Pin to favorites",
    "unpin": "Remove from favorites",
    "pin_limit": "Maximum 20 pinned forms reached.",
    "draft_resume": "Resume",
    "draft_delete": "Delete draft",
    "draft_delete_confirm": "Delete this draft? This cannot be undone.",
    "draft_expires": "Expires {{when}}",
    "draft_completion": "{{percent}}% complete",
    "notification_updated": "{{name}} updated to v{{version}}",
    "notification_dismiss": "Dismiss",
    "version": "v{{version}}",
    "last_used": "Last used {{date}}",
    "template_unavailable": "Template unavailable"
  }
}
```

```json
// ar.json additions
{
  "desk": {
    "title": "مكتب النماذج",
    "search_placeholder": "البحث في النماذج...",
    "filter_category": "التصنيف",
    "filter_country": "الدولة",
    "filter_language": "اللغة",
    "clear_filters": "مسح التصفية",
    "section_pinned": "النماذج المثبتة",
    "section_recent": "المستخدمة مؤخراً",
    "section_drafts": "المسودات المحفوظة",
    "section_all": "جميع النماذج",
    "section_notifications": "التحديثات",
    "empty_no_templates": "لا توجد نماذج متاحة. تواصل مع المسؤول.",
    "empty_no_results": "لا توجد نماذج تطابق بحثك.",
    "pin": "تثبيت في المفضلة",
    "unpin": "إزالة من المفضلة",
    "pin_limit": "الحد الأقصى 20 نموذج مثبت.",
    "draft_resume": "استئناف",
    "draft_delete": "حذف المسودة",
    "draft_delete_confirm": "حذف هذه المسودة؟ لا يمكن التراجع عن ذلك.",
    "draft_expires": "تنتهي {{when}}",
    "draft_completion": "{{percent}}% مكتمل",
    "notification_updated": "تم تحديث {{name}} إلى الإصدار {{version}}",
    "notification_dismiss": "تجاهل",
    "version": "الإصدار {{version}}",
    "last_used": "آخر استخدام {{date}}",
    "template_unavailable": "النموذج غير متاح"
  }
}
```

### Dashboard Layout (RTL-aware)

```
┌─────────────────────────────────────────────────┐
│ [Search bar...] [Category ▼] [Country ▼] [Lang ▼] │
├─────────────────────────────────────────────────┤
│ ★ Pinned Forms (hidden if empty)                │
│ ┌────────┐ ┌────────┐ ┌────────┐               │
│ │ Card 1 │ │ Card 2 │ │ Card 3 │               │
│ └────────┘ └────────┘ └────────┘               │
├─────────────────────────────────────────────────┤
│ 🕐 Recently Used (hidden if empty)              │
│ ┌────────┐ ┌────────┐ ┌────────┐               │
│ │ Card 1 │ │ Card 2 │ │ Card 3 │ ...           │
│ └────────┘ └────────┘ └────────┘               │
├─────────────────────────────────────────────────┤
│ 📋 Saved Drafts (hidden if empty)               │
│ ┌─────────────────────────────────────────┐     │
│ │ Draft row: name | 45% | 2h ago | Resume │     │
│ └─────────────────────────────────────────┘     │
├─────────────────────────────────────────────────┤
│ 📢 Updates (hidden if empty)                    │
│ ┌─────────────────────────────────────────┐     │
│ │ "KYC Form updated to v3" [Open] [✕]     │     │
│ └─────────────────────────────────────────┘     │
├─────────────────────────────────────────────────┤
│ All Forms                                       │
│ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │
│ │ Card   │ │ Card   │ │ Card   │ │ Card   │   │
│ └────────┘ └────────┘ └────────┘ └────────┘   │
│ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐   │
│ │ Card   │ │ Card   │ │ Card   │ │ Card   │   │
│ └────────┘ └────────┘ └────────┘ └────────┘   │
│                    < 1 2 3 >                    │
└─────────────────────────────────────────────────┘
```

In RTL mode, the entire layout mirrors: search bar aligns right, cards flow right-to-left, pagination controls flip.

### Component Architecture

```
DashboardComponent (container)
├── Search + Filters (toolbar area)
├── PinnedTemplatesComponent
│   └── TemplateCardComponent (reused)
├── RecentTemplatesComponent
│   └── TemplateCardComponent (reused)
├── DraftListComponent
│   └── DraftRowComponent
├── VersionNotificationsComponent
│   └── NotificationCardComponent
└── All Templates Grid
    ├── TemplateCardComponent (reused)
    └── MatPaginator
```

`TemplateCardComponent` is the shared building block used in pinned, recent, and all-templates sections. It accepts inputs for pin state, last-used date, and navigates on click.

## Complexity Tracking

| Decision | Justification |
|----------|--------------|
| Single aggregated endpoint | NFR-004 mandates no N+1; single round trip is measurably faster than 4 parallel calls |
| operator_pins as separate table | Constitution V requires org_id + RLS on all user data tables; a join table is the simplest way |
| Drafts section as read-only stub | Decouples dashboard from Form Filler feature; dashboard ships independently |
| ILIKE search over full-text search | < 200 templates per org makes ILIKE performant; no need for pg_trgm or tsvector at this scale |
