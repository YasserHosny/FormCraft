# Cross-Artifact Consistency Analysis: F051 Responsive Themes Mobile

**Date**: 2026-06-01 | **Artifacts**: spec.md, plan.md, tasks.md

## Coverage Matrix

### Spec Requirements → Plan Coverage

| Requirement | Plan Section | Status |
|-------------|-------------|--------|
| FR-001: Both themes responsive | Architecture: Responsive Strategy | COVERED |
| FR-002: 360px phone, 768px tablet | Architecture: Breakpoint definitions | COVERED |
| FR-003: No full-page horizontal scroll | Architecture: Data View Strategy | COVERED |
| FR-004: Shell controls accessible | Architecture: Shell Responsiveness | COVERED |
| FR-005: Touch-friendly navigation | Architecture: Shell Responsiveness | COVERED |
| FR-006: Touch-friendly sizing | Architecture: Responsive Strategy (logical properties) | COVERED |
| FR-007: Form Desk workflows | Architecture: Form Filling Strategy | COVERED |
| FR-008: Form fields readable | Architecture: Form Filling Strategy | COVERED |
| FR-009: Validation error guidance | Architecture: Form Filling Strategy (scrollIntoView) | COVERED |
| FR-010: Data-heavy views | Architecture: Data View Strategy | COVERED |
| FR-011: Table key columns preserved | Architecture: Data View Strategy (card layout) | COVERED |
| FR-012: Filters discoverable | Architecture: Data View Strategy (bottom sheet) | COVERED |
| FR-013: Dialogs fit viewport | Phase 1: T004 global dialog override | COVERED |
| FR-014: RTL/LTR support | Architecture: Logical properties + direction mixins | COVERED |
| FR-015: Long labels handled | Phase 8: T035 truncation + title attribute | COVERED |
| FR-016: Preserve auth/RBAC | Constitution Check: Security | COVERED |
| FR-017: Theme switch on mobile | Phase 8: T034 mobile theme switch | COVERED |
| FR-018: Preserve user state | Architecture: Form Filling Strategy + CSS-first approach | COVERED |
| FR-019: Unavailable pages hidden | Phase 6: T026 designer mobile guard | COVERED |
| FR-020: Coverage includes all modules | Phase 5 + Phase 6: all modules covered | COVERED |

### Spec User Stories → Task Coverage

| User Story | Tasks | Status |
|------------|-------|--------|
| US1: Core workflows on mobile | T017, T018, T025–T028, T030 | COVERED |
| US2: Shell navigation on mobile | T005–T012 | COVERED |
| US3: Form filling on mobile | T013–T016 | COVERED |
| US4: Responsive data views | T019–T024, T029 | COVERED |
| US5: RTL/LTR responsive | T031–T033 | COVERED |

### Spec Edge Cases → Task Coverage

| Edge Case | Task | Status |
|-----------|------|--------|
| Long labels/names exceeding width | T035 | COVERED |
| Large dialog on phone | T004, T035 | COVERED |
| Browser zoom / font size increase | Not explicitly tasked | GAP (minor) |
| On-screen keyboard hiding fields | Implicit via sticky action bar (T013, T014) | PARTIAL |
| Table/chart cannot collapse | T019–T023 (contained scroll) | COVERED |
| Orientation change | T035, T036 | COVERED |
| Theme switch on mobile | T034, T036 | COVERED |

## Gaps Identified

### Gap 1: Browser Zoom / Font Size (Minor)
**Spec Edge Case**: "Core workflows should remain readable and operable without fixed-height clipping" when zoom or font size increases.
**Impact**: Low — using relative units (rem, em) and viewport-relative sizing already handles this. No fixed-height containers are being introduced.
**Recommendation**: Add a note to T037 final validation to include a 150% zoom test pass. No dedicated task needed.

### Gap 2: On-Screen Keyboard (Minor)
**Spec Edge Case**: "The active field and submission/draft actions should not be permanently hidden or unreachable."
**Impact**: Low — the sticky action bar approach (T013, T014) uses `position: sticky; bottom: 0` which naturally sits above the virtual keyboard in modern mobile browsers. The `scrollIntoView` on validation error (T015) also helps.
**Recommendation**: Add to T016 Playwright test a note to verify field visibility when input is focused (Playwright's `page.keyboard` can simulate this). No dedicated task needed.

### Gap 3: Batch Queue Detail Pages (Minor)
**Spec**: FR-020 requires coverage of "representative pages from Desk."
**Plan/Tasks**: T029 covers batch list but not batch detail or batch error report.
**Impact**: Low — batch detail follows the same submission-detail pattern.
**Recommendation**: Extend T029 description to include `batch-detail.component.scss` and `batch-error-report.component.scss`.

## Consistency Issues

### Issue 1: Breakpoint Alignment (RESOLVED)
The classic theme had inconsistent breakpoints (599px, 768px, 959px). The plan normalizes these to shared mixins in Phase 1, and tasks T017, T019, T023 explicitly mention normalizing existing breakpoints. **No action needed.**

### Issue 2: Classic Shell Implementation Detail
The classic `app-shell.component.ts` uses an inline template (no separate `.html` file) and no separate `.scss` file. T011 correctly notes this and suggests adding styles via `styles:` array or creating a `.scss` file. **Recommendation**: Create `app-shell.component.scss` and add `styleUrls` — cleaner than inline styles for the volume of responsive CSS needed.

### Issue 3: New Theme Shell Parent Layout
The New theme uses a parent layout component that positions toolbar + sidebar + content. The sidebar overlay behavior (T007, T008) requires the parent to handle the backdrop and toggle state. **Recommendation**: Verify the parent layout component (likely in `ui-redesign.routes.ts` or a layout wrapper) is included in T007 scope.

## Duplications

No duplications found between spec, plan, and tasks. Each artifact serves its intended purpose:
- Spec: What and why (user-facing requirements)
- Plan: How (technical architecture and approach)
- Tasks: Ordered work items with exact file paths

## Quality Assessment

| Dimension | Score | Notes |
|-----------|-------|-------|
| Spec completeness | 9/10 | Comprehensive requirements, minor gaps in edge case coverage |
| Plan-spec alignment | 10/10 | Every FR mapped to a plan section |
| Task-plan alignment | 9/10 | Minor gap in batch detail coverage |
| Task ordering | 10/10 | Clean dependency chain, parallel tasks marked |
| Test coverage | 9/10 | Playwright tests for each phase, minor zoom/keyboard gap |
| RTL consideration | 10/10 | Dedicated phase, logical properties throughout |
| Constitution compliance | 10/10 | All applicable principles pass |

**Overall**: Ready for implementation. Three minor gaps identified — all addressable as notes on existing tasks without new work items.

## Recommendations

1. **Extend T029** to include batch-detail and batch-error-report SCSS files
2. **Add zoom test** to T037 final validation scope
3. **Verify parent layout** component in T007 scope for sidebar overlay behavior
4. **Create `app-shell.component.scss`** rather than inline styles for T011
