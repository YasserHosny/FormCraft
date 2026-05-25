# Research: Notification Center

**Feature**: 029-notification-center
**Date**: 2026-05-25

---

## R1: Generalized vs. Extending Existing Feedback Notifications

**Decision**: Create a NEW generalized `notifications` table and service. Migrate the existing F14 notification endpoints (`GET /notifications`, `PATCH /notifications/{id}/read`) to use the new table. Keep `feedback_notifications` table for backward compatibility but stop writing to it.

**Rationale**: The existing `feedback_notifications` table is tightly coupled to feedback threading — it has `feedback_id` and `reply_id` foreign keys that don't apply to template approval or system announcement notifications. A generalized table with `type`, `title_ar`, `title_en`, `body_ar`, `body_en`, and `action_url` supports all notification types without schema contortions.

**Migration strategy**: The new `notifications.py` route file takes over the `/api/notifications` URL prefix. The old `user_router` endpoints in `feedback.py` are removed and replaced with the new router. Existing `feedback_notifications` records can optionally be migrated to the new table via a data migration script, but this is not required for MVP — the old records simply become inaccessible through the new API.

---

## R2: Email Delivery Approach

**Decision**: Use Python's `smtplib` with `email.mime` for sending HTML emails, wrapped in an async background task (FastAPI `BackgroundTasks`). Email provider credentials stored in environment variables (`SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`, `SMTP_FROM`).

**Rationale**: Avoids adding a new dependency (SendGrid SDK, etc.) when standard SMTP works with any provider. The async background task approach ensures the API response is not blocked by email sending. For MVP, `BackgroundTasks` is sufficient — a proper job queue (Celery, etc.) can replace it later for retry/dead-letter handling.

**Alternatives considered**:
- SendGrid/Resend SDK — rejected to avoid vendor lock-in and additional dependency
- Celery job queue — over-engineering for MVP volume; can upgrade later
- Supabase Edge Functions for email — rejected as it moves logic outside the FastAPI app

---

## R3: Real-Time Notification Delivery (Polling vs SSE vs WebSocket)

**Decision**: Client-side polling via Angular `interval()` (every 30 seconds) hitting `GET /api/notifications/unread-count`. Full notification list fetched on bell click.

**Rationale**: Polling is the simplest approach with zero infrastructure changes. At 30s intervals with a lightweight count endpoint, the load is negligible (1 query per user per 30s). SSE or WebSocket would provide sub-second delivery but requires additional server infrastructure (long-lived connections, Supabase Realtime integration). The spec allows up to 5s delivery time, and polling at 30s exceeds this for worst-case — but in practice users click the bell frequently. The unread count endpoint is fast (<50ms) so the polling overhead is minimal.

**Upgrade path**: When real-time is needed, add Supabase Realtime subscription on the `notifications` table filtered by `recipient_id`. The frontend service already abstracts the data flow, so switching from polling to subscription is a local change.

---

## R4: Notification Recipient Resolution

**Decision**: Resolve recipients at event creation time using role and department queries. Store recipient list explicitly (one notification row per recipient) rather than broadcasting with filter-on-read.

**Rationale**: One row per recipient enables: individual read tracking, individual preference checking, individual email delivery tracking, and simple `WHERE recipient_id = :user_id` queries. The alternative (single event row with "broadcast to department X") would require complex read-time resolution and make read tracking difficult.

**Recipient resolution rules**:
| Event Type | Recipients |
|-----------|-----------|
| template_submitted_for_review | All branch_managers in template's department + all admins |
| template_approved | Template creator (designer) + all admins |
| template_rejected | Template creator (designer) |
| template_published | All operators in template's department |
| template_withdrawn | All branch_managers who were notified of submission |
| template_feedback_received | Template creator (designer) |
| template_feedback_resolved | Feedback submitter (operator) |
| draft_expiring | Draft owner (operator) |
| system_announcement | Targeted audience (all / role / department) |

---

## R5: Email Template Rendering

**Decision**: Use Jinja2 templates for HTML email rendering. Each notification type has a template file. A base template provides org branding (logo, colors, footer). Content is rendered in the recipient's preferred language.

**Rationale**: Jinja2 is already available in the Python ecosystem (used by FastAPI's template support). HTML email templates with org branding require dynamic content insertion (logo URL, primary color, event details, CTA link). Jinja2 handles this cleanly without adding a new rendering dependency.

**Template structure**: `base.html` provides the email wrapper (logo, color bar, footer with unsubscribe link). Event-specific templates extend the base and provide content blocks for title, body, and CTA button.

---

## R6: Notification Preferences Storage

**Decision**: Separate `notification_preferences` table with one row per user per notification type. Defaults inherited from org settings JSONB at user creation time. Missing preference rows fall back to org defaults.

**Rationale**: A separate table is cleaner than storing preferences in the user's profile JSONB (which would need schema-less validation). One row per type enables simple `WHERE user_id = :id AND notification_type = :type` lookups during notification creation. The fallback to org defaults means new notification types added in future work "just work" without requiring a migration of all user preference rows.

**Alternatives considered**:
- JSONB column on profiles — rejected because it becomes unwieldy with 9+ notification types and 2 channels each
- Single JSONB preferences row per user — workable but harder to query for specific type defaults
