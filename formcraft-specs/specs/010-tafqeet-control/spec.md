# Feature Specification: Tafqeet Control (Arabic/English Amount-to-Words)

**Feature Branch**: `10-tafqeet-control`
**Created**: 2026-05-02
**Status**: Draft
**Priority**: P2
**Input**: FormCraft — Tafqeet amount-to-words control for cheques, legal, and financial forms

---

## Overview

Tafqeet (تفقيط) is the practice of writing a numeric amount in words, mandatory on Arabic cheques, legal contracts, and financial documents. This spec introduces a new `tafqeet` element type that auto-converts a linked `number` or `currency` element's value into human-readable words in Arabic, English, or both. The element is read-only and computed — never directly editable.

**Out of scope**: Country-specific regulated format presets (EG/SA/AE). Designers configure prefix/suffix manually per their document requirements.

---

## Clarifications

### Session 2026-05-02

- Q: Where does the tafqeet conversion run for the canvas preview (frontend JS vs backend API)? → A: Backend API endpoint — `tafqit` is a Python-only library; no JS equivalent. Frontend calls `POST /api/tafqeet/preview` for canvas preview conversion.
- Q: What happens when "both" mode text overflows the element's bounding box? → A: Overflow is allowed; Designer is responsible for sizing. Property panel shows a warning indicator when converted text exceeds bounding box at current previewValue.
- Q: What happens when tafqit/num2words throws an unexpected runtime exception? → A: Catch exception → render blank cell + write error entry to audit log with element key and amount value.
- Q: Do country-specific regulatory tafqeet format presets need to be enforced? → A: No — configurable prefix/suffix is sufficient; no country presets required.
- Q: Should successful tafqeet conversions produce a dedicated audit log entry? → A: No — tafqeet conversions are covered under the existing `pdf.render` audit event; only failures log a dedicated entry (FR-009b).

---

## User Scenarios & Testing

### User Story 1 — Add Tafqeet Element to Canvas (Priority: P1)

A Designer drags a "Tafqeet" element from the toolbox onto the canvas like any other element type. The element appears as a read-only text box with a visual indicator (e.g., "تفقيط" label and lock icon) showing it is computed.

**Acceptance Scenarios**:
1. Dragging the Tafqeet entry from the toolbox onto the canvas creates a `tafqeet` element at the drop position with default dimensions
2. The element appears on canvas with a dashed-border style and the label "تفقيط / Amount in Words" indicating it is computed
3. The Tafqeet element appears in the layers panel like any other element

---

### User Story 2 — Link Tafqeet to a Source Number/Currency Element (Priority: P1)

In the property panel, Designer selects a source element from a dropdown listing only `number` and `currency` elements present on the same page. Once linked, the tafqeet element reacts to the source value.

**Acceptance Scenarios**:
1. The property panel "Source Element" dropdown lists only `number` and `currency` elements on the current page by their `label_ar` or `key`
2. Linking to a `currency` element whose `currencyCode` is "SAR" and entering a design-time preview value of `5500.75` shows "خمسة آلاف وخمسمائة ريال سعودي وخمسة وسبعون هللة" on canvas
3. If no source element is linked, the canvas shows the element's `label_ar`/`label_en` as placeholder text
4. Changing the source element's `currencyCode` from "SAR" to "EGP" immediately updates the tafqeet canvas preview to use "جنيه" and "قرش"
5. Deleting the linked source element clears `sourceElementKey` and canvas returns to placeholder

---

### User Story 3 — Bilingual Output (Arabic + English) (Priority: P1)

The tafqeet element supports three output language modes: Arabic only, English only, or both. In "both" mode the Arabic line renders above the English line within the element's bounding box.

**Acceptance Scenarios**:
1. `outputLanguage = "ar"`: element renders Arabic text only, direction RTL
2. `outputLanguage = "en"`: element renders English text only, direction LTR
3. `outputLanguage = "both"`: element renders two lines — Arabic (RTL) on top, English (LTR) below, within the same bounding box
4. English output for `12500.50 EGP` is "Twelve Thousand Five Hundred Egyptian Pounds and Fifty Piastres Only"
5. Arabic output for `12500.50 EGP` is "اثنا عشر ألفاً وخمسمائة جنيه مصري وخمسون قرشاً فقط لا غير"

---

### User Story 4 — Configurable Prefix and Suffix (Priority: P2)

Designer configures optional prefix and suffix to wrap the converted text, common on cheques and legal documents.

