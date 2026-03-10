# Feature Specification: Template Domain Model

**Feature Branch**: `03-template-model`
**Created**: 2026-02-21
**Status**: Draft
**Input**: FormCraft PRD Phase 1.3 – Template Domain Model

## User Scenarios & Testing

### User Story 1 - Create a New Template (Priority: P1)

A Designer can create a new form template by providing a name, description, category, language, and country. The template is created in "Draft" status with a default page (A4 dimensions).

**Why this priority**: Templates are the core domain object. All other features (designer, AI, PDF) operate on templates.

**Independent Test**: Can be tested by calling `POST /templates` and verifying the response contains a template with one default page.

**Acceptance Scenarios**:

1. **Given** a Designer is authenticated, **When** they create a template with name "شهادة ميلاد" (Birth Certificate), **Then** the template is created with status "Draft", version 1, and one default A4 page (210x297mm).
2. **Given** a Designer creates a template, **When** they omit the description, **Then** the template is created with an empty description (description is optional).
3. **Given** an Operator is authenticated, **When** they attempt to create a template, **Then** the API returns 403 Forbidden.

---

### User Story 2 - Manage Template Pages (Priority: P1)

A Designer can add, remove, and reorder pages within a template. Each page has configurable width, height, and optional background asset. Pages contain an ordered list of elements.

**Why this priority**: Multi-page support is required for complex government forms and certificates.

**Independent Test**: Can be tested by adding/removing pages via API and verifying the page order and dimensions.

**Acceptance Scenarios**:

1. **Given** a template with one page, **When** the Designer adds a second page with custom dimensions (148x210mm, A5), **Then** the template has two pages in order.
2. **Given** a template with three pages, **When** the Designer reorders page 3 to position 1, **Then** the page order is [3, 1, 2].
3. **Given** a template with one page, **When** the Designer attempts to delete the last page, **Then** the API returns 400 Bad Request (templates must have at least one page).
4. **Given** a page, **When** the Designer uploads a background image (JPEG/PNG), **Then** the image is stored in Supabase Storage and linked as `backgroundAsset`.

---

### User Story 3 - Manage Page Elements (Priority: P1)

A Designer can add, update, remove, and reorder elements on a page. Each element has a type, position (x, y, width, height in mm), labels (Arabic and English), validation rules, and formatting options.

**Why this priority**: Elements are the atomic building blocks of form design. The canvas editor and AI suggestion features depend on this data model.

**Independent Test**: Can be tested by CRUD operations on elements via API and verifying position, type, and properties.

**Acceptance Scenarios**:

1. **Given** a page, **When** the Designer adds a text element at position (10, 20, 50, 8) mm, **Then** the element is created with the specified position and type "text".
2. **Given** an element exists, **When** the Designer updates its label_ar to "الاسم الكامل" and label_en to "Full Name", **Then** both labels are persisted.
3. **Given** an element, **When** the Designer sets validation `{ required: true, maxLength: 100 }`, **Then** the validation object is stored as JSONB.
4. **Given** a page with 5 elements, **When** the Designer deletes element 3, **Then** the remaining 4 elements maintain correct ordering.

---

### User Story 4 - Template Status Lifecycle (Priority: P2)

Templates follow a lifecycle: Draft → Published. Only Admins can publish a template. Published templates are immutable (create a new version to edit). Drafts can be freely edited.

**Why this priority**: Status management prevents accidental modification of production forms.

**Independent Test**: Can be tested by transitioning template status and verifying edit restrictions.

**Acceptance Scenarios**:

1. **Given** a Draft template, **When** an Admin publishes it, **Then** the status changes to "Published" and the version is locked.
2. **Given** a Published template, **When** a Designer attempts to edit it, **Then** the API returns 400 Bad Request with message "Cannot edit published template".
3. **Given** a Published template, **When** a Designer clicks "Create New Version", **Then** a new Draft copy is created with version incremented by 1.

---

### User Story 5 - Template CRUD & Listing (Priority: P1)

Users can list templates filtered by status, category, language, and country. The list supports pagination and search by name.

**Why this priority**: Template listing is the primary navigation entry point for all roles.

**Independent Test**: Can be tested by creating multiple templates and verifying filter/search/pagination behavior.

**Acceptance Scenarios**:

1. **Given** 50 templates exist, **When** a user requests page 1 with limit 20, **Then** they receive 20 templates and pagination metadata.
2. **Given** templates in categories "Government" and "Finance", **When** filtering by category "Government", **Then** only government templates are returned.
3. **Given** a Viewer, **When** they list templates, **Then** they only see Published templates (Draft templates are hidden).

---

### Edge Cases

- What happens when two Designers edit the same template concurrently? → Last write wins; `updated_at` is checked for optimistic concurrency (409 Conflict if stale).
- What happens when a template has elements referencing a deleted background asset? → Element renders without background; UI shows a "missing asset" placeholder.
- What happens when element positions overlap? → Allowed — overlapping is a valid design choice (e.g., watermarks).
- What happens when a page has zero elements? → Valid state — empty pages are allowed.

## Requirements

### Functional Requirements

- **FR-001**: System MUST store Templates with: id (UUID), name, description, category, pages[], status (Draft/Published), version (integer), language (ar/en), country (EG/SA/AE).
- **FR-002**: System MUST store Pages with: id, template_id (FK), width (mm), height (mm), backgroundAsset (nullable URL), sort_order, elements[].
- **FR-003**: System MUST store Elements with: id, page_id (FK), type (enum), key (unique per template), label_ar, label_en, x (mm), y (mm), width (mm), height (mm), validation (JSONB), formatting (JSONB), required (boolean), direction (rtl/ltr/auto), sort_order.
- **FR-004**: Element types MUST include: text, number, date, currency, dropdown, radio, checkbox, image, qr, barcode.
- **FR-005**: System MUST enforce at least one page per template.
- **FR-006**: System MUST support optimistic concurrency via `updated_at` comparison.
- **FR-007**: System MUST support pagination (offset-based) with configurable page size (default 20, max 100).
- **FR-008**: System MUST support filtering by status, category, language, country.
- **FR-009**: System MUST support search by template name (partial match, case-insensitive).
- **FR-010**: Published templates MUST be immutable. Editing requires creating a new Draft version.
- **FR-011**: System MUST generate a unique `key` for each element (used for data binding in form filling).
- **FR-012**: All entities MUST have `created_at`, `updated_at`, `created_by` audit fields.
- **FR-013**: Background assets MUST be stored in Supabase Storage with path `templates/{template_id}/pages/{page_id}/background`.

### Key Entities

- **Template**: Core entity representing a form design. Has many Pages. Versioned.
- **Page**: Belongs to a Template. Has dimensions and optional background. Has many Elements. Ordered by sort_order.
- **Element**: Belongs to a Page. Positioned absolutely in mm. Has bilingual labels, typed validation, and formatting rules.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Template CRUD operations complete within 200ms (p95).
- **SC-002**: Template listing with filters returns within 300ms for up to 10,000 templates.
- **SC-003**: All entity relationships enforce referential integrity (no orphaned pages or elements).
- **SC-004**: Optimistic concurrency correctly detects and rejects stale updates (verified by integration tests).
- **SC-005**: 100% of element types defined in FR-004 are supported in the data model.
