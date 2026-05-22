# Feature Specification: Internationalization & RTL Support

**Feature Branch**: `02-i18n-rtl`
**Created**: 2026-02-21
**Status**: Draft
**Input**: FormCraft PRD Phase 1.2 – Multilingual System

## User Scenarios & Testing

### User Story 1 - Arabic-First UI Rendering (Priority: P1)

The application loads in Arabic (RTL) by default. All UI components, navigation, toolbars, and panels render correctly in RTL direction. Text alignment, icon positions, and layout flow are mirrored.

**Why this priority**: Arabic-first is a constitutional principle. The entire UI must work in RTL before any other feature is usable.

**Independent Test**: Can be tested by loading the app with `lang=ar` and visually verifying layout mirroring + running automated RTL layout tests.

**Acceptance Scenarios**:

1. **Given** a new user with no language preference, **When** the app loads, **Then** the HTML `dir` attribute is set to "rtl" and `lang` is set to "ar".
2. **Given** the app is in Arabic mode, **When** a sidebar navigation is rendered, **Then** it appears on the right side of the screen.
3. **Given** the app is in Arabic mode, **When** Angular Material components render (buttons, inputs, dialogs, menus), **Then** they display correctly in RTL layout with proper padding/margin mirroring.

---

### User Story 2 - Language Toggle (Priority: P1)

A logged-in user can switch between Arabic and English via a toggle in the toolbar. The switch is instant (no page reload), updates the `dir` attribute, re-renders all components, and persists the preference to the user's profile.

**Why this priority**: Bilingual support is a core requirement. Users must switch languages seamlessly.

**Independent Test**: Can be tested by clicking the language toggle and verifying DOM direction change + API call to persist preference.

**Acceptance Scenarios**:

1. **Given** the UI is in Arabic, **When** the user clicks the language toggle, **Then** the UI switches to English (LTR) without a page reload.
2. **Given** the user switched to English, **When** they refresh the page, **Then** the UI loads in English because the preference was persisted.
3. **Given** the UI is switching languages, **When** the toggle is clicked, **Then** all translation keys are resolved to the new language within 200ms.

---

### User Story 3 - Translation Key System (Priority: P1)

All user-facing strings are defined as translation keys in JSON files (`ar.json`, `en.json`). No hardcoded strings exist in templates or components. The i18n system supports nested keys and interpolation.

**Why this priority**: Translation-key architecture is a constitutional requirement. This must be in place before any UI string is added.

**Independent Test**: Can be tested by scanning all template/component files for hardcoded strings (lint rule) and verifying all keys resolve in both languages.

**Acceptance Scenarios**:

1. **Given** a component with text "Save Template", **When** the key `templates.actions.save` is resolved in Arabic, **Then** it returns "حفظ القالب".
2. **Given** a translation key that does not exist in `ar.json`, **When** it is resolved, **Then** the system falls back to the English value and logs a warning.
3. **Given** a developer adds a new component, **When** they include a hardcoded string, **Then** the lint rule flags it as an error.

---

### User Story 4 - Mixed Arabic-English Input Rendering (Priority: P1)

Form inputs and text fields correctly handle mixed Arabic-English content. When a user types Arabic text followed by English text (or vice versa), the rendering follows Unicode BiDi algorithm rules. Input fields use `dir="auto"` to detect direction from content.

**Why this priority**: Mixed-direction input is critical for form designers who label fields in Arabic but may include English technical terms.

**Independent Test**: Can be tested by typing mixed-direction text in input fields and verifying cursor position and text flow.

**Acceptance Scenarios**:

1. **Given** an input field with `dir="auto"`, **When** the user types "رقم National ID", **Then** the text renders with Arabic flowing RTL and "National ID" flowing LTR within the same line.
2. **Given** a text field in the canvas designer, **When** the user enters mixed content, **Then** the canvas preview matches the expected BiDi rendering.
3. **Given** a label field with Arabic content, **When** it is exported to PDF, **Then** the mixed-direction text renders identically to the canvas preview.

---

### User Story 5 - Angular Material RTL Compatibility (Priority: P2)

All Angular Material components (mat-sidenav, mat-toolbar, mat-form-field, mat-select, mat-dialog, mat-table, mat-menu) render correctly in both RTL and LTR modes. Custom theming adjusts for direction.

**Why this priority**: Angular Material has built-in RTL support via the CDK, but custom overrides may be needed for edge cases.

**Independent Test**: Can be tested by rendering a component gallery page in both directions and comparing layouts.

**Acceptance Scenarios**:

1. **Given** the app is in RTL mode, **When** a `mat-sidenav` is opened, **Then** it slides from the right.
2. **Given** the app is in RTL mode, **When** a `mat-form-field` with a prefix icon renders, **Then** the icon appears on the right side.
3. **Given** a `mat-table` in RTL mode, **When** columns are rendered, **Then** they flow from right to left.

---

### Edge Cases

- What happens when a translation file fails to load? → App uses the embedded fallback (English) and logs an error.
- What happens with very long Arabic text in fixed-width UI elements? → Text truncates with ellipsis; tooltip shows full text.
- What happens when the user's browser language is French? → System ignores browser language; uses stored user preference or defaults to Arabic.
- What happens with number formatting in Arabic locale? → Eastern Arabic numerals (٠١٢) are NOT used; Western Arabic numerals (012) are used per business requirement.

## Requirements

### Functional Requirements

- **FR-001**: System MUST support Arabic (ar) and English (en) as UI languages.
- **FR-002**: System MUST set `dir="rtl"` and `lang="ar"` on the `<html>` element when Arabic is active.
- **FR-003**: System MUST provide a language toggle accessible from the main toolbar.
- **FR-004**: Language switching MUST NOT require a page reload.
- **FR-005**: System MUST persist language preference to the user's profile via API.
- **FR-006**: System MUST resolve all UI strings via translation keys from JSON files.
- **FR-007**: System MUST provide a lint rule that flags hardcoded strings in templates.
- **FR-008**: System MUST support string interpolation in translation keys (e.g., `{count} templates`).
- **FR-009**: Input fields MUST use `dir="auto"` for mixed-direction content detection.
- **FR-010**: System MUST use Western Arabic numerals (0-9) in all locales.
- **FR-011**: System MUST mirror layout (flexbox direction, margins, paddings, icon positions) in RTL mode.
- **FR-012**: Angular Material CDK Bidi module MUST be configured at the app root.
- **FR-013**: Missing translation keys MUST fall back to English and log a warning.

### Key Entities

- **Translation File**: JSON key-value structure, nested by feature module. Located at `src/assets/i18n/{lang}.json`.
- **Direction Service**: Angular service that manages current direction state, provides `dir$` observable, and syncs with HTML element attributes.
- **Language Preference**: Stored in user profile table (see 01-auth-users spec).

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% of UI strings are resolved via translation keys (verified by lint rule — zero violations).
- **SC-002**: Language toggle completes within 200ms (no perceivable delay).
- **SC-003**: All Angular Material components pass visual regression tests in both RTL and LTR.
- **SC-004**: Mixed Arabic-English text in inputs renders correctly per Unicode BiDi spec.
- **SC-005**: Zero hardcoded strings detected in any template or component file.
