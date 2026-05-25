# Feature Specification: Notification Center

**Feature Branch**: `029-notification-center`  
**Created**: 2026-05-25  
**Status**: Draft  
**Input**: User description: "Notification Center — System-wide notification engine with in-app notifications and email delivery. Supports template approval events (submitted, approved, rejected, published), template feedback responses, template version updates, draft expiry warnings, and system announcements. Extends existing F14 notification infrastructure. Bell icon with unread count, notification preferences per user, bilingual email templates with org branding. Vision item AC-06."

## User Scenarios & Testing

### User Story 1 — In-App Notification Delivery & Bell Icon (Priority: P1)

Users across all roles receive real-time in-app notifications for events relevant to them. A bell icon in the nav bar shows the unread count badge. Clicking the bell opens a dropdown panel showing recent notifications with mark-as-read. Each notification includes a bilingual title (Arabic/English), a body, and a deep link to the relevant page (e.g., clicking "Template approved" navigates to the template in the designer).

The notification engine is event-driven: when a qualifying event occurs anywhere in the system (template transition, feedback reply, version publish), a notification record is created for each recipient. The bell icon updates without requiring a page refresh.

**Why this priority**: Without a centralized notification system, users have no visibility into events that require their attention — Reviewers don't know templates are waiting, Designers don't know their submissions were approved or rejected, and Operators don't know new template versions are available. This is the foundation all other notification features build on.

**Independent Test**: Trigger a template approval event, verify the Reviewer and Designer both receive in-app notifications with correct content, verify the bell icon shows unread count, verify clicking the notification navigates to the correct page.

**Acceptance Scenarios**:

1. **Given** a Designer submits a template for review, **When** the transition completes, **Then** all branch_managers in the template's department (and all admins) receive an in-app notification with title "Template submitted for review" and template name, linking to the review queue.
2. **Given** a Reviewer approves a template, **When** the transition completes, **Then** the Designer who created the template and all org admins receive an in-app notification with title "Template approved" and template name, linking to the template.
3. **Given** a Reviewer rejects a template, **When** the transition completes, **Then** the Designer receives an in-app notification with title "Template rejected" and the reviewer's comment, linking to the template.
4. **Given** an Admin publishes a template, **When** the transition completes, **Then** all operators in the template's department receive an in-app notification with title "New template version available" and template name, linking to Form Desk.
5. **Given** a user has 3 unread notifications, **When** they view the nav bar, **Then** the bell icon shows a badge with "3". Clicking opens a dropdown panel showing the 3 notifications with title, time ago, and read/unread styling.
6. **Given** a user clicks a notification, **When** the notification panel closes, **Then** the notification is marked as read and the user navigates to the deep-linked page.
7. **Given** a user clicks "Mark all as read", **When** the action completes, **Then** all notifications are marked as read and the badge count resets to 0.

---

### User Story 2 — Notification Preferences (Priority: P2)

Each user can configure which notification types they want to receive and through which channels (in-app, email). Preferences are per-notification-type (e.g., "Template approved" can be in-app only, while "Template rejected" is both in-app and email). Default preferences are set at the org level and inherited by new users, but each user can override.

**Why this priority**: Without preferences, users will be overwhelmed by notifications they don't care about, leading to notification fatigue and eventual disengagement. Preferences make the system usable at scale.

**Independent Test**: Set a user's preference to disable email for "Template published" events, trigger a publish, verify only in-app notification is created (no email sent).

**Acceptance Scenarios**:

1. **Given** a user navigates to their notification preferences, **When** the page loads, **Then** they see a table of all notification types with toggles for in-app and email channels. Each toggle shows the current preference (on/off).
2. **Given** a user disables email for "Template submitted for review", **When** a template is submitted, **Then** the user receives an in-app notification but no email.
3. **Given** a user disables both in-app and email for a notification type, **When** that event occurs, **Then** no notification is created for that user.
4. **Given** a new user joins the organization, **When** their account is created, **Then** their notification preferences inherit the org-level defaults.

---

### User Story 3 — Email Notification Delivery (Priority: P2)

For notification types where email is enabled, the system sends bilingual HTML emails with org branding (logo, colors). Emails are sent asynchronously (background task) and include the event details, a call-to-action link to the relevant page, and an unsubscribe link per notification type. Email delivery status is tracked (sent, failed).

**Why this priority**: Many users (especially managers and admins) don't stay logged in to FormCraft all day. Email ensures critical events reach them even when they're not in the app.

**Independent Test**: Trigger a template rejection with email enabled for the Designer, verify an HTML email is sent with the rejection comment, org logo, bilingual content, and a link to the template.

**Acceptance Scenarios**:

