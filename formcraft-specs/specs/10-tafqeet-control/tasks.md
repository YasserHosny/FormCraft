# Tasks: Tafqeet Control

**Input**: Design documents from `formcraft-specs/specs/10-tafqeet-control/`
**Prerequisites**: plan.md ✅ spec.md ✅ research.md ✅ data-model.md ✅ contracts/ ✅ quickstart.md ✅

**Tests**: Included — Constitution §V mandates TDD (Red → Green → Refactor). Test tasks are marked; they MUST be written and FAILING before the corresponding implementation task begins.

**Organization**: Tasks grouped by user story for independent implementation, testing, and delivery.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel (different files, no inter-task dependency)
- **[Story]**: User story this task belongs to (US1–US7)
- All file paths are relative to their respective repo root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install dependencies, apply DB migration, register new type in enums and schemas. No user story work begins until this phase is complete.

- [X] T001 Add `tafqit` and `num2words` to `formcraft-backend/requirements.txt` and install in venv
- [X] T002 Create DB migration `formcraft-backend/migrations/009_tafqeet_element_type.sql` with `ALTER TYPE element_type ADD VALUE IF NOT EXISTS 'tafqeet'` and apply via Supabase
- [X] T003 Add `TAFQEET = "tafqeet"` to `ElementType` enum in `formcraft-backend/app/models/enums.py`
- [X] T004 [P] Add `'tafqeet'` to `ElementType` union type in `formcraft-frontend/src/app/models/template.model.ts`
- [X] T005 [P] Add tafqeet entry to `ELEMENT_DEFAULTS` in `formcraft-frontend/src/app/models/element-defaults.ts` (`width_mm: 120, height_mm: 12, label_ar: 'المبلغ كتابةً', label_en: 'Amount in Words', icon: 'spellcheck'`)
- [X] T006 [P] Create `formcraft-backend/app/schemas/tafqeet.py` with `TafqeetPreviewRequest` and `TafqeetPreviewResponse` Pydantic models per `contracts/tafqeet-api.json`
- [X] T007 [P] Create `formcraft-frontend/src/app/shared/schemas/tafqeet-formatting.schema.ts` with `TafqeetFormattingSchema` Zod schema per `data-model.md`

**Checkpoint**: Dependencies installed, migration applied, enums updated in both repos, schemas defined.

---

## Phase 2: Foundational — TafqeetConverter + Preview Endpoint

**Purpose**: Core conversion engine (used by canvas preview AND PDF renderer). Covers the conversion logic for US2, US3, US4, US5, US7. **MUST be complete before any user story phase begins.**

⚠️ **CRITICAL — TDD ORDER**: Write tests (T008, T011) FIRST, confirm they FAIL, then implement (T009–T010, T012–T013).

- [X] T008 Write unit tests (FAILING) for `TafqeetConverter` in `formcraft-backend/tests/services/test_tafqeet_converter.py` — cover: valid integers (all 4 currencies), decimals with sub-units, whole numbers (no sub-unit phrase), zero → "صفر"/"Zero", negative → None, >1T → None, all prefix/suffix combos, ar/en/both language modes, `show_currency=False`, library exception → None
- [X] T009 Create `formcraft-backend/app/services/tafqeet/__init__.py` (empty module init)
- [X] T010 Implement `TafqeetConverter` in `formcraft-backend/app/services/tafqeet/converter.py` using `tafqit` + `num2words` + `CURRENCY_MAP` per `plan.md` until T008 tests pass
- [X] T011 Write contract tests (FAILING) for preview route in `formcraft-backend/tests/api/test_tafqeet_route.py` — cover: 200 with valid payload, 401 without JWT, 422 for `suffix="only"` + `language="ar"`, 200 with `result: null` for out-of-range amount
- [X] T012 Implement `POST /tafqeet/preview` route in `formcraft-backend/app/api/routes/tafqeet.py` per `plan.md` until T011 tests pass
- [X] T013 Register tafqeet router in `formcraft-backend/app/main.py` (`app.include_router(tafqeet.router, prefix="/api")`)

