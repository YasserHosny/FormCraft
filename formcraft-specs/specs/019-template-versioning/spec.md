# Feature Specification: Template Versioning & Cloning

**Feature Branch**: `018-template-versioning`  
**Created**: 2026-05-16  
**Status**: Draft  
**Input**: DS-08 — Template Versioning & Lifecycle; Constitution Principle VII (Template Versioning as Source of Truth)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Expanded Template Lifecycle States (Priority: P1)

When a designer completes editing a template, they submit it for review. A reviewer (admin or branch_manager) can approve or reject (with comments). Approved templates can be published by an admin. Published templates are immutable. Templates can be archived (hidden from Form Desk but accessible in library) or deprecated (visible but with "newer version available" warning).

**Why this priority**: The current draft→published binary is the #1 operational limitation. Designers cannot get templates reviewed before they go live, and there's no way to retire old templates safely.

**Independent Test**: Create template → submit for review → verify status changes → reject with comment → verify designer sees comment → resubmit → approve → publish → verify immutable → archive → verify hidden from Form Desk.

**Acceptance Scenarios**:

1. **Given** a designer clicks "Submit for Review" on a draft template, **When** the action completes, **Then** status changes to `submitted_for_review` and the template becomes read-only for the designer
2. **Given** a reviewer opens a template in `submitted_for_review` status, **When** they click "Reject" and enter a comment, **Then** status returns to `draft` and the designer sees the rejection comment
3. **Given** a reviewer approves a template, **When** an admin clicks "Publish", **Then** status becomes `published`, version number increments, and the template is available in Form Desk
4. **Given** a published template, **When** any user attempts to edit it, **Then** the system prevents editing and shows "Published templates are immutable — create a new version to make changes"
5. **Given** an admin archives a published template, **When** an operator opens Form Desk, **Then** the archived template does not appear in the template grid
6. **Given** an admin deprecates a published template (newer version exists), **When** an operator views the template in Form Desk, **Then** a warning banner shows "A newer version is available" with a link to the latest version

---

### User Story 2 - Version History & Lineage (Priority: P1)

Designers and admins can view the complete version history of a template family. Each version shows who created it, when it was published, what changed (element count, added/removed fields), and its current status. Templates in a lineage share a `lineage_id` that links all versions.

**Why this priority**: Constitution Principle VII mandates that version diff MUST be viewable for compliance evidence. Banks need to prove "what changed between v2 and v3 of the KYC form" for regulatory audits.

**Independent Test**: Publish v1 → create v2 → add a field → publish v2 → open version history → verify both versions listed → verify diff shows added field.

**Acceptance Scenarios**:

1. **Given** a template has 3 published versions, **When** the designer opens "Version History", **Then** all versions are listed with version number, publish date, publisher name, and element count
2. **Given** version history is open, **When** the user selects two versions for comparison, **Then** a diff view shows added fields (green), removed fields (red), and modified fields (yellow) with before/after values
3. **Given** a submission references template v2, **When** a user navigates from the submission to the template, **Then** they see v2 (not latest) with a note "This submission used version 2 — latest is v3"
4. **Given** any version in the lineage, **When** viewing its metadata, **Then** the lineage_id and parent_version_id are visible for traceability

---

### User Story 3 - Create New Version from Published (Priority: P1)

When a published template needs changes, the designer creates a new version. This copies all pages, elements, and properties into a new draft with an incremented version number. The original remains published and usable until the new version is published.

**Why this priority**: This is the core editing workflow — without it, any regulatory change forces creating a template from scratch. The existing `create_new_version()` backend method already supports this; this story adds the UI and lineage tracking.

**Independent Test**: Publish template v1 → click "Create New Version" → verify new draft (v2) has all fields from v1 → edit one field → publish v2 → verify v1 still accessible → verify Form Desk shows v2 by default.

**Acceptance Scenarios**:

1. **Given** a designer clicks "Create New Version" on a published template, **When** the new version is created, **Then** a draft with version=N+1 is created with all pages/elements copied, and `parent_version_id` points to the source
2. **Given** a new version (v2) is being edited, **When** an operator fills a form, **Then** Form Desk still uses v1 (the latest published version)
3. **Given** v2 is published, **When** Form Desk loads templates, **Then** v2 is now the default, and v1 is still accessible via version history or direct link
4. **Given** multiple drafts exist for a lineage, **When** viewing the template library, **Then** only the latest published version and in-progress drafts are shown (not a separate row per version)

---

### User Story 4 - Template Cloning (Priority: P2)

Any template (any status, any version) can be cloned into a completely new template with a new identity (new template_id, new lineage_id, version reset to 1). Cloning preserves all pages, elements, and properties but creates an independent template with no lineage link to the source.

**Why this priority**: Useful for creating similar forms (e.g., "KYC Individual" cloned to "KYC Corporate") or bootstrapping new templates from existing ones. Lower priority than versioning because it's a convenience feature, not a compliance requirement.

**Independent Test**: Clone a published template → verify new template has new ID → verify no lineage link → modify → publish → verify original unchanged.

**Acceptance Scenarios**:

