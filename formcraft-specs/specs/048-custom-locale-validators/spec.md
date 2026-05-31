# Feature 048: Custom Locale Validators

## Overview
Organization administrators can define custom regex-based validators with bilingual (Arabic/English) error messages, reusable across all templates in their organization. This eliminates the need for code changes to enforce org-specific validation rules.

## Objective
Enable org-scoped validator management that supports bilingual error messaging, audit trails, and seamless integration into the Design Studio canvas for template designers.

## Constitution Alignment

This feature **supplements** the built-in deterministic validator library required by Constitution Principle IV; it does **not** replace it. When a form element has a deterministic field type detected (national ID, IBAN, VAT, phone, CR number, TRN), the built-in validator runs **first**. Custom validators only run on elements whose detected field type is `unknown` / `generic`, or are explicitly added by the designer **after** all matching deterministic validators have already passed.

This precedence is non-negotiable:

> **Validator Precedence Rule:** `deterministic_validator(element) → custom_validator_1(element) → custom_validator_2(element) → ...`. If a deterministic validator rejects a value, no custom validator is evaluated and the deterministic error message is shown.

## User Stories

### US-1: Define Custom Validators (Org Admin)
**As an** Org Admin  
**I want to** define custom regex validators with Arabic and English error messages  
**So that** org-specific field validation rules are enforced without code changes

**Acceptance Criteria:**
- Admin can navigate to `/admin/validators` page
- Form allows input: name, regex pattern, error_message_ar, error_message_en
- Validator is stored in custom_validators table (org_id-scoped)
- Created validator immediately appears in Designer dropdowns

### US-2: Apply Custom Validators (Designer)
**As a** Designer  
**I want to** apply custom validators to form fields from a dropdown list  
**So that** I can reuse validated rule sets across multiple templates

**Acceptance Criteria:**
- Element properties panel shows "Custom Validators" section under validation rules
- Dropdown populated with org's custom validators
- Selecting a validator adds it to the element's validation array
- Multiple custom validators can be applied to a single field

### US-3: Discover Available Validators (Designer)
**As a** Designer  
**I want to** see which custom validators are available in my org  
**So that** I'm not inventing rules that already exist

**Acceptance Criteria:**
- Custom Validators dropdown displays validator name and description
- Validators searchable/filterable by name AND description (case-insensitive `ILIKE` over `name || ' ' || COALESCE(description, '')`)
- Default sort: `ORDER BY name ASC` (deterministic; no "relevance" scoring in Phase 1)
- Dropdown loads ≤ 200ms with up to 500 validators per org (see Performance Requirements)

### US-4: Audit Validator Usage (Org Admin)
**As an** Org Admin  
**I want to** see which templates use each custom validator  
**So that** I can track validation rule impact when updating rules

**Acceptance Criteria:**
- Admin can view a "Usage" or "Templates Using This" tab on each validator detail page
- Lists all templates (with link to edit) that reference the validator
- Count of active usages displayed prominently

## Functional Requirements

### FR-1: Custom Validator CRUD
- Admin can create, read, update, delete custom validators via `/admin/validators` API endpoints
- All operations are org-scoped; templates in Org A cannot see validators from Org B
- Validator fields (reconciled with schema): `id`, `org_id`, `name`, `description` (nullable), `regex_pattern`, `error_message_ar`, `error_message_en`, `created_at`, `updated_at`, `created_by`, `updated_by`, `deleted_at` (soft delete; NULL = active)
- Hard limits: max **500 custom validators per org**, max **10 custom validators per element**
- Rate limits: `POST /admin/validators` and `PUT /admin/validators/:id` capped at **30 req/min/org** (mitigates regex-DoS via mass creation)

### FR-2: Bilingual Error Messages
- Each validator stores `error_message_ar` and `error_message_en`. Both are required (`NOT NULL`, non-empty).
- During form fill, the error message is selected via this fallback chain:
  1. **Internal operator (Form Desk):** `profiles.preferred_language` → AR or EN
  2. **External portal user:** `template.language` field → AR or EN
  3. **Default fallback:** `error_message_en`
