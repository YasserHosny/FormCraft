# Specification Analysis Report: F046 Digital Signatures

## Findings

| ID | Category | Severity | Location(s) | Summary | Recommendation |
|----|----------|----------|-------------|---------|----------------|
| A1 | Coverage Gap | MEDIUM | spec.md:NFR-003, tasks.md | 7-year audit retention (NFR-003) has no explicit task | Add a task to configure retention policy or document that existing audit_log retention covers signature_events |
| A2 | Coverage Gap | MEDIUM | spec.md:FR-007, tasks.md | FR-007 (prevent silent regeneration) is only partially covered by evidence service | Add a task to inject signature-status checks into submission/template update guards so signed submissions cannot be modified without explicit invalidation |
| A3 | Coverage Gap | MEDIUM | spec.md:FR-009, tasks.md | FR-009 requires recording events in "submission history and audit views" but T036 only mentions minimal integration | Expand T036 to explicitly integrate with existing `audit_logs` table and submission history service, not just frontend views |
| A4 | Coverage Gap | MEDIUM | spec.md:NFR-002, tasks.md | AES-256 at rest for JSONB evidence is mentioned but no explicit encryption task exists | Add a task for encrypting sensitive JSONB evidence fields before persistence (e.g., using existing crypto_service or PostgreSQL pgcrypto) |
| A5 | Inconsistency | LOW | plan.md, tasks.md | plan.md says evidence service does "PDF sealing via WeasyPrint" but evidence service should orchestrate, not replace, existing PDF service | Clarify that evidence service calls existing PDF renderer and appends certificate page; no new PDF engine is introduced |
| A6 | Underspecification | LOW | spec.md, tasks.md | FR-001 mentions "approval steps" but tasks focus almost entirely on submission workflows | Add at least one task (or clarify in T015/T017) for wiring signature workflows to approval steps via `approval_step_id` |
| A7 | Constitution | LOW | plan.md, tasks.md | Test-first is claimed PASS but no explicit frontend unit/component test tasks exist | Add frontend test tasks for workflow-config, signer-portal, and evidence-viewer components to fully satisfy Constitution V |

## Coverage Summary Table

| Requirement Key | Has Task? | Task IDs | Notes |
|-----------------|-----------|----------|-------|
| FR-001: Enable workflows | Yes | T001, T015, T017, T019 | Approval step wiring underspecified |
| FR-002: Identity verification | Yes | T004, T005, T018 | Covered by token, identity services, and public endpoints |
| FR-003: Internal/external signers | Yes | T005, T018 | Covered by identity service and public endpoints |
| FR-004: Ordered/parallel workflows | Yes | T001, T026, T027, T028 | Max 10 signers enforced in data model |
| FR-005: Track states | Yes | T001, T017, T018 | All states modeled in migration and transitions in service |
| FR-006: Evidence package | Yes | T006, T033, T034, T035, T037 | JSONB + Storage reference covered |
| FR-007: Prevent silent regeneration | Partial | T006 | Missing explicit guard tasks on submission update path |
| FR-008: Resend/cancel/expire/correct | Yes | T017, T021, T027 | Cancel and resend explicitly in tasks |
| FR-009: Record lifecycle events | Partial | T036 | Needs explicit audit_log table integration |
| FR-010: Arabic/English messages | Yes | T003, T043 | i18n keys planned |
| NFR-001: Under 5 seconds | Yes | T033, T034 | Performance implicitly covered by endpoint design |
| NFR-002: AES-256 encryption | Partial | T006 | Needs explicit encryption task for JSONB at rest |
| NFR-003: 7-year retention | No | — | No explicit retention policy task |
| NFR-004: Idempotent processing | Yes | T037 | Duplicate event guards planned |

## Constitution Alignment Issues

No CRITICAL constitution violations detected. All principles are addressed in plan.md Constitution Check with PASS or PASS WITH TASK REQUIREMENT. One LOW finding: frontend test tasks are missing, which slightly weakens the Test-First Development claim but does not block implementation since backend tests are comprehensive.

## Unmapped Tasks

No tasks are entirely unmapped. All tasks trace to at least one requirement or story.

## Metrics

- Total Requirements: 14 (10 FR + 4 NFR)
- Total Tasks: 43
- Coverage %: 100% of FRs have task coverage (2 are partial); 75% of NFRs have explicit task coverage (NFR-003 missing, NFR-002 partial)
- Ambiguity Count: 1 (approval step wiring)
- Duplication Count: 0
- Critical Issues Count: 0

## Next Actions

- **Recommended**: Resolve the 4 MEDIUM coverage gaps before `/speckit.implement` by editing `tasks.md` to add:
  1. A task for submission/template update guards (FR-007)
  2. A task for explicit `audit_logs` integration (FR-009)
  3. A task for evidence JSONB encryption at rest (NFR-002)
  4. A task for audit retention policy or a note that it is covered by existing infrastructure (NFR-003)
- **Optional**: Add frontend component test tasks to strengthen Constitution V compliance.
- **Proceed**: No CRITICAL issues block implementation.