1. **Given** a designer clicks "Clone" on any template, **When** the clone is created, **Then** a new template exists with a new ID, version=1, status=draft, and all pages/elements copied
2. **Given** a cloned template, **When** viewing its metadata, **Then** there is no `parent_version_id` or lineage link to the original (it's independent)
3. **Given** a template is cloned, **When** the original is later edited or archived, **Then** the clone is unaffected

---

### User Story 5 - Version Diff View (Priority: P2)

Users can compare any two versions of a template side-by-side. The diff shows: added elements, removed elements, modified element properties (position, validation, label changes), and page-level changes (added/removed pages, dimension changes).

**Why this priority**: Required by Constitution Principle VII for compliance evidence but slightly lower urgency than the state machine and lineage tracking which enable the rest.

**Independent Test**: Create v1 with 5 fields → create v2, add 2 fields, move 1 field → open diff view → verify added fields shown green, moved field shown yellow with position change.

**Acceptance Scenarios**:

1. **Given** the user selects v1 and v2 for comparison, **When** the diff loads, **Then** elements are matched by `key` and differences are categorized as added/removed/modified
2. **Given** an element's position changed between versions, **When** viewing the diff, **Then** the modification shows "x_mm: 20 → 35, y_mm: 50 → 55"
3. **Given** a page was added in v2, **When** viewing the diff, **Then** the new page and all its elements appear as additions

---

### Edge Cases

- What happens when a template is rejected after the reviewer added comments? The template returns to `draft` status; the designer sees rejection comments in a notification or on the template detail. Comments are stored as metadata on the template.
- What happens if two designers try to create a new version of the same published template simultaneously? Each gets their own draft version (v2, v3). When one publishes, the other's version number stays as-is (they become v3 when published). Conflict resolution is not needed — both drafts are independent.
- What happens to Form Desk submissions if a template is archived? Existing submissions remain valid and reprintable (field_values + version reference preserved). Only new form-filling sessions are blocked.
- What happens to in-progress drafts when a template is archived? Drafts reference specific versions; if the referenced template is archived, drafts can still be completed and submitted (the template data is already loaded into the draft). The operator sees a warning.
- What happens when cloning a template with background images? The clone references the same Storage URLs (images are not duplicated). If the original's storage is deleted, the clone loses its backgrounds. A warning is shown during clone if background assets exist.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST support template states: draft, submitted_for_review, approved, published, archived, deprecated
- **FR-002**: System MUST enforce state transitions: draft→submitted_for_review, submitted_for_review→approved|rejected, approved→published, published→archived|deprecated, rejected→draft, archived→published (un-archive)
- **FR-003**: Published templates MUST be immutable (no edits to pages, elements, or properties)
- **FR-004**: System MUST track template lineage via `lineage_id` (all versions of a template share the same lineage_id)
- **FR-005**: System MUST track parent-child relationships via `parent_version_id` (which version was this created from)
- **FR-006**: "Create New Version" MUST copy all pages, elements, and properties into a new draft row with version=N+1
- **FR-007**: Form Desk MUST default to the latest published version of each lineage
- **FR-008**: System MUST provide a version history view showing all versions in a lineage with metadata
- **FR-009**: System MUST provide a diff view comparing any two versions by matching elements on `key`
- **FR-010**: Diff MUST show: added elements, removed elements, modified properties (with before/after)
- **FR-011**: Template cloning MUST create a new template with new ID, new lineage_id, version=1, no parent link
- **FR-012**: Rejection MUST include a comment/reason visible to the designer
- **FR-013**: Deprecated templates MUST show a "newer version available" warning in Form Desk
- **FR-014**: Submissions MUST continue to reference the exact version used (existing behavior preserved)
- **FR-015**: System MUST log audit events for all state transitions: TEMPLATE_SUBMITTED, TEMPLATE_APPROVED, TEMPLATE_REJECTED, TEMPLATE_PUBLISHED, TEMPLATE_ARCHIVED, TEMPLATE_DEPRECATED, TEMPLATE_CLONED

### Non-Functional Requirements

- **NFR-001**: Version creation (copy all pages/elements) MUST complete within 2 seconds for templates with up to 100 elements
- **NFR-002**: Version history endpoint MUST respond within 500ms for lineages with up to 50 versions
- **NFR-003**: Diff computation MUST complete within 1 second for templates with up to 200 elements per version
- **NFR-004**: State transitions MUST be atomic (no partial state visible if transaction fails)

### Key Entities

- **Template** (modified): adds `lineage_id`, `parent_version_id`, expanded status enum
- **Template Review Comment**: rejection reason/comment stored in template metadata or separate table
- **Version Diff**: computed at query time (not stored), comparing two template versions by element key

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every published template is traceable to its full version history (lineage_id → all versions)
- **SC-002**: Published templates have zero edit operations succeed (immutability enforced at API level)
- **SC-003**: Diff view accurately identifies 100% of added/removed/modified elements between any two versions
- **SC-004**: State transitions are validated server-side (invalid transitions return 422)
- **SC-005**: Form Desk always shows the latest published version per lineage (no stale version served)
- **SC-006**: All state transitions produce audit log entries with actor, action, before/after status
