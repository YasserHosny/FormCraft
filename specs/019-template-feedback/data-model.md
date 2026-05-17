# Data Model: Template Feedback

**Date**: 2026-05-17

## Schema Changes

### New Table: `template_feedback`

| Column | Type | Nullable | Notes |
|--------|------|----------|-------|
| id | UUID | NO | PK, default gen_random_uuid() |
| template_id | UUID | NO | FK → templates(id) |
| template_version | INT | NO | Version number at time of submission |
| page_number | INT | YES | Page where issue was found (null = general) |
| element_key | TEXT | YES | Element key on that page (null = page-level or general) |
| category | TEXT | NO | 'bug', 'suggestion', 'question' |
| text | TEXT | NO | Feedback description (min 10 chars) |
| status | TEXT | NO | 'open', 'resolved'. Default 'open' |
| submitted_by | UUID | NO | FK → auth.users(id) |
| resolved_by | UUID | YES | FK → auth.users(id), set on resolve |
| resolved_at | TIMESTAMPTZ | YES | Timestamp of resolution |
| resolution_note | TEXT | YES | Optional note from resolver |
| org_id | UUID | NO | FK → organizations(id), RLS scope |
| created_at | TIMESTAMPTZ | NO | Default now() |

**Migration file**: `022_template_feedback.sql`

```sql
CREATE TABLE template_feedback (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
  template_version INT NOT NULL,
  page_number INT,
  element_key TEXT,
  category TEXT NOT NULL CHECK (category IN ('bug', 'suggestion', 'question')),
  text TEXT NOT NULL CHECK (char_length(text) >= 10),
  status TEXT NOT NULL DEFAULT 'open' CHECK (status IN ('open', 'resolved')),
  submitted_by UUID NOT NULL REFERENCES auth.users(id),
  resolved_by UUID REFERENCES auth.users(id),
  resolved_at TIMESTAMPTZ,
  resolution_note TEXT,
  org_id UUID NOT NULL REFERENCES organizations(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_template_feedback_template ON template_feedback(template_id, template_version DESC);
CREATE INDEX idx_template_feedback_status ON template_feedback(template_id, status);
CREATE INDEX idx_template_feedback_org ON template_feedback(org_id);

ALTER TABLE template_feedback ENABLE ROW LEVEL SECURITY;

CREATE POLICY template_feedback_org_isolation ON template_feedback
  USING (org_id = current_setting('app.current_org_id')::UUID);

COMMENT ON TABLE template_feedback IS
  'Structured feedback from operators on templates, linked to version/page/element.';
COMMENT ON COLUMN template_feedback.element_key IS
  'Stable element identifier within the template. Survives element recreation across versions.';
```

## Entity Relationships

```
template_feedback (NEW)
├── id (UUID PK)
├── template_id (UUID FK → templates)
├── template_version (INT)
├── page_number (INT, nullable)
├── element_key (TEXT, nullable)
├── category (TEXT: bug|suggestion|question)
├── text (TEXT, min 10 chars)
├── status (TEXT: open|resolved)
├── submitted_by (UUID FK → auth.users)
├── resolved_by (UUID FK → auth.users, nullable)
├── resolved_at (TIMESTAMPTZ, nullable)
├── resolution_note (TEXT, nullable)
├── org_id (UUID FK → organizations)
└── created_at (TIMESTAMPTZ)

Relationships:
  template_feedback.template_id → templates.id (N:1)
  template_feedback.submitted_by → auth.users.id (N:1)
  template_feedback.resolved_by → auth.users.id (N:1, nullable)
  template_feedback.element_key → elements.key (logical, not FK — element may be deleted)
```

## Validation Rules

| Rule | Enforced At | Error |
|------|-------------|-------|
| text min 10 characters | DB CHECK + API | 422 "Feedback must be at least 10 characters" |
| category must be bug/suggestion/question | DB CHECK + API | 422 "Invalid category" |
| status must be open/resolved | DB CHECK + API | 422 "Invalid status" |
| template_id must exist | DB FK | 404 "Template not found" |
| resolved_by required when status = resolved | API service | 422 "Resolver required" |
| Duplicate submission debounce (same text + element within 60s) | API service | 409 "Similar feedback recently submitted" |
| template_feedback scoped by org_id | RLS | Row not visible |

## Data Volume Impact

- Expected: 5-20 feedback items per template version lifecycle
- Low volume table; indexes on (template_id, status) sufficient
- No denormalization needed
