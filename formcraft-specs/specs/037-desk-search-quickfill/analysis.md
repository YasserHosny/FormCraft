## Specification Analysis Report: F037 - Desk Search & Quick Fill

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| C1 | Constitution | CRITICAL | tasks.md:Phase 2–4 | Constitution V (Test-First Development) violated: test tasks (T015–T016, T025–T026, T036–T038) are scheduled alongside or after implementation, not before. | Restructure phases so that for each service/component, the failing test task is created and executed BEFORE the implementation task. E.g., T011a: write failing test for search_global → T011b: implement search_global. |
| C2 | Constitution | CRITICAL | tasks.md:Phase 3–4 | Constitution VII (Translation-Key Architecture) violated: no tasks require adding i18n translation keys for new UI strings in GlobalSearchBarComponent or QuickFillDialogComponent. | Add translation-key tasks: create translation entries for search placeholder, section headers, Quick Fill button labels, "Save to Profile", empty/loading states, etc. |
| H1 | Coverage Gap | HIGH | plan.md:Phase 2.1, tasks.md | Materialized view refresh mechanism is mentioned in plan (5-min cron/trigger) but no task covers implementing the refresh job, cron schedule, or Supabase cron extension setup. | Add task T0xx: "Implement materialized view refresh strategy using pg_cron or trigger-based refresh in `037_desk_search_quickfill.sql`" |
| H2 | Coverage Gap | HIGH | spec.md:FR-007, tasks.md:T034 | `customer_id` FK added to `form_submissions`, but no task addresses backfill logic, nullable migration safety, or ensuring existing submissions remain valid. | Add explicit task: "Verify nullable `customer_id` migration is safe and does not break existing submission queries or RLS policies" |
| H3 | Coverage Gap | HIGH | spec.md:FR-004, tasks.md | Reference number exact match bypasses materialized view (good), but no task implements the direct table query or verifies its performance/RLS compliance. | Add task T0xx: "Implement exact reference number query in `search_service.py` with RLS filtering and index verification" |
| M1 | Inconsistency | MEDIUM | spec.md, plan.md, tasks.md | Terminology drift: spec uses "Quick Fill" (with space), tasks use `quickfill` (no space) and `QuickFill`. Pick one canonical form and normalize. | Normalize to "QuickFill" in code identifiers and "Quick Fill" in UI labels. Update all files consistently. |
| M2 | Underspecification | MEDIUM | spec.md:Edge Cases | Edge case "How does search ranking work when a query matches both a template name and a customer name?" is answered in clarifications but not enforced in backend implementation or tests. | Add task to verify ranking order in `test_search_service.py`: templates rank first, then customers, then submissions. |
| M3 | Underspecification | MEDIUM | contracts/api-contracts.md | `GET /search` response shape includes `metadata` as `{}` but no schema constraints or example values for each entity type. | Expand contract to include `SearchResultTemplateMetadata`, `SearchResultSubmissionMetadata`, `SearchResultCustomerMetadata` Pydantic/Zod schemas. |
| M4 | Coverage Gap | MEDIUM | tasks.md:Phase 5 | Accessibility tasks are lumped into a single late task (T044); ARIA labels, keyboard traps, and focus management should be built into component creation tasks (T021, T030), not bolted on later. | Split T044 into per-component accessibility tasks (T021b, T030b) or add acceptance criteria to component tasks. |
| L1 | Redundancy | LOW | tasks.md:Phase 2 | T011 and T012 are marked [P] (parallel) but both depend on the migration being applied. Parallel is only safe after T014. | Remove [P] from T011–T012 until after T014, or reorder so migration applies before parallel service implementation. |

---

## Coverage Summary Table

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|
| FR-001 Global search bar | Yes | T006–T010, T017, T021–T024 | Covered |
| FR-002 Results < 300ms | Partial | T002 (debounce), T039 (benchmark) | Missing explicit indexing/performance tasks for 300ms guarantee |
| FR-003 Grouped by type | Yes | T017, T022 | Covered |
| FR-004 Reference number direct nav | Yes | T018, T020 | Missing exact query RLS task (H3) |
| FR-005 Quick Fill mode | Yes | T027–T035 | Covered |
| FR-006 Visual distinction + editable | Yes | T034 | Covered |
| FR-007 Link submission to customer | Yes | T034 | Covered |
| FR-008 Mixed Arabic/English | Yes | T009, T041 | Covered |
| FR-009 Customer search fields | Yes | T027, T030 | Covered |
| FR-010 Configurable mapping | Yes | T007, T012–T013 | Covered |
| FR-011 Save to Profile | Yes | T035 | Covered |
| SC-001 < 300ms latency | Yes | T039 | Benchmark task exists |
| SC-002 50% time reduction | Partial | No explicit measurement task | Add task to measure before/after form completion time |
| SC-003 95%+ mapping accuracy | Partial | No explicit accuracy test | Add unit test task to verify mapping accuracy against sample templates |
| SC-004 < 5s reference find | Partial | T020 | No explicit benchmark task; T026 integration test covers flow but not timing |
| SC-005 50 concurrent queries | Yes | T039 | Load test task needed; currently only latency benchmark |

---

## Constitution Alignment Issues

1. **Test-First (V)**: Tasks must be reordered to create failing tests before implementation. Current plan risks "tests after code" anti-pattern.
2. **Translation-Key (VII)**: All new UI components must include i18n key extraction tasks. Missing for search and quick-fill.
3. **Security & Auditability (VIII)**: Quick Fill creates a new submission linked to a customer. No audit log task covers this data linkage event. Add audit trail entry for `submission_customer_linked`.

---

## Unmapped Tasks

- T042 (recent searches cache) — nice-to-have, not tied to any requirement. Consider marking as stretch/MVP-excluded.
- T043 (loading/empty states) — should be part of component acceptance criteria, not a standalone task.
- T047 (update AGENTS.md) — housekeeping; keep but lower priority.

---

## Metrics

- Total Requirements: 11 functional + 5 success criteria = 16
- Total Tasks: 48
- Coverage %: ~85% (requirements with >=1 task)
- Ambiguity Count: 2 (ranking order, metadata schema)
- Duplication Count: 1 (terminology drift)
- Critical Issues Count: 2 (C1, C2)

---

## Next Actions

1. **CRITICAL**: Fix C1 and C2 before implementation — restructure tasks to put tests first and add i18n translation tasks.
2. **HIGH**: Add tasks for materialized view refresh (H1) and exact reference query (H3).
3. **MEDIUM**: Normalize terminology (M1) and expand API contract schemas (M3).
4. Once issues C1–H3 are resolved, the plan is safe to execute via `/speckit.implement`.

---

## Remediation

Would you like me to suggest concrete remediation edits for the top issues? Key fixes needed:
- Reorder Phase 2–4 tasks to enforce TDD (test → implement → refactor)
- Add i18n translation key tasks for all new UI strings
- Add materialized view refresh implementation task
- Normalize QuickFill vs Quick Fill terminology
