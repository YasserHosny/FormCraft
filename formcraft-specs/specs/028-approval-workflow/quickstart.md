# Quickstart: Template Approval Workflow

**Feature**: 028-approval-workflow
**Date**: 2026-05-24

---

## Prerequisites

- FormCraft backend running (`formcraft-backend/`)
- FormCraft frontend running (`formcraft-frontend/`)
- Supabase instance with existing migrations applied (001–029)
- At least one organization with departments, designers, and branch_managers
- Approval workflow enabled in org settings

---

## Test Scenarios

### Scenario 1: Full Approval Lifecycle (P1 — MVP)

**Setup**: Org with approval_workflow_enabled=true, 1 Designer, 1 Branch Manager, 1 Admin.

1. Log in as Designer → create a template → add elements
2. Click "Submit for Review" → verify status becomes `submitted_for_review`
3. Verify template is read-only for Designer (cannot edit elements)
4. Log in as Branch Manager → open review queue
5. Find the submitted template → click to review
6. Add an overall comment → click "Reject"
7. Log in as Designer → open the rejected template
8. Verify rejection comment is visible with reviewer name and timestamp
9. Edit the template → click "Submit for Review" again
10. Log in as Branch Manager → approve the template
11. Log in as Admin → click "Publish"
12. Verify template is now available in Form Desk

**Expected**: Complete lifecycle works, each transition logged in audit trail.

### Scenario 2: Self-Review Prevention

1. Log in as a user who has both Designer and Branch Manager roles (or Admin)
2. Create a template → submit for review
3. Attempt to approve the template yourself
4. Verify: System prevents self-review with clear error message
5. Log in as a different reviewer → approve succeeds

**Expected**: Self-review blocked. Different reviewer required.

### Scenario 3: Designer Withdrawal

1. Log in as Designer → submit a template for review
2. Before any reviewer acts, click "Withdraw"
3. Verify: Template returns to draft, becomes editable
4. Verify: Withdrawal event appears in audit trail
5. Submit again → log in as reviewer → begin reviewing
6. Log in as Designer → attempt to withdraw
7. Verify: Withdrawal blocked (reviewer has seen it — optional: or allowed)

**Expected**: Withdrawal works before review, audit trail records it.

### Scenario 4: Approval Workflow Disabled

1. Log in as Admin → navigate to org settings
2. Disable "Approval Workflow"
3. Log in as Designer → create a template
4. Click "Publish" directly (no "Submit for Review" button visible)
5. Verify: Template goes directly from `draft → published`
6. Verify: No review record is created

**Expected**: Direct publish works when approval disabled.

### Scenario 5: Review Queue

1. Create 5 templates: 3 submitted_for_review, 1 approved, 1 rejected
2. Log in as Branch Manager → open review queue
3. Verify: Templates grouped by status
4. Verify: Filter by department works
5. Verify: Sort by days waiting works
6. Verify: Overdue templates highlighted (if any > threshold)

**Expected**: Queue shows correct grouping and filtering.

### Scenario 6: Element-Level Comments

1. Submit a template with 10 elements
2. Log in as reviewer → open template preview
3. Click on 3 specific elements → add a comment to each
4. Add 1 overall comment → reject
5. Log in as Designer → open rejected template
6. Verify: 3 elements show comment badges on canvas
7. Click each badge → verify correct comment appears
8. Verify: Overall comment also visible

**Expected**: Element-level comments anchored correctly.

### Scenario 7: Governance Dashboard

1. Put 10 templates through various review cycles (some approved, some rejected)
2. Log in as Admin → open governance dashboard
3. Verify: Pending count matches actual pending templates
4. Verify: Average turnaround time calculation is reasonable
5. Verify: Rejection rate percentage is accurate
6. Verify: Overdue count matches templates past threshold

**Expected**: Metrics match reality.

### Scenario 8: Review History Timeline

1. Put a template through 3 review cycles: submit→reject→edit→submit→reject→edit→submit→approve→publish
2. Open template's review timeline
3. Verify: All 8 events shown chronologically with correct actors and timestamps
4. Click "Export Audit Trail" → verify PDF contains complete timeline

**Expected**: Zero gaps in audit trail.

### Scenario 9: Default Reviewer Assignment

1. Log in as Admin → assign a default reviewer to "Retail Banking" department
2. Log in as Designer in "Retail Banking" → submit a template
3. Verify: Default reviewer is suggested in the queue (or notification — if implemented)
4. Verify: A different reviewer can still review it (not enforced)

**Expected**: Soft suggestion, not hard assignment.

### Scenario 10: Bilingual Display

1. Switch language to Arabic → navigate through approval workflow
2. Verify: All status labels, buttons, review comments render in Arabic with RTL
3. Submit → reject with Arabic comment → verify comment displays correctly
4. Export timeline → verify Arabic content in PDF

**Expected**: Full Arabic support throughout.

---

## API Smoke Tests

```bash
# Submit for review
curl -X POST -H "Authorization: Bearer $DESIGNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "submitted_for_review"}' \
  "$API/templates/$TEMPLATE_ID/transition"

# Review queue
curl -H "Authorization: Bearer $REVIEWER_TOKEN" \
  "$API/admin/review-queue?status=submitted_for_review"

# Reject with element comments
curl -X POST -H "Authorization: Bearer $REVIEWER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "rejected", "comment": "Fix layout", "element_comments": [{"element_key": "name_field", "comment": "Too narrow"}]}' \
  "$API/templates/$TEMPLATE_ID/transition"

# Withdraw
curl -X POST -H "Authorization: Bearer $DESIGNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "draft"}' \
  "$API/templates/$TEMPLATE_ID/transition"

# Governance metrics
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "$API/admin/review-queue/metrics"

# Review timeline
curl -H "Authorization: Bearer $ADMIN_TOKEN" \
  "$API/admin/review-queue/$TEMPLATE_ID/timeline"

# Set default reviewer
curl -X PUT -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"reviewer_id": "'$REVIEWER_ID'"}' \
  "$API/admin/departments/$DEPT_ID/default-reviewer"

# Direct publish (approval disabled)
curl -X POST -H "Authorization: Bearer $DESIGNER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "published"}' \
  "$API/templates/$TEMPLATE_ID/transition"

# Get reviews with element comments
curl -H "Authorization: Bearer $TOKEN" \
  "$API/templates/$TEMPLATE_ID/reviews"
```