**Acceptance Scenarios**:
1. `prefix = "faqat"`, `suffix = "la_ghair"`: output is "**فقط** اثنا عشر ألفاً **لا غير**"
2. `prefix = "none"`, `suffix = "faqat_la_ghair"`: output is "اثنا عشر ألفاً **فقط لا غير**"
3. `prefix = "none"`, `suffix = "none"`: output is plain converted text with no additions
4. In English mode, `suffix = "only"` appends "Only" at the end; `suffix = "none"` produces plain output
5. Prefix/suffix options shown as a dropdown in the property panel with Arabic preview updating live on canvas

---

### User Story 5 — Sub-Unit Handling (Decimals) (Priority: P1)

Fractional amounts are converted to sub-unit words per the linked currency's locale rules.

**Acceptance Scenarios**:
1. `1500.25 EGP` → "ألف وخمسمائة جنيه مصري وخمسة وعشرون قرشاً"
2. `3000.50 SAR` → "ثلاثة آلاف ريال سعودي وخمسون هللة"
3. `750.10 AED` → "سبعمائة وخمسون درهماً إماراتياً وعشرة فلوس"
4. Whole numbers with no decimal (e.g., `2000.00`) omit the sub-unit phrase entirely
5. Sub-units are always rounded to 2 decimal places before conversion

---

### User Story 6 — PDF Rendering with Filled Data (Priority: P1)

When the backend renders a PDF with a filled data map, the tafqeet element recomputes its output from the source element's filled value and renders it using WeasyPrint with full Arabic glyph shaping.

**Acceptance Scenarios**:
1. PDF rendered with `{"amount": "7350.00"}` where tafqeet is linked to `amount` outputs "سبعة آلاف وثلاثمائة وخمسون ريالاً سعودياً فقط لا غير"
2. Arabic tafqeet text in the PDF shows correct ligatures and right-to-left flow
3. "both" mode PDF renders two lines: Arabic above, English below, both within element's mm bounding box
4. If the source element's filled value is absent or null, the tafqeet cell renders blank (not an error)
5. Currency unit in PDF matches the source currency element's `currencyCode`

---

### User Story 7 — Zero and Edge Case Handling (Priority: P2)

**Acceptance Scenarios**:
1. Value `0` or `0.00` → "صفر" / "Zero"
2. Negative values are not supported; the element renders "—" with a warning in the property panel
3. Values exceeding one trillion render up to 12 digits (tafqit library limit); above that shows "—"
4. Non-numeric or missing source value renders placeholder without throwing an error

---

## Requirements

### Functional Requirements

**Data Model**
- FR-001: Add `tafqeet` to the element type enum in both DB migration and Pydantic/Zod schemas
- FR-002: Add the following tafqeet-specific fields to the Element entity (stored in `formatting` JSONB to avoid schema churn):
  - `sourceElementKey` (string | null) — key of the linked `number` or `currency` element on the same page
  - `currencyCode` (string | null, default `null`) — snapshot of the source element's `currencyCode` at time of linking; updated whenever the source element's `currencyCode` changes; used by PDF renderer to resolve currency without needing the source element's config at render time
  - `outputLanguage` (enum: `ar` | `en` | `both`, default `ar`)
  - `showCurrency` (bool, default `true`) — include currency unit name in output
  - `prefix` (enum: `none` | `faqat`, default `none`)
  - `suffix` (enum: `none` | `la_ghair` | `faqat_la_ghair` | `only`, default `none`)
  - `previewValue` (number | null) — design-time preview value shown in canvas; not used in PDF render

**Backend Conversion**
- FR-003: Implement a `TafqeetConverter` utility class in the backend with a single method `convert(amount: Decimal, currency_code: str, language: Literal["ar","en","both"], show_currency: bool, prefix: str, suffix: str) → str`
- FR-004: Use the `tafqit` Python library for Arabic conversion
- FR-005: Use `num2words` Python library with `lang="en"` for English conversion
- FR-006: Currency unit map (Arabic / English / sub-unit-Arabic / sub-unit-English):

  | Code | Arabic unit | English unit | Arabic sub-unit | English sub-unit |
  |------|-------------|--------------|-----------------|------------------|
  | EGP | جنيه مصري | Egyptian Pound | قرش | Piastre |
  | SAR | ريال سعودي | Saudi Riyal | هللة | Halala |
  | AED | درهم إماراتي | UAE Dirham | فلس | Fils |
  | USD | دولار أمريكي | US Dollar | سنت | Cent |