- Error message displayed inline next to form field when validation fails (consistent with built-in validator UI).
- All admin/designer UI strings (`"Custom Validators"`, `"Usage"`, `"Templates Using This"`, dialog text) MUST use i18n translation keys per Constitution Principle VII — no hardcoded strings. Key prefix: `admin.validators.*` and `designer.validators.*`.

### FR-3: Org-Scoped Isolation
- Custom validators are isolated per organization
- RLS policy: users can only see validators for their org
- Templates in different orgs cannot share or access each other's validators

### FR-4: Designer UI Integration
- Canvas element properties panel includes "Custom Validators" dropdown under validation rules
- Dropdown populated dynamically from org's custom validator list
- Selected validators appear as tags/chips in the validation rules section
- Ability to remove validators from element by clicking X on tag

### FR-5: Validator Reusability
- Once created, a custom validator appears in dropdown for ALL templates in the org
- No additional setup needed per template
- Validator name and description visible in dropdown for context

### FR-6: Template Audit Trail
- Reverse reference: Admin can see which templates use a specific custom validator
- Shows for each template: `template_name`, `template_status` (draft/published/archived), `last_submission_at` (derived: `MAX(submissions.created_at) WHERE submission.template_id = template.id AND validator_id ∈ element.custom_validators_ids`; NULL if never used)
- Computation: `last_submission_at` is computed on demand per request (no materialized column); query is indexed via existing `submissions.template_id` index and the new GIN index on `elements.custom_validators_ids` — see data-model.md
- API endpoint: `GET /admin/validators/:id/templates` returns paginated list (50/page) sorted by `last_submission_at DESC NULLS LAST`