1. **Given** a template is rejected and the Designer has email enabled for "Template rejected", **When** the notification is created, **Then** an HTML email is sent to the Designer's email address with: org logo and colors in header, bilingual title (Arabic/English), rejection comment, reviewer name, and a "View Template" button linking to the template.
2. **Given** a notification email fails to send (SMTP error), **When** the send fails, **Then** the system retries up to 3 times with exponential backoff (1min, 5min, 15min). The delivery status is logged as "failed" after all retries.
3. **Given** a user clicks the unsubscribe link in an email, **When** they confirm, **Then** the email channel is disabled for that notification type in their preferences. Other notification types remain unchanged.

---

### User Story 4 — Full Notification History (Priority: P3)

Users can view their complete notification history at `/notifications` — a full-page view with filters by notification type, read status, and date range. This replaces the dropdown panel for users who need to review older notifications.

**Why this priority**: The dropdown panel only shows recent notifications. Users reviewing audit trails or catching up after absence need access to the full history.

**Independent Test**: Generate 50 notifications for a user, navigate to `/notifications`, verify all are visible with filters working correctly.

**Acceptance Scenarios**:

1. **Given** a user has 50 notifications over the past 30 days, **When** they navigate to `/notifications`, **Then** they see a paginated list of all notifications with: type icon, title, body preview, timestamp, and read/unread styling.
2. **Given** a user filters by "Template approval" type, **When** the filter is applied, **Then** only template approval notifications are shown.
3. **Given** a user filters by "Unread" status, **When** the filter is applied, **Then** only unread notifications are shown.

---

### User Story 5 — System Announcements (Priority: P3)

Org Admins can create system announcements that are delivered to all users in the organization (or filtered by role/department). Announcements appear as a special notification type with higher visual priority (e.g., different icon, pinned to top of notification panel).

**Why this priority**: Admins need a way to communicate system-wide messages (maintenance windows, policy changes, new template availability) without relying on external email.

**Independent Test**: Create a system announcement as Admin, verify all targeted users see it in their notification panel with announcement styling.

**Acceptance Scenarios**:

1. **Given** an Admin creates a system announcement with title and body, **When** they select "All users" as audience and click "Send", **Then** every active user in the organization receives an in-app notification with announcement styling.
2. **Given** an Admin creates an announcement targeting "Retail Banking" department operators only, **When** sent, **Then** only operators in that department receive the notification.
3. **Given** a system announcement exists, **When** a user opens the notification panel, **Then** announcements appear pinned at the top with a distinct icon (megaphone), separate from regular notifications.

---

### Edge Cases

- What happens when a notification recipient is deactivated? The notification is created but not delivered. If the user is later reactivated, the notification is available in their history but not surfaced as "new".
- What happens when an email bounces permanently (invalid address)? After 3 failed attempts, the email channel is automatically disabled for that user with a flag "email_delivery_failed". Admin can see which users have delivery failures.
- What happens when a template transition generates notifications for 500+ users (large org publish)? Notifications are created in batch (bulk insert) and emails are queued for background processing with rate limiting (max 50 emails/minute per org) to avoid SMTP throttling.
- What happens when a user has 1000+ unread notifications (long absence)? The bell badge shows "99+" and the dropdown shows the 20 most recent. The full history page handles pagination.
- What happens when the same event generates both an in-app and email notification and the user reads the in-app one? The email is still sent (it was queued at event time). The email contains a "View in app" link that marks the notification as read.
- What happens when notification preferences are updated while notifications are being generated? Preferences are read at notification creation time. Any notification already queued for email will still be sent.

## Requirements

### Functional Requirements