- FR-007: Sub-units always rounded to 2 decimal places; whole-number amounts omit sub-unit phrase
- FR-008: Zero amount returns "صفر" (ar) / "Zero" (en)
- FR-009: Negative amounts and amounts > 999,999,999,999 return `None`; caller renders blank
- FR-009b: Unexpected exceptions from `tafqit` or `num2words` are caught by `TafqeetConverter`; method returns `None`. In the PDF render context (`TafqeetRenderer`), the caller logs `action="tafqeet.conversion_error"` to the audit log with `resource_type="element"`, `resource_id=element.key`, and `metadata={amount, currency_code, error}`, then renders a blank cell. In the canvas preview context (`POST /api/tafqeet/preview`), the endpoint returns `{"result": null}` with no audit log entry (preview failures are transient user input, not production events).
- FR-010: `TafqeetConverter` is a pure stateless class with no external dependencies beyond tafqit and num2words

**PDF Engine Integration**
- FR-011: In `POST /api/pdf/render/{template_id}`, when a `tafqeet` element is encountered, resolve `sourceElementKey` against the filled data map to get the amount value
- FR-012: Call `TafqeetConverter.convert()` at render time with the resolved amount and element config
- FR-013: Arabic portions of tafqeet output pass through `arabic-reshaper` + `python-bidi` before WeasyPrint rendering
- FR-014: In `outputLanguage = "both"` mode, render Arabic text in one `<p>` with `dir="rtl"` and English in a second `<p>` with `dir="ltr"`, both within the element's mm bounding box
- FR-015: If resolved amount is null/missing, render element as blank (no error, no placeholder)

**Design Studio Frontend**
- FR-016: Add `tafqeet` entry to the element palette in the left toolbox with a descriptive icon and label "تفقيط / In Words"
- FR-017: Tafqeet element on canvas renders with a distinct dashed border and lock icon to indicate it is read-only/computed
- FR-018: Property panel for tafqeet element shows:
  - Source Element picker (dropdown, filtered to `number` and `currency` elements on same page, sorted by label_ar)
  - Output Language selector (Arabic / English / Both)
  - Show Currency toggle (enabled by default)
  - Prefix dropdown (None / فقط)
  - Suffix dropdown (None / لا غير / فقط لا غير / Only)
  - Preview Value input (number, used for design-time canvas preview only)
- FR-019: When `previewValue` changes, frontend calls `POST /api/tafqeet/preview` (stateless, no DB) with a 300ms debounce; canvas updates within 500ms of the last keystroke (300ms debounce + <200ms API latency p95); endpoint accepts `{amount, currency_code, language, show_currency, prefix, suffix}` and returns `{result: str}`
- FR-020: Tafqeet element canvas display: if `previewValue` is set, call preview endpoint and show result; otherwise show `label_ar` or `label_en` as placeholder
- FR-021: The tafqeet element cannot be placed inside a multi-select group for bulk type changes
- FR-026: When the converted preview text height exceeds the element's bounding box height, the property panel displays an orange warning: "Text may overflow — resize the element"
- FR-022: Zod schema updated to include all tafqeet-specific `formatting` fields with appropriate defaults

**Validation**
- FR-023: Backend validates that `sourceElementKey` (if provided) references an element of type `number` or `currency` on the same page; returns 422 if not
- FR-024: Backend rejects `suffix = "only"` when `outputLanguage = "ar"` (English-only suffix); returns 422

**Observability**
- FR-027: Successful tafqeet conversions are not logged separately — they are covered under the existing `pdf.render` audit event
- FR-028: Conversion failures are logged per FR-009b with action `tafqeet.conversion_error`

**Migration**
- FR-025: Supabase migration adds `tafqeet` to the `element_type` enum

### Key Entities (additions to Element)

Fields stored in `formatting` JSONB on the existing Element row:

```json
{
  "sourceElementKey": "amount_field",
  "outputLanguage": "both",
  "showCurrency": true,
  "prefix": "none",
  "suffix": "faqat_la_ghair",
  "previewValue": 12500.50
}
```

---

## Success Criteria

- SC-001: Arabic tafqeet conversion correct for integers and decimals for all four supported currencies using tafqit library
- SC-002: English tafqeet conversion correct for integers and decimals for all four supported currencies using num2words
- SC-003: PDF Arabic text shows correct ligatures and RTL flow (arabic-reshaper + python-bidi applied)
- SC-004: "Both" mode PDF renders Arabic and English lines within element's mm bounding box; overflow is permitted and Designer-managed — property panel displays a visible warning when previewValue text exceeds element height
- SC-005: Sub-unit phrases correctly omitted for whole-number amounts
- SC-006: Canvas preview updates within 500ms of last keystroke (300ms debounce + <200ms API latency p95)
- SC-007: Tafqeet element correctly resolves source value from fill data map at PDF render time
- SC-008: Zero, null, and out-of-range inputs handled gracefully — no unhandled exceptions
- SC-009: 100% of TafqeetConverter cases covered by unit tests (valid amounts, zero, null, each currency, each language, prefix/suffix combinations)
- SC-010: DB migration applies cleanly; existing elements unaffected