### FR-7: Safe Update Semantics
- When an admin updates validator regex or error message, the new definition applies to **all subsequent form-fill validations** for templates referencing it (by ID).
- **In-flight form fills:** clients cache validators for the duration of a single fill session; the cache is refreshed (a) on each navigation between pages, and (b) at submission time — so the final submit always validates against the latest definition.
- Validators maintain referential integrity via the `custom_validators_ids UUID[]` on elements; soft-deleted validators (deleted_at NOT NULL) are skipped at validation time (no error raised — they simply don't fire).
- Audit log records: `VALIDATOR_UPDATED` event with before/after values for changed fields only.

### FR-8: Validator Naming and Discovery
- Clear, descriptive names help designers choose the right validator (e.g., "Egypt Commercial Register", "Saudi SADAD Bill Number")
- Optional `description` field for additional context. When NULL, dropdown shows name only.
- Search engine: PostgreSQL `ILIKE '%query%'` over `name || ' ' || COALESCE(description, '')`. Phase 1 does not use `to_tsvector` (deferred until ≥ 500 validators/org becomes common).

### FR-9: Regex Safety (ReDoS Prevention)
- `regex_pattern` max length: **500 characters** (enforced at API + DB CHECK)
- Pattern is compiled at create/update time in a sandboxed worker with a **100ms timeout** against a fixed suite of adversarial probe strings; patterns that timeout are rejected with `400 INVALID_REGEX_REDOS_RISK`.
- Runtime evaluation in form fill uses a **50ms per-pattern timeout**; on timeout the validation is treated as **pass** (fail-open) and an audit event `VALIDATOR_TIMEOUT` is logged for admin review (fail-closed would block legitimate forms during pathological inputs).
- Nested unbounded quantifiers (`(.+)+`, `(.*)*`) are rejected by a static pre-check before compilation.

## Data Model

### custom_validators Table
```sql
CREATE TABLE custom_validators (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  regex_pattern VARCHAR(500) NOT NULL,
  error_message_ar TEXT NOT NULL,
  error_message_en TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  created_by UUID NOT NULL REFERENCES profiles(id),
  updated_by UUID NOT NULL REFERENCES profiles(id),
  deleted_at TIMESTAMP,
  UNIQUE(org_id, name),
  CHECK (regex_pattern != ''),
  CHECK (error_message_ar != ''),
  CHECK (error_message_en != '')
);
```

### Validator References in elements Table
```sql
ALTER TABLE elements ADD COLUMN custom_validators_ids UUID[] DEFAULT '{}';
-- Stores array of custom_validators.id that apply to this element
```

### Audit Log Events
- VALIDATOR_CREATED: {validator_id, org_id, name, regex_pattern}
- VALIDATOR_UPDATED: {validator_id, field_changed, before_value, after_value}
- VALIDATOR_DELETED: {validator_id, org_id, name}

## Acceptance Criteria

1. **Storage & Persistence**
   - Custom validator created with name, regex pattern, error_message_ar, error_message_en is stored in custom_validators table
   - Soft delete: deleted_at timestamp set on deletion, not removed from DB

2. **Designer Integration**
   - Validator appears in Designer's element properties panel when editing any template in the org
   - Applied validators visible as tags in validation rules section

3. **Operator Experience**
   - Operator sees bilingual error message (respecting profile language preference) when entering invalid data
   - Error message displays inline next to the field

4. **Admin Interface**
   - Org Admin can view all custom validators at `/admin/validators` with search/filter by name
   - Admin can view which templates use each validator

5. **Update Safety**
   - Org Admin can update validator regex or error message without breaking templates
   - Change applies immediately to all active templates using the validator
   - Audit log records the update with before/after values

6. **Audit Trail**
   - All CRUD operations logged: VALIDATOR_CREATED, VALIDATOR_UPDATED, VALIDATOR_DELETED
   - Audit log includes operator identity, timestamp, and changes made

## API Endpoints

### Validator Management
- `GET /admin/validators` — List org's custom validators (with pagination, search)
- `POST /admin/validators` — Create new validator
- `GET /admin/validators/:id` — Get validator details
- `PUT /admin/validators/:id` — Update validator
- `DELETE /admin/validators/:id` — Soft delete validator
- `GET /admin/validators/:id/templates` — List templates using this validator

### Designer API
- `GET /api/validators/org` — Get all custom validators for current org (used by element properties panel)

## Implementation Phases

### Phase 1: Data Model & API
- Create custom_validators table with RLS policies
- Implement CRUD endpoints for `/admin/validators`
- Add audit logging for validator operations
- Add custom_validators_ids array to elements table

### Phase 2: Admin UI
- Build `/admin/validators` page with list/create/edit/delete UI
- Implement search and filter
- Add "Usage" tab showing templates using each validator

### Phase 3: Designer UI Integration
- Add "Custom Validators" section to element properties panel
- Implement dropdown populated from org's validators
- Add validation logic to support multiple custom validators on single field
- Visual indicator (tags/chips) for applied validators

### Phase 4: Form Filler Integration
- Integrate custom validator evaluation during form submission
- Display bilingual error messages based on operator's language preference
- Real-time validation feedback during form fill

### Phase 5: Testing & Documentation
- Unit tests for validator CRUD operations
- Integration tests for multi-validator evaluation
- E2E tests for designer and operator workflows
- API documentation and audit log documentation

## Dependencies

- Organizations table (existing)
- Elements table (existing — add custom_validators_ids column)
- Profiles table (for user references)
- Audit logs table (existing)
- Form fill validation engine (existing — extend to support custom validators)

## Risks & Mitigation

| Risk | Mitigation |
|------|-----------|
| Regex DoS (ReDoS) vulnerability | Validate regex patterns before storage; limit pattern length; test against known ReDoS patterns |
| Performance with many validators | Index org_id, name for fast lookups; cache validator list in memory per org |
| Validator update breaking forms | Soft delete instead of hard delete; version validators; maintain audit trail |
| Language fallback failures | Always provide both AR and EN messages; default to EN if operator's language not available |

## Testing Strategy

- **Unit**: Validator CRUD, regex validation, error message selection
- **Integration**: Multi-validator evaluation on form fields, audit logging
- **E2E**: Designer applies validator, operator submits form with validation, error shows in correct language
- **Performance**: Test with 100+ validators per org; measure dropdown load time

## Success Metrics

- Validators load in < 200ms for Designer dropdown
- Admin can create validator in < 30 seconds
- 100% of org-scoped validators correctly isolated (no cross-org leakage)
- Audit log captures all CRUD operations with no missing entries