**Checkpoint**: `pytest tests/services/test_tafqeet_converter.py tests/api/test_tafqeet_route.py` all green. `POST /api/tafqeet/preview` responding correctly.

---

## Phase 3: User Story 1 — Add Tafqeet Element to Canvas (Priority: P1) 🎯 MVP Start

**Goal**: Designer can drag a Tafqeet element from the toolbox onto the Konva canvas. It appears with a dashed border and lock icon. It shows in the layers panel.

**Independent Test**: Drag "تفقيط / In Words" from the toolbox → element appears on canvas with dashed border, lock icon, and placeholder label. Visible in layers panel.

- [X] T014 [US1] Add tafqeet entry to the element palette array in `formcraft-frontend/src/app/features/designer/designer-page/designer-page.component.ts` (palette icon `spellcheck`, labels `تفقيط / In Words`)
- [X] T015 [US1] Implement tafqeet Konva node rendering in the canvas layer in `formcraft-frontend/src/app/features/designer/services/canvas.service.ts` — dashed stroke border, lock icon overlay, placeholder label text, read-only (no direct text editing)
- [X] T016 [US1] Confirm tafqeet element appears in the layers panel (no separate change needed if layers panel is driven by the elements array — verify and fix if not)

**Checkpoint**: US1 fully testable. Drag tafqeet → canvas shows element with dashed border + lock icon + placeholder. Layers panel lists it.

---

## Phase 4: User Story 2 — Link Tafqeet to Source Element (Priority: P1)

**Goal**: Designer picks a source `number`/`currency` element from the property panel dropdown. Entering a `previewValue` triggers `POST /api/tafqeet/preview` and updates the canvas text within 300ms. Deleting the source element clears the link.

**Independent Test**: Link tafqeet to a `currency` element (SAR). Enter `previewValue = 5500.75`. Canvas shows correct Arabic tafqeet within 300ms. Delete source → canvas returns to placeholder.

- [X] T017 [US2] Create `formcraft-frontend/src/app/features/designer/services/tafqeet.service.ts` with `preview(req: TafqeetPreviewRequest): Observable<TafqeetPreviewResponse>` calling `POST /api/tafqeet/preview`
- [X] T018 [US2] Create `TafqeetPropertyPanelComponent` shell in `formcraft-frontend/src/app/features/designer/components/tafqeet-property-panel/tafqeet-property-panel.component.ts` — inputs: `element`, `pageElements`; outputs: `elementChange`
- [X] T019 [US2] Implement source element picker dropdown in `tafqeet-property-panel.component.html` — filters `pageElements` to `type === 'number' || 'currency'`, sorted by `label_ar`, binds to `formatting.sourceElementKey`
- [X] T020 [US2] Implement `previewValue` number input in `tafqeet-property-panel.component.html` — on change: call `TafqeetService.preview()` with `currency_code` from `formatting.currencyCode` snapshot (not resolved at call time from source element), debounce 300ms, update canvas Konva text node on response
- [X] T021 [US2] Wire `TafqeetPropertyPanelComponent` into `designer-page.component.ts` — show when selected element type is `'tafqeet'`
- [X] T022 [US2] Handle source element deletion and currencyCode sync in `canvas.service.ts` — when a `number`/`currency` element is deleted, find any tafqeet elements on the same page with matching `sourceElementKey`, clear `sourceElementKey` and `currencyCode` snapshot, revert canvas to placeholder; when a `currency` element's `currencyCode` changes, update `formatting.currencyCode` snapshot on any linked tafqeet elements on the same page

**Checkpoint**: US2 fully testable. Source picker, preview call, canvas update, and deletion cleanup all work.

---

## Phase 5: User Story 3 — Bilingual Output (Priority: P1)

**Goal**: Property panel exposes output language selector (Arabic / English / Both). "Both" mode renders Arabic line above English line on canvas and in PDF.

**Independent Test**: Set `outputLanguage = "both"`, enter `previewValue = 12500.50` with EGP. Canvas shows two lines: Arabic (RTL) above, English (LTR) below.

