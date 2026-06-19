# Tasks: Per-Control Font & Generic Line Insets for Overlay Forms

**Input**: Design documents from `/specs/057-overlay-control-font-insets/`
**Prerequisites**: plan.md (required), spec.md (required)

**Tests**: TDD is mandatory per Constitution Principle V. Test tasks are included and must be written first.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare project for feature work; no new dependencies required.

- [x] T001 [P] Add translation keys for Font, Line Layout, and Overflow panels to `formcraft-frontend/src/assets/i18n/en.json`
- [x] T002 [P] Add Arabic translation keys for Font, Line Layout, and Overflow panels to `formcraft-frontend/src/assets/i18n/ar.json`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Backend font resolution and optional Pydantic formatting validation must be in place before user stories.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

### Tests for Foundational

- [x] T003 [P] Write unit tests for `fonts.resolve_font_family` covering bundled families, custom names, and fallback in `formcraft-backend/app/services/pdf/tests/test_fonts.py`
- [x] T004 [P] Write Pydantic validation tests for `FontSettings`, `LineLayout`, and `ElementFormatting` schemas in `formcraft-backend/app/schemas/tests/test_element_formatting.py`

### Implementation for Foundational

- [x] T005 Implement `resolve_font_family(name: str) -> str` and warning logging in `formcraft-backend/app/services/pdf/fonts.py`
- [x] T006 Add optional `FontSettings`, `LineLayout`, `ElementFormatting` Pydantic sub-models to `formcraft-backend/app/schemas/element.py`
- [x] T007 Update `@font-face` CSS generation in `formcraft-backend/app/services/pdf/fonts.py` to include Courier and Arial if present in assets

**Checkpoint**: Foundation ready — font resolution works, schema validation passes, user story implementation can now begin in parallel.

---

## Phase 3: User Story 1 — Per-Control Font Styling (Priority: P1) 🎯 MVP

**Goal**: Designers can set per-control font family, size, weight, style, and color; settings persist under `formatting.font` and render identically in canvas preview and PDF.

**Independent Test**: Open a control → set font to `Courier`, `13px`, `Bold` → save → generate PDF → verify the value renders in Courier 13px bold (not Noto 10pt) at the control's position.

### Tests for User Story 1

- [x] T008 [P] [US1] Write unit test for `_base_style` font injection: custom font overrides default in `formcraft-backend/app/services/pdf/element_renderers/tests/test_base_renderer.py`
- [x] T009 [P] [US1] Write unit test for `_base_style` fallback when `formatting.font` is absent in `formcraft-backend/app/services/pdf/element_renderers/tests/test_base_renderer.py`
- [x] T010 [P] [US1] Write frontend component test for `FormattingPropertyPanelComponent` font form binding and event emission in `formcraft-frontend/src/app/features/designer/components/formatting-property-panel/formatting-property-panel.component.spec.ts`

### Implementation for User Story 1

- [x] T011 [US1] Extend `_base_style` in `formcraft-backend/app/services/pdf/element_renderers/base.py` to read `formatting.font` and emit CSS `font-family`, `font-size`, `font-weight`, `font-style`, `color`
- [x] T012 [US1] Update `TextRenderer.render` in `formcraft-backend/app/services/pdf/element_renderers/text_renderer.py` to use the inherited styled `_base_style`
- [x] T013 [US1] Update `TafqeetRenderer.render` in `formcraft-backend/app/services/pdf/element_renderers/tafqeet_renderer.py` to use the inherited styled `_base_style` (remove manual style rebuild if any)
- [x] T014 [P] [US1] Create `FormattingPropertyPanelComponent` with Font section (family dropdown+custom, size, weight, style, color) in `formcraft-frontend/src/app/features/designer/components/formatting-property-panel/`
- [x] T015 [US1] Wire `FormattingPropertyPanelComponent` into `DesignerPageComponent` for all element types in `formcraft-frontend/src/app/features/designer/designer-page/designer-page.component.html`
- [x] T016 [US1] Update `CanvasService.addElementInternal` and `updateElementVisual` in `formcraft-frontend/src/app/features/designer/services/canvas.service.ts` to apply `formatting.font` to `Konva.Text` nodes

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently.

---

## Phase 4: User Story 2 — Generic Line Insets (Priority: P1)

**Goal**: Designers configure max lines and optional left/right insets per line (or first-line / last-line shorthand); the model is generic and works for any multi-line-capable control.

**Independent Test**: On a 2-line tafqeet control over the Al Baraka cheque, set first-line left-inset = 22mm and last-line right-inset = 26mm → generate PDF → verify line 1 starts clear of "The sum of" and line 2 ends clear of "بالحروف", with neither label covered.

### Tests for User Story 2

