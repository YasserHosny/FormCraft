# Research: Template Approval Workflow

**Feature**: 028-approval-workflow
**Date**: 2026-05-24

---

## R1: Existing Backend Infrastructure

**Decision**: Extend the existing state machine and endpoints rather than building from scratch.

**Rationale**: The backend already has:
- `TRANSITION_MAP` in `template_service.py` with all approval states (draft, submitted_for_review, approved, rejected, published, archived, deprecated)
- `ROLE_TRANSITIONS` mapping who can perform each transition (designer, admin, branch_manager)
- `transition_status()` method with role checking, comment requirement for rejection, audit logging, and review record creation
- `template_reviews` table with reviewer_id, action, comment, created_at
- `POST /templates/:id/transition` endpoint accepting `TransitionRequest(status, comment)`
- `GET /templates/:id/reviews` endpoint returning review history
- `TemplateStatus` enum in `enums.py` with all 7 states
- `approval_workflow_enabled` field in org settings schema

**What needs to be added**:
- Withdrawal transition: `submitted_for_review → draft` by designer
- Direct publish shortcut: `draft → published` when approval disabled
- Self-review prevention logic
- Element-level comments on reviews
- Review queue query (filter/sort pending templates)
- Governance metrics computation
- Org settings enforcement of workflow toggle
- Default reviewer per department storage
- Frontend UI for all workflows

---

## R2: Approval-Disabled Shortcut Path

**Decision**: When `approval_workflow_enabled = false`, allow direct `draft → published` transition (add to TRANSITION_MAP conditionally).

**Rationale**: The existing TRANSITION_MAP only allows `draft → submitted_for_review`. When approval is disabled, we add a conditional `draft → published` path. This avoids creating fake review records or auto-passing through intermediate states. The transition service reads the org's `approval_workflow_enabled` setting before validating the transition.

**Implementation approach**: At transition time, if the target is `published` and the source is `draft`, check org settings. If approval is disabled and the actor is designer+, allow the direct shortcut. If approval is enabled, reject and require the review flow.

---

## R3: Element-Level Review Comments

**Decision**: Store element-level comments as JSONB array on the `template_reviews` table, keyed by element `key` (the stable identifier).

**Rationale**: Elements have a unique `key` field that persists across template edits (unlike `id` which is UUID-based). Using `key` ensures comments survive element modifications. The JSONB array approach avoids a separate join table for a feature that typically has 0–10 comments per review.

**Structure**: `element_comments: [{"element_key": "national_id", "comment": "Needs Arabic label"}, ...]`

**Alternatives considered**:
- Separate `review_comments` table — rejected as over-engineering for typically small comment counts (< 10 per review)
- Comments keyed by element_id (UUID) — rejected because element IDs can change if element is deleted and recreated

---

## R4: Review Queue Query Strategy

**Decision**: Live query against `templates` table filtered by `status = 'submitted_for_review'`, joined with `profiles` (designer name) and `departments` (department name).

**Rationale**: The review queue is a filtered view of the templates table, not a separate data structure. At typical organizational scale (< 500 templates, < 50 pending review), a direct query with appropriate indexes is performant. The existing `idx_templates_org_status` index (if present) or a new composite index supports this efficiently.

**Governance metrics**: Computed live from `template_reviews` table — average turnaround = AVG(review.created_at - template.submitted_at), rejection rate = COUNT(rejected) / COUNT(all decisions).

---

## R5: Self-Review Prevention

**Decision**: Compare `template.created_by` with `actor_id` at transition time. Block if they match and the transition is `submitted_for_review → approved/rejected`.

**Rationale**: Simple equality check. Uses `created_by` rather than "who submitted" because the designer who created the template is the one who needs independent review. Edge case: if an admin created the template, another admin can still review it (admins have review privileges).

---

## R6: Withdrawal Transition

**Decision**: Add `submitted_for_review → draft` to `TRANSITION_MAP` with `["designer", "admin"]` role permissions. Log as `TEMPLATE_WITHDRAWN` audit event.

**Rationale**: Allows designers to pull back templates they've submitted if they notice issues before a reviewer acts. The transition clears any pending state but does NOT delete the submission record from history (preserves audit trail).