- [X] T023 [US3] Add output language selector (Arabic / English / Both) to `tafqeet-property-panel.component.html` bound to `formatting.outputLanguage`; on change re-call preview if `previewValue` set
- [X] T024 [US3] Update `canvas.service.ts` tafqeet node rendering to handle "both" mode — render two `Konva.Text` nodes stacked within the element's bounding box (Arabic RTL on top, English LTR below)
- [X] T025 [US3] Add `show_currency` toggle to `tafqeet-property-panel.component.html` bound to `formatting.showCurrency`; on change re-call preview if `previewValue` set

**Checkpoint**: US3 fully testable. Language toggle updates canvas preview correctly for all three modes.

---

## Phase 6: User Story 4 — Configurable Prefix and Suffix (Priority: P2)

**Goal**: Property panel exposes prefix (None / فقط) and suffix (None / لا غير / فقط لا غير / Only) dropdowns. Selections update canvas preview live. Backend rejects invalid `suffix="only"` + `language="ar"` combination.

**Independent Test**: Set `prefix="faqat"`, `suffix="la_ghair"` → canvas preview shows "فقط [text] لا غير". Set `suffix="only"` with `language="ar"` → backend returns 422, property panel shows validation error.

- [X] T026 [US4] Add prefix dropdown (None / فقط) to `tafqeet-property-panel.component.html` bound to `formatting.prefix`; on change re-call preview
- [X] T027 [US4] Add suffix dropdown (None / لا غير / فقط لا غير / Only) to `tafqeet-property-panel.component.html` bound to `formatting.suffix`; on change re-call preview; disable "Only" option when `outputLanguage = "ar"` (client-side guard matching FR-024)
- [X] T028 [US4] Add backend validation in `formcraft-backend/app/api/routes/tafqeet.py` — reject `suffix="only"` when `language="ar"` with HTTP 422 (already covered by T011 contract test; ensure implementation handles it)

**Checkpoint**: US4 fully testable. Prefix/suffix combinations render correctly; invalid combination blocked.

---

## Phase 7: User Story 5 — Sub-Unit Handling (Priority: P1)

**Goal**: Fractional amounts show correct sub-unit words per currency. Whole numbers omit sub-unit phrase.

**Independent Test**: `1500.25 EGP` → "وخمسة وعشرون قرشاً" present. `2000.00 SAR` → no "هللة" phrase.

> Sub-unit logic is implemented inside `TafqeetConverter` (Phase 2). This phase adds verification test cases and frontend display confirmation.

- [X] T029 [US5] Extend `formcraft-backend/tests/services/test_tafqeet_converter.py` with explicit sub-unit parametrized test cases for all four currencies (EGP/SAR/AED/USD) at `.25`, `.50`, `.10`, `.00` — confirm T008 already covers these or add missing cases
- [X] T030 [US5] Verify end-to-end: enter `previewValue = 1500.25` in canvas with EGP currency → confirm sub-unit phrase appears in canvas text node (manual smoke test documented in `quickstart.md`)

**Checkpoint**: US5 verified. Sub-unit phrases appear for fractional amounts, absent for whole numbers, across all four currencies.

---

## Phase 8: User Story 6 — PDF Rendering with Filled Data (Priority: P1)

**Goal**: `POST /api/pdf/render/{template_id}` with filled data map resolves tafqeet from source element value, converts it, applies arabic-reshaper + python-bidi, and renders correctly in WeasyPrint.

**Independent Test**: Render PDF with `{"amount": "7350.00"}` where tafqeet is linked to `amount` (SAR). Open PDF — Arabic text flows RTL with correct ligatures. "Both" mode shows two lines. Missing source key → blank cell (no error).

