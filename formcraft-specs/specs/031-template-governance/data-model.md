# Data Model: Template Governance

## Existing Entities Used

### Template

Source table: `templates`

Relevant fields:
- `id` UUID primary key
- `name` text
- `category` text
- `status` text: `draft`, `submitted_for_review`, `approved`, `rejected`, `published`, `archived`, `deprecated`
- `version` integer
- `lineage_id` UUID
- `created_by` UUID to `profiles.id`
- `department_id` UUID nullable to `departments.id`
- `org_id` UUID to `organizations.id`
- `updated_at` timestamptz

Governance usage:
- Admin list reads all statuses for the current `org_id`.
- Bulk archive updates `status='archived'` using status-aware warnings for published templates.
- Bulk reassign updates `created_by`.
- Bulk category change updates `category`.
- Staleness flag is computed when `updated_at < now() - interval '6 months'`.

### Template Page

Source table: `pages`

Relevant fields:
- `id` UUID primary key
- `template_id` UUID
- `width_mm`, `height_mm`
- `background_asset`
- `sort_order`

Governance usage:
- Review context returns pages for read-only canvas preview.

### Template Element

Source table: `elements`

Relevant fields:
- `id` UUID primary key
- `page_id` UUID
- `type` text
- `key` text
- `label_ar`, `label_en` text nullable
- `validation` JSONB nullable
- `help_text` text or JSONB nullable, depending on applied feature migration
- `tab_order` integer nullable
- `x_mm`, `y_mm`, `width_mm`, `height_mm`

Governance usage:
- Read-only canvas preview.
- Quality score computation.
- Element-level review comment pinning.
- Missing validator and bilingual label lists.

### Template Review

Source table: `template_reviews`

Relevant fields:
- `id` UUID primary key
- `template_id` UUID
- `reviewer_id` UUID
- `action` text: `approved`, `rejected`, `changes_requested`
- `comment` text nullable
- `element_comments` JSONB nullable
- `org_id` UUID
- `created_at` timestamptz

Governance usage:
- Historical review decisions and timeline snapshots.
- New lifecycle comments are stored in `template_review_comments`; `element_comments` can still include a snapshot of comments submitted with a review action for compatibility.

### Form Submission

Source table: `form_submissions`

Relevant fields:
- `id` UUID primary key
- `template_id` UUID
- `template_version` integer
- `operator_id` UUID
- `org_id` UUID
- `created_at` timestamptz

Governance usage:
- Bulk archive usage warning counts distinct operators who submitted/printed selected published templates in the current calendar month.

## New Entity: Template Review Comment

Source table: `template_review_comments`

Fields:
- `id` UUID primary key, default `gen_random_uuid()`
- `org_id` UUID not null, references `organizations(id)`
- `template_id` UUID not null, references `templates(id)` on delete cascade
- `template_version` integer not null
- `review_id` UUID nullable, references `template_reviews(id)` on delete set null
- `reviewer_id` UUID not null, references `profiles(id)`
- `created_by` UUID not null, references `profiles(id)`
- `element_id` UUID nullable, references `elements(id)` on delete set null
- `element_key` text nullable
- `page_id` UUID nullable, references `pages(id)` on delete set null
- `x_mm` numeric(10,3) nullable — Canvas X coordinate in mm (Constitution II compliant)
- `y_mm` numeric(10,3) nullable — Canvas Y coordinate in mm (Constitution II compliant)
- `comment_text` text not null
- `status` text not null default `open`, allowed values `open`, `resolved`
- `designer_reply` text nullable
- `resolved_by` UUID nullable, references `profiles(id)`
- `resolved_at` timestamptz nullable
- `created_at` timestamptz not null default `now()`
- `updated_at` timestamptz not null default `now()`

