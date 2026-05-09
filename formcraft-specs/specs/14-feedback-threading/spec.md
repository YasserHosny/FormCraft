# Feature Specification: Feedback Threading & Replies

**Feature Branch**: `014-feedback-threading`  
**Created**: 2026-05-07  
**Status**: Draft  
**Depends on**: Feature 011 (Customer Feedback) — submission pipeline and admin dashboard must exist  
**Input**: Deferred from feature 011 out-of-scope: "Feedback threading or replies from the team back to the user"

## User Scenarios & Testing *(mandatory)*

### User Story 1 – Admin Replies to Feedback (Priority: P1)

An admin reviewing a feedback submission wants to respond directly to the submitter — acknowledging the issue, asking a follow-up question, or sharing a resolution. They type a reply in the admin dashboard and post it. The reply is attached to the submission thread.

**Why this priority**: The ability for admins to reply is the foundation of two-way communication. User-visible replies (P2) and notifications (P3) depend on this capability existing first.

**Independent Test**: Can be tested by posting a reply as an admin on any submission and verifying the reply appears in the submission thread in the dashboard.

**Acceptance Scenarios**:

1. **Given** an admin viewing an expanded feedback submission, **When** they type a reply and click Send, **Then** the reply is saved and appended to the thread beneath the submission.
2. **Given** an admin who has posted a reply, **When** they view the thread, **Then** the reply shows the admin's name, timestamp, and text content.
3. **Given** an admin, **When** they post multiple replies on the same submission, **Then** all replies appear in chronological order in the thread.
4. **Given** an admin, **When** they attempt to post an empty reply, **Then** submission is blocked and a validation message is shown.
5. **Given** a non-admin user, **When** they access the admin dashboard, **Then** they cannot view or post replies (admin dashboard remains inaccessible per FR-016 from feature 011).

---

### User Story 2 – Users View Their Feedback History and Replies (Priority: P2)

A user who submitted feedback previously wants to check whether the team has responded. They navigate to a "My Feedback" page that lists all their past submissions with their current status and any admin replies. They can read the thread and post a follow-up message.

**Why this priority**: Admin replies (P1) must exist before there is anything for users to read. This story closes the feedback loop by making replies visible to submitters.

**Independent Test**: Can be tested by submitting feedback as a regular user, posting an admin reply, then logging in as the submitter and verifying the reply is visible on the "My Feedback" page.

**Acceptance Scenarios**:

1. **Given** a logged-in user, **When** they navigate to "My Feedback", **Then** they see a list of all their past submissions ordered by most recent, with status and submission date.
2. **Given** a user on "My Feedback", **When** they expand a submission, **Then** they see the original submission content and any admin replies in chronological order.
3. **Given** a user reading a thread with an admin reply, **When** they type a follow-up message and click Send, **Then** the message is appended to the thread and visible to the admin in the dashboard.
4. **Given** a user with no past submissions, **When** they navigate to "My Feedback", **Then** an empty-state message is shown inviting them to submit their first feedback.
5. **Given** a user, **When** they view "My Feedback", **Then** they can only see their own submissions; other users' feedback is never shown.

---

### User Story 3 – In-App Notifications for Thread Activity (Priority: P3)

Both sides of a conversation need to know when the other party has responded. Users are notified in-app when an admin posts a reply; admins see a visual indicator on submissions with new unread user messages.

**Why this priority**: Notifications are only meaningful once both parties can reply (P1 + P2). They improve response rates but are not required for the core threading flow to function.

**Independent Test**: Can be tested by posting an admin reply while the submitting user is logged in and verifying an in-app notification appears in their session within 5 seconds. Then posting a user follow-up and verifying the admin dashboard marks the submission as having unread messages.

**Acceptance Scenarios**:

1. **Given** a logged-in user whose submission has just received an admin reply, **When** the reply is posted, **Then** an in-app notification appears in the user's current session within 5 seconds.
2. **Given** a user who clicks the notification, **When** they are taken to "My Feedback", **Then** the relevant submission is expanded and the new reply is visible.
3. **Given** an admin on the feedback dashboard, **When** a user has posted a follow-up message that the admin has not yet read, **Then** a visual indicator (e.g., unread badge) marks that submission.
4. **Given** an admin who opens the submission thread and reads the new message, **When** they view the dashboard list, **Then** the unread indicator is cleared for that submission.
5. **Given** a logged-in user who is not currently active in the app, **When** an admin reply arrives, **Then** no email or push notification is sent; the notification is held for their next session.

---

### Edge Cases

- What if the user is not logged in when a reply arrives? → Notification is queued and shown on their next login; it does not expire.
- What if an admin posts a reply to a deleted or non-existent submission? → Return a 404 error; no reply is saved.
- What if the thread becomes very long? → Display the most recent 20 messages and load older messages on demand ("Load earlier messages").
- What if a reply exceeds the character limit? → Block posting and show an inline character count with the limit.

## Requirements *(mandatory)*

### Functional Requirements

#### Admin Replies (User Story 1)

- **FR-001**: System MUST allow admins to post text replies (max 2000 characters) on any feedback submission via the admin dashboard.
- **FR-002**: System MUST display replies in chronological order within the submission thread, each showing author name, role (Admin / User), and timestamp.
- **FR-003**: System MUST block posting of an empty reply and display a validation message.
- **FR-004**: Reply threads MUST be visible only to the submitting user and admins; other users MUST NOT see threads on submissions they did not create.

#### My Feedback & User Replies (User Story 2)