- [X] T031 [US6] Write PDF integration test (FAILING) in `formcraft-backend/tests/api/test_pdf_tafqeet.py` — test: tafqeet with filled data renders non-blank, Arabic text present, null source key renders blank cell, both-mode produces two lines
- [X] T032 [US6] Implement `TafqeetRenderer` in `formcraft-backend/app/services/pdf/element_renderers/tafqeet_renderer.py` per `plan.md` — resolves source key from data map, calls `TafqeetConverter.convert()`, applies `apply_bidi()` to Arabic lines, sets `overflow: visible`, renders two `<p>` tags for "both" mode
- [X] T033 [US6] Register `TafqeetRenderer` in `RENDERER_MAP` in `formcraft-backend/app/services/pdf/element_renderers/__init__.py` — key `"tafqeet": TafqeetRenderer()`
- [X] T034 [US6] Add FR-009b audit logging in `TafqeetRenderer.render()` — on `TafqeetConverter.convert()` returning `None` due to exception (distinguish from intentional `None` for missing data), log `action="tafqeet.conversion_error"` to `AuditLogger` with `resource_id=element['key']` and `metadata={amount, currency_code, error}`

**Checkpoint**: US6 fully testable. PDF renders correctly for all cases: filled data, missing data, Arabic-only, both-mode, exception → blank + audit.

---

## Phase 9: User Story 7 — Edge Cases & Overflow Warning (Priority: P2)

**Goal**: Zero renders "صفر"/"Zero". Negative values show warning in property panel. Overflow warning shown when text height exceeds bounding box. Backend validates `sourceElementKey` type (FR-023).

**Independent Test**: Enter `previewValue = 0` → canvas shows "صفر". Enter `-500` → property panel shows warning, canvas stays blank. Resize element to 5mm height with long Arabic text → orange overflow warning appears.

- [X] T035 [US7] Write integration test (FAILING) in `formcraft-backend/tests/api/test_templates_tafqeet.py` — cover: saving tafqeet element with valid `sourceElementKey` returns 200; saving with `sourceElementKey` pointing to a non-number/currency element returns 422; saving with null `sourceElementKey` returns 200 (FR-023)
- [X] T036 [US7] Add backend validation in `formcraft-backend/app/api/routes/templates.py` (element save/update path) — if element type is `tafqeet` and `formatting.sourceElementKey` is set, verify the referenced key belongs to a `number` or `currency` element on the same page; return HTTP 422 if not (FR-023); ensure T035 tests pass
- [X] T037 [US7] Add negative value detection in `tafqeet-property-panel.component.ts` — if `previewValue < 0`, show inline warning "Negative values not supported" and skip preview API call
- [X] T038 [US7] Implement overflow warning (FR-026) in `tafqeet-property-panel.component.ts` — after each successful preview response, measure rendered text height against `element.height_mm * PX_PER_MM`; if text overflows, display orange mat-hint "Text may overflow — resize the element"
- [X] T039 [US7] Verify zero handling end-to-end: `previewValue = 0` → preview API returns `{"result": "صفر"}` (ar) / `{"result": "Zero"}` (en) — already covered by T008; confirm property panel and canvas display it correctly

**Checkpoint**: US7 fully testable. All edge cases handled gracefully with no unhandled exceptions.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: i18n keys, multi-select guard, Swagger docs, final integration smoke test.

- [X] T040 [P] Add i18n translation keys for all `TafqeetPropertyPanelComponent` labels in `formcraft-frontend/src/assets/i18n/ar.json` and `en.json` — keys: `tafqeet.source_element`, `tafqeet.output_language`, `tafqeet.show_currency`, `tafqeet.prefix`, `tafqeet.suffix`, `tafqeet.preview_value`, `tafqeet.overflow_warning`, `tafqeet.negative_warning`
- [X] T041 [P] Guard multi-select bulk type change in `formcraft-frontend/src/app/features/designer/designer-page/designer-page.component.ts` — exclude `tafqeet` elements from bulk type-change operations (FR-021)
- [X] T042 [P] Add OpenAPI tags and response examples to `formcraft-backend/app/api/routes/tafqeet.py` matching `contracts/tafqeet-api.json`
- [X] T043 Run full integration smoke test per `quickstart.md`: install deps → apply migration → start BE → start FE → drag tafqeet → link source → preview → render PDF → verify output

