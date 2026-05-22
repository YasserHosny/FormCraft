# Research: Template Feedback

**Date**: 2026-05-17

## Research Questions

No NEEDS CLARIFICATION items. Research focused on separation from existing feedback system, element reference strategy, and real-time notification approach.

## Findings

### 1. Separation from Existing Feedback System

The existing `feedback_submissions` table (from features 001-014) is a GENERIC user feedback system (page_url based, with rich media). Template feedback is fundamentally different:

- Tied to template_id, version, page_number, element_key (not a URL)
- Has lifecycle (open → resolved)
- Has category taxonomy (bug, suggestion, question)
- Consumed by designers in Design Studio (not support team)

**Decision**: Create a SEPARATE `template_feedback` table. No modification to existing feedback_submissions. The two systems serve different audiences and workflows.

### 2. Element Reference Strategy

**Options**:
1. Store element_id (UUID FK) — breaks if element deleted
2. Store element_key (stable string identifier) — survives element recreation

**Decision**: Store `element_key` (string, nullable). The element key is a stable identifier within a template version (e.g., "national_id", "full_name"). If the element is deleted in a future version, the feedback is still meaningful — it shows what element existed at that version.

### 3. Status Lifecycle

Simple two-state model is sufficient for v1:
- `open` — newly submitted, unresolved
- `resolved` — designer has addressed or acknowledged

Future extension could add `in_progress`, `wont_fix`, `duplicate`. Keeping simple for initial release.

### 4. Notification to Designers

**Decision**: No real-time push for v1. Designers see feedback when they open the template. The feedback count badge on template cards in the library provides passive notification. Real-time (Supabase Realtime) can be added later if needed.

### 5. Audit Trail Integration

Use existing `audit_logs` table with new action types:
- `TEMPLATE_FEEDBACK_SUBMITTED` — metadata includes template_id, version, category
- `TEMPLATE_FEEDBACK_RESOLVED` — metadata includes feedback_id, resolver comment
