# Data Model: Feedback Dashboard Search & Labels

**Branch**: `012-feedback-dashboard-search` | **Phase**: 1

---

## New Table: `feedback_labels`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | `UUID` | PK, default `gen_random_uuid()` | Unique identifier |
| `name` | `TEXT` | NOT NULL, UNIQUE, `char_length <= 50` | Display name (case-sensitive unique) |
| `colour` | `TEXT` | NULLABLE, CHECK IN palette | Semantic colour token (see palette below) |
| `created_by` | `UUID` | NOT NULL, FK → `auth.users(id)` | Admin who created the label |
| `created_at` | `TIMESTAMPTZ` | NOT NULL, default `NOW()` | Creation timestamp |

**Colour palette CHECK constraint values**:
`'red'`, `'orange'`, `'yellow'`, `'green'`, `'teal'`, `'blue'`, `'purple'`, `'pink'`, `'grey'`, `'brown'`

**Indexes**:
- `(name)` — uniqueness enforced by UNIQUE constraint; index implicit
- `(created_at DESC)` — label management list default sort

**RLS Policies**:
- SELECT: admin role (label management) and authenticated users (future: if labels become visible to submitters — NOT in this feature)
- INSERT: admin role only
- UPDATE: admin role only
- DELETE: admin role only

---

## New Table: `feedback_submission_labels`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `feedback_id` | `UUID` | NOT NULL, FK → `feedback_submissions(id) ON DELETE CASCADE` | The tagged submission |
| `label_id` | `UUID` | NOT NULL, FK → `feedback_labels(id) ON DELETE CASCADE` | The assigned label |
| `assigned_by` | `UUID` | NOT NULL, FK → `auth.users(id)` | Admin who made the assignment |
| `assigned_at` | `TIMESTAMPTZ` | NOT NULL, default `NOW()` | Assignment timestamp |

**Primary Key**: `(feedback_id, label_id)` — composite, prevents duplicate assignments

**Indexes**:
- `(feedback_id)` — look up all labels for a submission (dashboard row render)
- `(label_id)` — look up all submissions carrying a label (label filter query)

**Constraint**: Max 5 labels per submission enforced at the service layer (checked before INSERT); a DB-level trigger is optional but not required for v1.

**RLS Policies**:
- SELECT: admin role
- INSERT: admin role
- DELETE: admin role

---

## Modified: `feedback_submissions` (feature 011)

No schema changes to the table itself. The feature adds:
- JOIN to `feedback_submission_labels` and `feedback_labels` in the `list_feedback()` service query
- `search` query parameter handled via ILIKE on `text_content`
- Extended `GET /api/admin/feedback` query parameters: `search`, `label_ids`

---

## Relationships

```
auth.users (existing)
    │
    └── feedback_labels (new)
            │
            └── feedback_submission_labels (new) ←── feedback_submissions (existing)
```

---

## Migration File

`009_create_feedback_labels.sql`

```sql
-- Colour palette enum values (used in CHECK constraint)
-- red, orange, yellow, green, teal, blue, purple, pink, grey, brown

CREATE TABLE feedback_labels (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT        NOT NULL UNIQUE CHECK (char_length(name) BETWEEN 1 AND 50),
    colour      TEXT        CHECK (colour IN (
                                'red','orange','yellow','green','teal',
                                'blue','purple','pink','grey','brown'
                            )),
    created_by  UUID        NOT NULL REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_feedback_labels_created_at ON feedback_labels (created_at DESC);

CREATE TABLE feedback_submission_labels (
    feedback_id  UUID NOT NULL REFERENCES feedback_submissions(id) ON DELETE CASCADE,
    label_id     UUID NOT NULL REFERENCES feedback_labels(id) ON DELETE CASCADE,
    assigned_by  UUID NOT NULL REFERENCES auth.users(id) ON DELETE SET NULL,
    assigned_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (feedback_id, label_id)
);

CREATE INDEX idx_fsl_feedback_id ON feedback_submission_labels (feedback_id);
CREATE INDEX idx_fsl_label_id    ON feedback_submission_labels (label_id);

-- RLS
ALTER TABLE feedback_labels ENABLE ROW LEVEL SECURITY;
ALTER TABLE feedback_submission_labels ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Admins can manage labels"
    ON feedback_labels FOR ALL
    USING (
        EXISTS (SELECT 1 FROM profiles WHERE profiles.id = auth.uid() AND profiles.role = 'admin')
    )
    WITH CHECK (
        EXISTS (SELECT 1 FROM profiles WHERE profiles.id = auth.uid() AND profiles.role = 'admin')
    );

CREATE POLICY "Admins can manage submission labels"
    ON feedback_submission_labels FOR ALL
    USING (
        EXISTS (SELECT 1 FROM profiles WHERE profiles.id = auth.uid() AND profiles.role = 'admin')
    )
    WITH CHECK (
        EXISTS (SELECT 1 FROM profiles WHERE profiles.id = auth.uid() AND profiles.role = 'admin')
    );
```

---

## Filter Query Pattern

The extended `list_feedback()` service method builds a dynamic query:

```
SELECT fs.*, 
       array_agg(fl.id)     AS label_ids,
       array_agg(fl.name)   AS label_names,
       array_agg(fl.colour) AS label_colours
FROM feedback_submissions fs
LEFT JOIN feedback_submission_labels fsl ON fsl.feedback_id = fs.id
LEFT JOIN feedback_labels fl             ON fl.id = fsl.label_id
WHERE
  (search IS NULL  OR fs.text_content ILIKE '%' || search || '%')
  AND (status IS NULL  OR fs.status = status)
  AND (user_id IS NULL OR fs.user_id = user_id)
  AND (date_from IS NULL OR fs.submitted_at >= date_from)
  AND (date_to IS NULL   OR fs.submitted_at <= date_to)
  AND (label_ids IS NULL OR fsl.label_id = ANY(label_ids))   -- OR across labels
GROUP BY fs.id
ORDER BY fs.submitted_at DESC
LIMIT limit OFFSET offset;
```