**Checkpoint**: All 43 tasks complete. Full smoke test passes.

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    └── Phase 2 (Foundational — TafqeetConverter)
            ├── Phase 3 (US1 — Canvas Toolbox)          [P] after Phase 2
            ├── Phase 4 (US2 — Source Linking)          [P] after Phase 2, uses TafqeetService
            ├── Phase 5 (US3 — Bilingual Output)        after Phase 4 (extends property panel)
            ├── Phase 6 (US4 — Prefix/Suffix)           after Phase 5 (extends property panel)
            ├── Phase 7 (US5 — Sub-unit Verification)   after Phase 2 (converter tests)
            └── Phase 8 (US6 — PDF Renderer)            [P] after Phase 2
Phase 9 (US7 — Edge Cases)                              after Phase 4 + Phase 8
Phase 10 (Polish)                                       after all story phases
```

### User Story Dependencies

| Story | Priority | Depends on | Can Parallel with |
|---|---|---|---|
| US1 | P1 | Phase 2 | US2, US5, US6 |
| US2 | P1 | Phase 2 | US1, US5, US6 |
| US3 | P1 | US2 (property panel exists) | — |
| US4 | P2 | US3 (property panel complete) | — |
| US5 | P1 | Phase 2 (converter) | US1, US2, US6 |
| US6 | P1 | Phase 2 (converter) | US1, US2, US5 |
| US7 | P2 | US2 + US6 | — |

### TDD Order (Within Each Phase)

1. Write test → confirm it **FAILS** → implement → confirm it **PASSES**
2. Applies to: T008 → T010, T011 → T012, T031 → T032, T035 → T036

---

## Parallel Opportunities

### Phase 1 — Run Together

```
T004  Add 'tafqeet' to frontend ElementType
T005  Add tafqeet to ELEMENT_DEFAULTS
T006  Create backend Pydantic schemas
T007  Create frontend Zod schema
```

### After Phase 2 — Run in Parallel (if staffed)

```
Backend Dev:   Phase 8 (US6 — PDF Renderer)  →  T031, T032, T033, T034
               Phase 9 (US7 — Edge Cases)    →  T035, T036
Frontend Dev:  Phase 3 (US1 — Canvas)         →  T014, T015, T016
               then Phase 4 (US2 — Linking)   →  T017..T022
```

### Phase 10 — All Polish Tasks in Parallel

```
T040  i18n keys
T041  Multi-select guard
T042  Swagger docs
```

---

## Implementation Strategy

### MVP (US1 + US2 + Core Converter)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (TafqeetConverter + preview endpoint)
3. Complete Phase 3: US1 — canvas toolbox
4. Complete Phase 4: US2 — source linking + preview
5. **STOP AND VALIDATE**: Drag tafqeet → link to amount → enter previewValue → canvas shows conversion
6. Deliver MVP — Designer can place and preview tafqeet elements

### Incremental Delivery

| Step | Stories | Value Delivered |
|---|---|---|
| MVP | US1 + US2 | Drag, link, and preview tafqeet on canvas |
| +US3 | +US3 | Bilingual output toggle works |
| +US5 | +US5 | Sub-unit verification confirmed |
| +US6 | +US6 | Full PDF export with tafqeet |
| +US4 | +US4 | Prefix/suffix formatting for cheques |
| +US7 | +US7 | Edge cases and overflow warnings |
| Polish | — | i18n, guard, docs, smoke test |

---

## Notes

- TDD is **mandatory** (Constitution §V) — T008 and T011 MUST fail before T010 and T012
- `tafqeet` element is read-only — no direct user text input on canvas
- `sourceElementKey` is a logical reference, not a DB FK — validated at API level (T035)
- Overflow is intentionally `visible` in PDF renderer — Designer responsibility (Clarification Q2)
- Canvas preview debounced 300ms (FR-019) — implement in `TafqeetService` using `debounceTime(300)`; total round-trip target is <500ms (debounce + API latency)
- `previewValue` is design-time only — never sent in PDF render data map
- Audit logging for conversion failures only (FR-027/028) — no per-conversion success log
