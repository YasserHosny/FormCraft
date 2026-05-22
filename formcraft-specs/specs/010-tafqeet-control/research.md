# Research: Tafqeet Control

**Branch**: `10-tafqeet-control` | **Date**: 2026-05-02

---

## Decision 1 — Arabic Conversion Library

**Decision**: Use `tafqit` PyPI package for Arabic number-to-words conversion.

**Rationale**: `tafqit` is purpose-built for Arabic tafqeet, handles grammatical gender agreement, dual forms, and large numbers correctly. It is the only actively maintained Python library dedicated to this use case.

**API**:
```python
from tafqit import tafqit
tafqit(12500)  # → "اثنا عشر ألفاً وخمسمائة"
```
Currency units are appended manually from the FR-006 currency map (tafqit converts the integer and decimal parts; the caller assembles the full phrase).

**Alternatives considered**:
- `arabic_number_to_words` — unmaintained, limited to small numbers
- Custom lookup tables — significant maintenance burden, rejected per YAGNI

---

## Decision 2 — English Conversion Library

**Decision**: Use `num2words` PyPI package with `lang="en"` for English cardinal conversion.

**Rationale**: `num2words` is the standard Python library for number-to-words across languages. Currency units are appended manually (same pattern as Arabic) for consistent output format across both languages.

**API**:
```python
from num2words import num2words
num2words(12500, lang="en", to="cardinal")  # → "twelve thousand, five hundred"
```
Integer and fractional parts converted separately; currency and sub-unit names appended from FR-006 map.

**Alternatives considered**:
- `inflect` — English only, no Arabic, rejected
- `num2words` with `to="currency"` — has limited currency support and inconsistent output format; manual assembly preferred for control

---

## Decision 3 — Canvas Preview Conversion

**Decision**: Frontend calls `POST /api/tafqeet/preview` on the backend. No frontend JS conversion library.

**Rationale**: `tafqit` is Python-only. A single backend implementation ensures canvas preview and PDF output are always identical. The endpoint is stateless (no DB), so p95 latency is well within the 300ms canvas budget (~80–130ms on local network).

**Confirmed by**: Clarification Q1 (2026-05-02)

---

## Decision 4 — Storage Strategy

**Decision**: Tafqeet-specific config stored in the existing `formatting` JSONB column on the `elements` table. No new columns or tables.

**Rationale**: Consistent with how `currency`, `date`, and other type-specific config is already stored. Avoids a migration that adds nullable columns for a single element type. The JSONB approach is already validated at runtime via Pydantic (backend) and Zod (frontend).

---

## Decision 5 — PDF Overflow Handling

**Decision**: Overflow is allowed and Designer-managed. Property panel shows an orange warning when `previewValue` text height exceeds element bounding box.

**Rationale**: FormCraft's Constitution §II mandates absolute mm positioning with no auto-scaling. The base renderer already sets `overflow: hidden` in CSS — tafqeet renderer will set `overflow: visible` with the warning surfaced in the property panel rather than silently clipping financial text.

**Confirmed by**: Clarification Q2 (2026-05-02)

---

## Decision 6 — Library Exception Handling

**Decision**: `TafqeetConverter.convert()` catches all exceptions from `tafqit`/`num2words`, returns `None`, and the caller (renderer and preview route) renders blank. The exception is written to the audit log with `action="tafqeet.conversion_error"`.

**Confirmed by**: Clarification Q3 (2026-05-02)

---

## Decision 7 — Audit Logging Scope

**Decision**: Successful conversions are covered under the existing `pdf.render` audit event. Only failures get a dedicated `tafqeet.conversion_error` entry.

**Confirmed by**: Clarification Q5 (2026-05-02)

---

## Decision 8 — New Dependencies

| Package | Version Constraint | Purpose |
|---|---|---|
| `tafqit` | `>=1.0` | Arabic number-to-words |
| `num2words` | `>=0.5.13` | English number-to-words |

Both are pure Python, no system dependencies, compatible with Python 3.12.

---

## All NEEDS CLARIFICATION: Resolved ✅