- **FR-005**: System MUST provide authenticated users with a "My Feedback" page at route `/my-feedback`, listed as a top-level nav item in the main sidebar/header, showing all their past submissions ordered by most recent with status and date.
- **FR-006**: Each submission on "My Feedback" MUST be expandable to show full text content and the complete reply thread.
- **FR-007**: System MUST allow users to post follow-up text messages (max 2000 characters) on any thread on their own submissions.
- **FR-008**: User follow-up messages MUST appear in the admin dashboard thread and be distinguishable from admin replies (e.g., different label or colour).
- **FR-009**: Users MUST only be able to view and reply to their own submissions; the "My Feedback" page MUST never display other users' feedback.
- **FR-010**: When a thread contains more than 20 messages, only the 20 most recent are shown by default. A "Load earlier messages" button MUST appear at the top of the thread; clicking it fetches the next page of older messages using a `before_id` cursor parameter, with scroll position anchored to the current view (no jump).

#### In-App Notifications (User Story 3)

- **FR-011**: System MUST deliver an in-app notification to a submitting user's active session within 5 seconds of an admin posting a reply to their submission.
- **FR-012**: Notification MUST link directly to the relevant thread on the "My Feedback" page.
- **FR-013**: If the user is not in an active session when the reply arrives, the notification MUST be queued and displayed on their next login; it MUST NOT expire.
- **FR-014**: Admin dashboard MUST display a visual unread indicator on submissions that contain user follow-up messages the admin has not yet read.
- **FR-015**: The unread indicator MUST be cleared automatically when the admin expands the submission thread — no explicit "Mark as read" action required. The frontend fires a PATCH to clear `has_unread_user_reply` on the `feedback_submissions` row as soon as the thread panel opens.
- **FR-016**: System MUST NOT send email or push notifications; in-app delivery only.

### Key Entities

- **FeedbackReply**: Represents one message in a submission thread. Attributes: id, feedback_id, author_id, author_role (admin / user), text_content (max 2000 chars), created_at. No per-reply `read_at` field — unread state is tracked at the submission level via `has_unread_user_reply` on `FeedbackSubmission` (admin-side) and at the notification level via `FeedbackNotification.read_at` (user-side).
- **FeedbackNotification**: Represents a queued in-app notification. Attributes: id, recipient_user_id, feedback_id, reply_id, created_at, delivered_at (nullable), read_at (nullable).
- **FeedbackSubmission** (existing, from feature 011): Extended with a `reply_count` denormalised counter and `has_unread_user_reply` flag for admin dashboard performance.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An admin reply posted on a submission is visible in the admin thread within 1 second without a page reload.
- **SC-002**: An in-app notification for an admin reply reaches the submitting user's active session within 5 seconds of posting.
- **SC-003**: The "My Feedback" page loads a user's full submission history within 2 seconds for up to 500 past submissions.
- **SC-004**: Queued notifications (for offline users) are delivered within 3 seconds of the user's next login.
- **SC-005**: Zero reply messages are lost after the sender receives a send confirmation.

## Assumptions

- In-app notifications and live thread updates use **Supabase Realtime** (WebSocket) — Angular subscribes to `postgres_changes` on the `feedback_replies` and `feedback_notifications` tables. This satisfies SC-001 (1 s, no reload) and SC-002 (5 s notification delivery) with no polling overhead and no additional infrastructure beyond the existing Supabase client.
- Reply threads are visible to the submitting user and admins only; they are not visible to other authenticated users.
- There is no moderation or editing of posted replies in v1 — once sent, a reply cannot be edited or deleted.
- The "My Feedback" page is accessible at route `/my-feedback` as a top-level nav item in the main sidebar/header for all authenticated users.
- The `has_unread_user_reply` flag on FeedbackSubmission is updated server-side on each user reply and cleared when the admin reads the thread, to avoid expensive per-request counts.

## Clarifications

### Session 2026-05-09

- Q: What real-time mechanism should be used for live thread updates and in-app notifications? → A: Supabase Realtime (WebSocket) — subscribe to `postgres_changes` on `feedback_replies` and `feedback_notifications` tables; satisfies SC-001 (1 s) and SC-002 (5 s) with no polling overhead.
- Q: Should `FeedbackReply` carry a per-reply `read_at` field, or rely on the submission-level `has_unread_user_reply` flag? → A: Drop `read_at` from `FeedbackReply`; use `has_unread_user_reply` on `FeedbackSubmission` for admin unread state and `FeedbackNotification.read_at` for user notification state — simpler, faster, sufficient for v1.
- Q: How is the admin unread indicator cleared — automatically on thread expand, or via explicit "Mark as read" button? → A: Automatically on expand — frontend fires a PATCH to clear `has_unread_user_reply` the moment the admin expands the thread panel; no explicit action required.
- Q: What route and nav placement for the "My Feedback" page? → A: `/my-feedback` — new top-level route, added as a nav item in the main sidebar/header for all authenticated users.
- Q: What UI pattern for loading older thread messages beyond the 20-message default? → A: "Load earlier messages" button at the top of the thread — fetches older messages via `before_id` cursor; scroll position stays anchored (no jump).

## Out of Scope

- Email or push notifications for reply activity.
- Reply editing or deletion after posting.
- Read receipts visible to the sender ("Seen at…").
- Reactions or emoji responses to replies.
- Mentions or tagging other users in replies.
- Admin-to-admin internal notes on a submission (separate from the user-visible thread).
- Bulk reply or templated responses.
