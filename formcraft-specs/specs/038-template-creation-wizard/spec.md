# Feature Specification: Template Creation Wizard

**Feature Branch**: `038-template-creation-wizard`  
**Created**: 2026-05-25  
**Status**: Draft  
**Vision Reference**: DS-02

## User Scenarios & Testing

### User Story 1 - Multi-Step Template Creation (Priority: P1)

As a designer, I need a guided multi-step wizard when creating a new template that collects basic info, locale settings, page setup, and starting point (blank/clone/import/package), so I can properly configure templates before entering the canvas editor.

**Why this priority**: Foundation for all template creation — the current simple dialog misses critical configuration (page size, margins, starting point options) that must be set before canvas work begins.

**Independent Test**: Click "New Template", walk through 4 wizard steps, arrive at canvas editor with all settings applied.

**Acceptance Scenarios**:

1. **Given** designer clicks "New Template", **When** the wizard opens, **Then** Step 1 shows: name (with fcAutoDir for Arabic/English), description, category dropdown, tags input.
2. **Given** designer completes Step 1, **When** advancing to Step 2 (Locale), **Then** fields show: language (AR/EN/Both), country (EG/SA/AE), currency, with the org defaults pre-selected.
3. **Given** designer completes Step 2, **When** advancing to Step 3 (Page Setup), **Then** fields show: page size (A4/A3/Letter/Legal/Custom mm), orientation (portrait/landscape), margins (top/bottom/left/right in mm).
4. **Given** designer completes Step 3, **When** advancing to Step 4 (Starting Point), **Then** four options are shown: Blank Canvas, Clone from Existing, Import from Scan (OCR), Import from Package (.formcraft).
5. **Given** designer selects "Blank Canvas" and clicks "Create", **When** the template is created, **Then** the canvas editor opens with the configured page size, orientation, margins, and locale settings applied.

---

### User Story 2 - Clone from Existing Template (Priority: P2)

As a designer, I need to start a new template by cloning an existing one from the wizard, so I can reuse proven layouts and modify them for new use cases.

**Why this priority**: Accelerates template creation — most new templates are variations of existing ones.

**Independent Test**: In wizard Step 4, select "Clone from Existing", browse templates, select one, create — verify all elements are copied.

**Acceptance Scenarios**:

1. **Given** designer selects "Clone from Existing" in Step 4, **When** the clone browser opens, **Then** a searchable list shows all accessible templates (own + department + marketplace imports).
2. **Given** designer selects a template to clone, **When** a preview loads, **Then** a thumbnail of the template canvas is shown with element count and page count.
3. **Given** designer clicks "Create", **When** the template is created, **Then** all pages, elements, properties, validation rules, and reference bindings are copied into the new draft.

---

### User Story 3 - Import from Package (Priority: P3)

As a designer or admin, I need to import a template from a .formcraft package file during the creation wizard, so I can bring in templates exported from other environments or shared by partners.

**Why this priority**: Enables template portability — critical for multi-environment and cross-org workflows.

**Independent Test**: In wizard Step 4, select "Import from Package", upload .formcraft file, create — verify template matches the exported original.

**Acceptance Scenarios**:

1. **Given** designer selects "Import from Package" in Step 4, **When** they upload a .formcraft file, **Then** the system parses the package and shows a preview: template name, page count, element count, and any binding warnings.
2. **Given** the package references reference data lists not in the current org, **When** import preview shows, **Then** warnings list the missing bindings with "Remap Later" option.
3. **Given** designer clicks "Create", **When** the template is created, **Then** all elements and validators are imported and the template opens in the canvas editor as a new draft.

---

### Edge Cases

- What happens when a .formcraft package is from an incompatible FormCraft version?
- How does the wizard handle the browser back button mid-wizard?
- What happens when the designer navigates away mid-wizard (auto-save wizard state)?
- How does "Clone from Existing" handle templates with department-scoped reference data?

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide a multi-step wizard for template creation with steps: Basic Info, Locale, Page Setup, Starting Point.
- **FR-002**: Step 1 (Basic Info) MUST collect: name (bilingual-aware), description, category, and tags.
- **FR-003**: Step 2 (Locale) MUST collect: language, country, currency with org defaults pre-selected.
- **FR-004**: Step 3 (Page Setup) MUST collect: page size (preset and custom mm), orientation, margins.
- **FR-005**: Step 4 (Starting Point) MUST offer: Blank Canvas, Clone from Existing, Import from Scan (OCR), Import from Package.
- **FR-006**: Clone starting point MUST copy all pages, elements, properties, validation rules, and reference bindings.
- **FR-007**: Package import MUST detect and warn about missing reference data bindings.
- **FR-008**: Wizard MUST support back/next navigation between steps without data loss.
- **FR-009**: On creation, the canvas editor MUST open with all wizard-configured settings applied.

### Key Entities

- **Template Creation Config**: Transient wizard state holding basic info, locale, page setup, and starting point selection until template creation is confirmed.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Designers complete the creation wizard in under 60 seconds for blank canvas starting point.
- **SC-002**: Clone from existing preserves 100% of element properties and bindings.
- **SC-003**: Package import correctly detects 100% of missing reference data bindings.
- **SC-004**: Wizard abandonment rate is below 10% (users who start the wizard but don't complete).
- **SC-005**: Page setup settings (size, orientation, margins) are correctly applied on canvas load.
