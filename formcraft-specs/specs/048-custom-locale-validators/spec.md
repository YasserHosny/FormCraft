# Feature 048: Custom Locale Validators

## Overview
Organization administrators can define custom regex-based validators with bilingual (Arabic/English) error messages, reusable across all templates in their organization. This eliminates the need for code changes to enforce org-specific validation rules.

## Objective
Enable org-scoped validator management that supports bilingual error messaging, audit trails, and seamless integration into the Design Studio canvas for template designers.

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
- Validators searchable/filterable by name
- Validators appear in order of relevance or creation date

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
- Validator fields: `id`, `org_id`, `name`, `description`, `regex_pattern`, `error_message_ar`, `error_message_en`, `created_at`, `updated_by`, `deleted_at` (soft delete)

### FR-2: Bilingual Error Messages
- Each validator stores `error_message_ar` and `error_message_en`
- During form fill, operator sees error in their preferred language (from profile setting)
- Error message displayed inline next to form field when validation fails

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
- Shows: template name, last used date, current usage status (active/inactive form)
- API endpoint: `GET /admin/validators/:id/templates` returns list of using templates

### FR-7: Safe Update Semantics
- When an admin updates validator regex or error message, change applies to ALL templates using it immediately
- Validators maintain referential integrity; no orphaned references
- Audit log records: VALIDATOR_UPDATED event with before/after values

### FR-8: Validator Naming and Discovery
- Clear, descriptive names help designers choose the right validator (e.g., "Egypt Commercial Register", "Saudi SADAD Bill Number")
- Optional description field for additional context
- Full-text search across name + description in dropdown

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