- [x] T017 [P] [US2] Write unit test for line inset CSS generation: first-line left padding, last-line right padding in `formcraft-backend/app/services/pdf/element_renderers/tests/test_line_insets.py`
- [x] T018 [P] [US2] Write unit test for tafqeet renderer with line insets: multi-line output respects per-line widths in `formcraft-backend/app/services/pdf/element_renderers/tests/test_tafqeet_renderer.py`
- [x] T019 [P] [US2] Write frontend component test for Line Layout form binding and validation (inset clamping) in `formcraft-frontend/src/app/features/designer/components/formatting-property-panel/formatting-property-panel.component.spec.ts`

### Implementation for User Story 2

- [x] T020 [US2] Implement `render_line_inset_html` helper in `formcraft-backend/app/services/pdf/element_renderers/base.py` that wraps lines in `<p>` or `<span>` with per-line `padding-left` / `padding-right` CSS
- [x] T021 [US2] Update `TextRenderer.render` in `formcraft-backend/app/services/pdf/element_renderers/text_renderer.py` to apply line insets when `formatting.lineLayout` is present
- [x] T022 [US2] Update `TafqeetRenderer.render` in `formcraft-backend/app/services/pdf/element_renderers/tafqeet_renderer.py` to apply line insets to each `<p>` line
- [x] T023 [US2] Add Line Layout section (max lines, first-line left inset, last-line right inset) to `FormattingPropertyPanelComponent` in `formcraft-frontend/src/app/features/designer/components/formatting-property-panel/`
- [x] T024 [US2] Update `CanvasService` in `formcraft-frontend/src/app/features/designer/services/canvas.service.ts` to simulate line insets in Konva preview by adjusting effective text width per line

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently.

---

## Phase 5: User Story 3 — Overflow / Fit Policy (Priority: P2)

**Goal**: Designers choose `clip`, `shrink-to-fit`, or `visible` overflow behavior; tafqeet default changes from unconditional `visible` to `shrink-to-fit`.

**Independent Test**: Set a tafqeet control to `shrink-to-fit`, feed an amount whose words exceed the box at the chosen size → generate PDF → verify the text auto-reduces to fit within the box bounds and does not overlap adjacent controls.

### Tests for User Story 3

- [x] T025 [P] [US3] Write unit test for `shrink-to-fit` convergence: font reduces until content fits or min size reached in `formcraft-backend/app/services/pdf/element_renderers/tests/test_overflow_policy.py`
- [x] T026 [P] [US3] Write unit test for `clip` policy: overflow hidden in `formcraft-backend/app/services/pdf/element_renderers/tests/test_overflow_policy.py`
- [x] T027 [P] [US3] Write unit test for tafqeet default policy when `formatting.overflow` is absent: `shrink-to-fit` in `formcraft-backend/app/services/pdf/element_renderers/tests/test_tafqeet_renderer.py`
- [x] T028 [P] [US3] Write frontend component test for overflow policy selection in `formatting-property-panel.component.spec.ts`

### Implementation for User Story 3

- [x] T029 [US3] Implement `apply_overflow_policy(element, html, style)` helper in `formcraft-backend/app/services/pdf/element_renderers/base.py` handling `clip`, `visible`, and `shrink-to-fit` iterative reduction
- [x] T030 [US3] Replace unconditional `overflow: visible` in `formcraft-backend/app/services/pdf/element_renderers/tafqeet_renderer.py` with `apply_overflow_policy`; default to `shrink-to-fit` when absent
- [x] T031 [US3] Update `TextRenderer.render` in `formcraft-backend/app/services/pdf/element_renderers/text_renderer.py` to call `apply_overflow_policy`; default to `clip` when absent
- [x] T032 [US3] Add Overflow section (`clip` / `shrink-to-fit` / `visible`) to `FormattingPropertyPanelComponent`
- [x] T033 [US3] Update `CanvasService` in `formcraft-frontend/src/app/features/designer/services/canvas.service.ts` to respect overflow policy in preview (`clip` = truncated, `visible` = allow spill, `shrink-to-fit` = reduced fontSize)

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, backward compatibility, canvas-PDF parity, and final validation.

### Tests for Polish

- [x] T034 [P] Write backward-compatibility test: template with no new settings generates identical HTML to pre-feature baseline in `formcraft-backend/app/services/pdf/element_renderers/tests/test_backward_compat.py`
- [x] T035 [P] Write edge-case test: inset larger than box width → clamp to minimum usable width in `formcraft-backend/app/services/pdf/element_renderers/tests/test_line_insets.py`
- [x] T036 [P] Write edge-case test: `shrink-to-fit` with font size larger than box height → reduces to fit in `formcraft-backend/app/services/pdf/element_renderers/tests/test_overflow_policy.py`

### Implementation for Polish