- **FR-001**: System MUST support a centralized notification engine that creates notification records for qualifying events and routes them to appropriate recipients based on event type and user roles.
- **FR-002**: System MUST support the following notification event types: template_submitted_for_review, template_approved, template_rejected, template_published, template_withdrawn, template_feedback_received, template_feedback_resolved, draft_expiring, system_announcement.
- **FR-003**: System MUST deliver notifications through two channels: in-app (real-time via polling) and email (asynchronous background delivery).
- **FR-004**: System MUST display a bell icon in the nav bar with an unread count badge. Clicking opens a dropdown panel showing the 20 most recent notifications.
- **FR-005**: System MUST allow users to mark individual notifications as read, mark all as read, and navigate to the deep-linked page when clicking a notification.
- **FR-006**: System MUST allow each user to configure notification preferences per notification type and per channel (in-app on/off, email on/off).
- **FR-007**: System MUST support org-level default notification preferences that are inherited by new users.
- **FR-008**: System MUST send bilingual HTML emails (Arabic/English based on recipient's language preference) with org branding (logo, primary color) for email-enabled notifications.
- **FR-009**: System MUST retry failed email deliveries up to 3 times with exponential backoff before marking as permanently failed.
- **FR-010**: System MUST provide a full notification history page (`/notifications`) with filters by type, read status, and date range, with pagination.
- **FR-011**: System MUST allow Admins to create system announcements targeting all users, a specific role, or a specific department.
- **FR-012**: System MUST respect multi-tenant isolation — notifications are scoped by org_id and never leak across organizations.
- **FR-013**: System MUST display all notification content in bilingual format (Arabic title + English title) matching the user's language preference.
- **FR-014**: System MUST include an unsubscribe link in each email that disables the email channel for that specific notification type.
- **FR-015**: System MUST determine notification recipients based on event type: approval events go to relevant reviewers/designers/admins, publish events go to department operators, feedback events go to template designers, announcements go to targeted audience.

### Non-Functional Requirements

- **NFR-001**: In-app notifications MUST appear within 5 seconds of the triggering event.
- **NFR-002**: Email notifications MUST be queued within 1 second of the triggering event and sent within 5 minutes under normal load.
- **NFR-003**: Notification creation for bulk events (e.g., template published to 500 operators) MUST complete within 3 seconds using batch insert.
- **NFR-004**: The notification bell badge count MUST update without full page refresh (polling interval max 30 seconds).
- **NFR-005**: All notification data MUST respect multi-tenant RLS isolation — scoped by org_id.

### Key Entities

- **Notification**: A record created for a specific recipient when a qualifying event occurs. Contains: recipient_id, org_id, type, title_ar, title_en, body_ar, body_en, action_url, read_at, email_status, created_at.
- **Notification Preference**: A user's per-type channel preferences. Contains: user_id, notification_type, in_app_enabled, email_enabled. Defaults inherited from org settings.
- **System Announcement**: A special notification created by an Admin targeting a broad audience. Contains: org_id, title_ar, title_en, body_ar, body_en, target_audience (all/role/department), target_id, created_by, created_at.

## Assumptions

- The existing `feedback_notifications` table from F14 is specific to feedback threading and will remain as-is. This feature creates a NEW generalized `notifications` table that covers all event types including feedback. The F14 notification endpoints (`GET /notifications`, `POST /notifications/{id}/read`) will be migrated to use the new table.
- The existing `notification_dismissals` table from F16 handles operator dashboard version dismissals and will remain separate (it's UX-specific, not the notification engine).
- Email sending requires an SMTP provider or transactional email service (e.g., SendGrid, AWS SES, Resend). The email provider configuration will be stored in org settings or environment variables. The specific provider is not prescribed by this spec.
- The `notification_preferences` field already exists in the org settings JSONB (migration 027). This feature extends it from a simple `{"email": true, "in_app": true}` to a per-type preference matrix.
- Notification polling (client-side interval) is the MVP approach for real-time updates. Server-Sent Events (SSE) or WebSocket upgrade is a future enhancement.
- The existing `profiles` table has `language` (ar/en) which determines which language the user sees in-app and which language the email is rendered in.

## Dependencies

- **F01 Auth & Users**: User identity, roles, and email addresses for notification routing.
- **F02 i18n**: Bilingual content rendering for notification titles, bodies, and email templates.
- **F25 Multi-Tenancy**: Org scoping for notifications, org branding for emails, department-level audience targeting.
- **F28 Approval Workflow**: Primary event source — template submission, approval, rejection, publish transitions trigger notifications.
- **F14 Feedback Threading**: Existing notification infrastructure (endpoints, schemas) to be generalized. Feedback reply events trigger notifications.
- **F19 Template Versioning**: Template publish events trigger operator notifications.

## Out of Scope

- Push notifications (mobile/browser) — deferred to mobile support feature.
- Real-time WebSocket or SSE delivery — MVP uses polling; upgrade deferred to performance enhancement.
- Email template visual editor (Admin customizes email layout) — emails use a standard template with org branding auto-applied.
- Notification aggregation/digest (daily summary email) — deferred to future iteration.
- Slack/Teams/webhook integration for notification delivery — deferred to AC-07 integration feature.
- SMS notifications — deferred to future iteration.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users are aware of events requiring their attention within 30 seconds of the event occurring (in-app notification visible in bell dropdown).
- **SC-002**: 100% of template approval transitions (submit, approve, reject, publish) generate notifications to the correct recipients with zero missed events.
- **SC-003**: Email delivery success rate exceeds 95% for valid email addresses (excluding permanent bounces).
- **SC-004**: Users can configure their notification preferences in under 1 minute with no more than 2 clicks per notification type.
- **SC-005**: The notification bell badge accurately reflects the true unread count at all times (no stale counts after marking as read).
- **SC-006**: System announcements reach all targeted users within 5 seconds of being sent.
