# Research: Feedback Threading & Replies

**Branch**: `014-feedback-threading` | **Phase**: 0

---

### 1. Real-Time Delivery Mechanism

**Decision**: Supabase Realtime (`postgres_changes`) for all live updates.

**Rationale**: SC-001 (reply visible in 1 s, no reload) and SC-002 (notification in ≤ 5 s) together make polling impractical — a ≤ 1 s polling interval would generate ~3,600 requests/hour per connected client. Supabase Realtime is already bundled with the existing `@supabase/supabase-js` client. No additional infrastructure is required. The Angular `FeedbackRealtimeService` subscribes to `postgres_changes` on `feedback_replies` and `feedback_notifications` tables, enabling push-based updates to both the admin thread view and the user notification badge.

**Alternatives considered**:
- Client-side polling (`interval()`): meets SC-002 at 5 s but cannot reliably meet SC-001 at 1 s without excessive request volume.
- Server-Sent Events (SSE) via FastAPI: one-directional push; avoids Supabase dependency but adds a new FastAPI streaming pattern not present in the codebase.

---

### 2. Migration Numbering

**Decision**: `011_create_feedback_replies.sql` — next sequential number after feature 013's `010_extend_feedback_rich_media.sql`.

**Rationale**: Follows the established `001…00N` sequential convention. Feature 014 depends on features 011 and 013.

---

### 3. `FeedbackReply.read_at` Dropped

**Decision**: No `read_at` column on `feedback_replies`. Admin unread state is tracked via the `has_unread_user_reply` boolean on `feedback_submissions`; user notification state is tracked via `FeedbackNotification.read_at`.

**Rationale**: Decided in `/speckit.clarify` session 2026-05-09. Per-reply `read_at` adds a scan cost per thread load and per read-clear operation without providing functionality needed for v1. The submission-level flag is faster (single boolean column read) and sufficient for the admin unread badge (FR-014/FR-015). The notification table already has a `read_at` field to track user interaction.

**Alternatives considered**: Per-reply `read_at` (deferred to future "seen at" receipts feature, out-of-scope in v1).

---

### 4. Unread Indicator Clearing (FR-015)

**Decision**: Automatic on admin thread expand — frontend fires `PATCH /api/admin/feedback/{id}/read` immediately when the thread panel opens; no explicit user gesture required.

**Rationale**: Decided in `/speckit.clarify` session 2026-05-09. Matches email-client and support-tool UX conventions (Intercom, Zendesk, Slack). The PATCH is a lightweight single-column UPDATE (`has_unread_user_reply = false`); debouncing is not needed.

---

### 5. Thread Pagination Strategy

**Decision**: `before_id` cursor — GET `/api/feedback/{id}/replies?limit=20&before_id=<uuid>` returns the 20 replies immediately older than the given reply ID. A "Load earlier messages" button triggers this call; scroll position is anchored to the current view (no jump).

**Rationale**: Decided in `/speckit.clarify` session 2026-05-09. Cursor-based pagination (keyset) is stable under concurrent inserts — unlike OFFSET pagination, new replies posted while the user is reading do not shift pages. `created_at DESC` indexed on `(feedback_id, created_at)` makes the cursor efficient.

**Alternatives considered**: OFFSET pagination (unstable under concurrent writes); infinite scroll (requires IntersectionObserver, more complex scroll-anchor management).

---

### 6. `/my-feedback` Angular Route Structure

**Decision**: New lazy-loaded `MyFeedbackModule` at route `/my-feedback`, registered in `app-routing.module.ts` behind `AuthGuard` only (no `RoleGuard` — all authenticated users, not just admins).

**Rationale**: Decided in `/speckit.clarify` session 2026-05-09. Mirrors the existing lazy-loaded pattern (`templates`, `designer`, `admin/feedback`). `AuthGuard` only: regular users must access this page; the admin-only `RoleGuard` must not be applied.

---

### 7. Supabase Realtime Channel Strategy

**Decision**: Two channel subscriptions per Angular session:
1. **Global notification channel** (always active for logged-in users): subscribes to `INSERT` on `feedback_notifications WHERE recipient_user_id = auth.uid()` — drives the notification badge count.
2. **Per-thread channel** (active only while a thread is open): subscribes to `INSERT` on `feedback_replies WHERE feedback_id = <current_id>` — drives live reply append in the open thread. Unsubscribed when the thread panel closes.

**Rationale**: Separating channels by scope avoids processing irrelevant events. The global channel is cheap (notification inserts are rare). The per-thread channel is scoped to a single submission and torn down on close, preventing memory/socket leaks.

**Alternatives considered**: Single global channel for all `feedback_replies` changes — would receive all admin activity regardless of current view; requires client-side filtering and creates unnecessary network traffic.

---

### 8. `reply_count` and `has_unread_user_reply` Update Strategy

**Decision**: Service-layer UPDATEs (no PostgreSQL triggers).

**Rationale**: The existing codebase uses service-layer mutations exclusively (no DB triggers). Maintaining this pattern keeps the mutation logic visible in Python and testable with pytest. The two UPDATE cases are:
- On user reply posted: `reply_count += 1`, `has_unread_user_reply = true` on the parent `feedback_submissions` row.
- On admin reply posted: `reply_count += 1` only (does not set the admin-unread flag — notifications serve that purpose).
- On admin thread expand: `has_unread_user_reply = false`.

**Alternatives considered**: PostgreSQL `AFTER INSERT` trigger on `feedback_replies` — consistent but adds invisible side effects and complicates testing.

---

### 9. Queued Notification Delivery on Login (SC-004)

**Decision**: On Angular app initialisation (post-auth), call `GET /api/notifications` to fetch all undelivered notifications (`delivered_at IS NULL`). The backend sets `delivered_at = NOW()` atomically during this GET response. Supabase Realtime handles live delivery for notifications that arrive while the user is active.

**Rationale**: SC-004 requires queued notifications delivered within 3 seconds of next login. A single REST call on startup is simpler and more reliable than waiting for the Realtime subscription to catch up with historical rows. The Realtime subscription then handles only new events — no overlap.

---

### 10. Admin Thread View: Reply Input Location

**Decision**: Reply input (textarea + Send button) rendered inside the expanded submission row in the admin dashboard, below the thread list — same panel, no modal or separate page.

**Rationale**: Keeps the admin workflow in one place: read thread and reply without context switching. Matches the spec's description "typing a reply in the admin dashboard" (US1). Consistent with how `FeedbackAdminComponent` currently uses expanded rows for detail views.