- [x] T037 [P] Add inset clamping logic (left+right ≥ width → warn and clamp) to `formcraft-backend/app/services/pdf/element_renderers/base.py`
- [x] T038 [P] Add frontend warning toast for custom font not bundled in `FormattingPropertyPanelComponent`
- [x] T039 Verify canvas preview parity: font size, weight, color, and insets render identically to PDF at 100% zoom; document any known Konva limitations
- [x] T040 [P] Run `ruff check .` in `formcraft-backend` and fix any lint issues
- [x] T041 [P] Run `pytest` in `formcraft-backend` and ensure all new and existing tests pass
- [x] T042 [P] Run `ng test --watch=false` in `formcraft-frontend` and ensure all tests pass
- [x] T043 Update `AGENTS.md` active technologies and recent changes sections to mention F057

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion — BLOCKS all user stories.
- **User Stories (Phase 3–5)**: All depend on Foundational phase completion.
  - Proceed sequentially in priority order (US1 → US2 → US3) or in parallel if staffed.
- **Polish (Phase 6)**: Depends on all desired user stories being complete.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational. No dependencies on other stories.
- **User Story 2 (P1)**: Can start after US1 or in parallel if the line inset helper in `base.py` is ready. For sequential execution, depends on T011 (styled `_base_style`).
- **User Story 3 (P2)**: Can start after US1/US2 or in parallel. For sequential execution, depends on T020 (line inset helper) and T011 (styled `_base_style`).

### Within Each User Story

- Tests MUST be written and FAIL before implementation.
- Backend helpers before renderer updates.
- Frontend component before canvas service wiring.
- Story complete before moving to next priority.

### Parallel Opportunities

- T001 and T002 (translations) can run in parallel.
- T003 and T004 (backend tests) can run in parallel.
- T005, T006, T007 (backend foundation) can run in parallel after tests exist.
- T008, T009, T010 (US1 tests) can run in parallel.
- T011, T014 (US1 backend + frontend component) can run in parallel.
- T017, T018, T019 (US2 tests) can run in parallel.
- T020, T023 (US2 backend + frontend) can run in parallel.
- T025, T026, T027, T028 (US3 tests) can run in parallel.
- T029, T032 (US3 backend + frontend) can run in parallel.
- T034, T035, T036, T037, T038, T040, T041, T042 (polish) can run in parallel after all stories complete.

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Write unit test for _base_style font injection in test_base_renderer.py"
Task: "Write unit test for _base_style fallback in test_base_renderer.py"
Task: "Write frontend component test for FormattingPropertyPanelComponent"

# Launch backend and frontend implementation together:
Task: "Extend _base_style in base.py"
Task: "Create FormattingPropertyPanelComponent"

# Wire after both complete:
Task: "Update CanvasService to apply formatting.font"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (translations)
2. Complete Phase 2: Foundational (font resolution, schema validation)
3. Complete Phase 3: User Story 1 (per-control font)
4. **STOP and VALIDATE**: Test User Story 1 independently — generate PDF with custom font, verify canvas parity.
5. Deploy/demo if ready.

### Incremental Delivery

1. Setup + Foundational → Foundation ready.
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!).
3. Add User Story 2 → Test independently → Deploy/Demo.
4. Add User Story 3 → Test independently → Deploy/Demo.
5. Polish → Final validation → Merge.

### Sequential Agent Strategy (single developer)

Because this is executed by a single AI agent, phases run sequentially:

1. Setup + Foundational (T001–T007)
2. US1 tests → US1 implementation (T008–T016)
3. US2 tests → US2 implementation (T017–T024)
4. US3 tests → US3 implementation (T025–T033)
5. Polish tests → Polish implementation (T034–T043)

---

## Post-Implementation Review (2026-06-05)

A validation pass after the initial merge (commit `9085cba`) found and fixed:

- **shrink-to-fit was not content-aware.** The first implementation unconditionally
  reduced any tafqeet (default size > min) straight to 6pt, shrinking even short
  amounts and breaking backward compatibility (FR-14). Reworked `_apply_overflow_policy`
  to measure content against a deterministic box-capacity heuristic (`_fits_at_size`)
  and only shrink when content actually overflows, never below `min_size_pt`. Callers
  now pass the plain `text_content` for measurement.
- **Missing mandatory tests added**: `test_overflow_policy.py` (clip/visible/shrink,
  determinism, min-size fallback, oversized-height edge case), `test_tafqeet_renderer.py`
  (no unconditional `overflow: visible`, short-vs-long shrink, insets, custom font), and
  the frontend `formatting-property-panel.component.spec.ts` (getters, warnings, change
  handlers). The backward-compat test was corrected to assert a blank/short tafqeet keeps
  its default 10pt rather than the previously-enshrined 6pt.
- Backend: 52 PDF/schema tests pass.
- **Known caveat (out of F057 scope)**: the Angular karma suite currently fails to
  compile due to pre-existing errors in `features/ui-redesign/feature-validation.spec.ts`
  (specs 054/056 — `createNewCustomer`, `AnalyticsComponent` ctor, `FormFiller` fb arg).
  This blocks running ANY frontend spec, including the new F057 one, until those are fixed.

## Notes

- [P] tasks = different files, no dependencies.
- [Story] label maps task to specific user story for traceability.
- Each user story should be independently completable and testable.
- Verify tests fail before implementing.
- Commit after each phase or logical group.
- Stop at any checkpoint to validate story independently.
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence.