Validation rules:
- `comment_text` must be non-empty after trimming.
- `status='resolved'` requires `resolved_by` and `resolved_at`.
- If `element_id` is null but `x_mm`/`y_mm` are present, the comment is shown as an orphan/general canvas pin.
- `template_version` must match the template version under review when the comment is created.
- Only org admins can create comments.
- Designers/admins with access to the template can resolve comments; designers generally resolve comments before resubmitting.
- Templates previously returned for changes cannot be resubmitted while any `template_review_comments` for the current template version remain `open`.

Relationships:
- Many comments belong to one template.
- Many comments may belong to one review action.
- A comment may point to one element and one page.

State transitions:

```text
open -> resolved
```

No reopen transition in v1. Admins can add a new comment on the next review if resolution is insufficient.

## New Entity: Validator Change Event

Source table: `validator_change_events`

Fields:
- `id` UUID primary key, default `gen_random_uuid()`
- `org_id` UUID nullable, references `organizations(id)`; null means platform/built-in validator event
- `validator_key` text not null (e.g., "national_id", "iban", "vat")
- `country` text nullable
- `field_type` text nullable
- `old_rule` JSONB not null (previous regex/format config)
- `new_rule` JSONB not null (updated regex/format config)
- `affected_template_count` integer not null default 0
- `change_summary` text not null
- `effective_date` date not null default `current_date`
- `created_by` UUID nullable, references `profiles(id)`
- `created_at` timestamptz not null default `now()`
- `updated_at` timestamptz not null default `now()`

Validation rules:
- `validator_key` must match keys used in element `validation` JSON.
- Org-specific custom validator changes use non-null `org_id`.
- Built-in validator events use null `org_id` and are visible to all orgs when matching template elements.

Governance usage:
- Compliance dashboard reports affected templates by joining recent validator change events to elements whose validation metadata references `validator_key`.

## Computed Model: Template Compliance Metric

Not stored.

Fields returned by API:
- `template_id`
- `template_name`
- `status`
- `quality_score` number 0-100
- `validator_coverage_pct`
- `bilingual_label_pct`
- `help_text_coverage_pct`
- `tab_order_pct`
- `is_stale`
- `stale_since`
- `missing_validator_fields`: array of `{ element_id, key, label }`
- `missing_bilingual_label_fields`: array of `{ element_id, key, missing: 'label_ar' | 'label_en' | 'both' }`
- `regulatory_alerts`: array of `{ validator_key, change_summary, effective_date }`

Formula:
- Validator coverage: required/input fields with validation divided by required/input fields, weight 40.
- Bilingual labels: fields with both `label_ar` and `label_en` divided by all elements with labels, weight 30.
- Help text coverage: required/input fields with help text divided by required/input fields, weight 20.
- Tab order: input fields with `tab_order` divided by input fields, weight 10.
- Score is rounded to nearest integer.

Input field types:
- `text`, `number`, `date`, `currency`, `checkbox`, `radio`, `dropdown`, `image`, `signature`, `table`

## Migration Sketch

```sql
CREATE TABLE IF NOT EXISTS template_review_comments (...);
ALTER TABLE template_review_comments ENABLE ROW LEVEL SECURITY;
CREATE POLICY template_review_comments_org_isolation ON template_review_comments
  FOR ALL
  USING (org_id = current_setting('app.current_org_id', true)::uuid)
  WITH CHECK (org_id = current_setting('app.current_org_id', true)::uuid);

CREATE INDEX idx_template_review_comments_template_status
  ON template_review_comments(org_id, template_id, status);
CREATE INDEX idx_template_review_comments_element
  ON template_review_comments(element_id);

CREATE TABLE IF NOT EXISTS validator_change_events (...);
ALTER TABLE validator_change_events ENABLE ROW LEVEL SECURITY;
CREATE POLICY validator_change_events_org_read ON validator_change_events
  FOR SELECT
  USING (
    org_id IS NULL OR org_id = current_setting('app.current_org_id', true)::uuid
  );
CREATE POLICY validator_change_events_org_write ON validator_change_events
  FOR INSERT
  WITH CHECK (org_id = current_setting('app.current_org_id', true)::uuid);
```
