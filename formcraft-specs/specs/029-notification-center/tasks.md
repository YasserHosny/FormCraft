# Tasks: Notification Center

**Input**: Design documents from `/specs/029-notification-center/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/notification-api.md, quickstart.md

**Tests**: Not explicitly requested. Test tasks omitted.

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Database migration, shared schemas, TypeScript interfaces

- [ ] T001 Create database migration for notifications and notification_preferences tables in formcraft-backend/migrations/031_notification_center.sql — includes notifications table (id, recipient_id, org_id, type, title_ar, title_en, body_ar, body_en, action_url, source_id, source_type, is_announcement, read_at, email_status, email_sent_at, email_error, email_retry_count, created_by, created_at), notification_preferences table (id, user_id, org_id, notification_type, in_app_enabled, email_enabled, created_at, updated_at) with UNIQUE(user_id, org_id, notification_type), all indexes per data-model.md, RLS policies, and org settings migration from flat notification_preferences to per-type defaults structure
- [ ] T002 [P] Add NotificationType enum values (template_submitted_for_review, template_approved, template_rejected, template_published, template_withdrawn, template_feedback_received, template_feedback_resolved, draft_expiring, system_announcement) and EmailStatus enum (pending, sent, failed, skipped) in formcraft-backend/app/models/enums.py
- [ ] T003 [P] Create notification Pydantic schemas in formcraft-backend/app/schemas/notification.py — NotificationResponse (id, type, title_ar, title_en, body_ar, body_en, action_url, source_id, source_type, is_announcement, read_at, created_by, created_at), NotificationsListResponse (notifications list, total, page, page_size), UnreadCountResponse (unread_count), NotificationPreferenceResponse (notification_type, in_app_enabled, email_enabled, is_default), PreferencesListResponse, PreferenceUpdateRequest, AnnouncementCreateRequest (title_ar, title_en, body_ar, body_en, target_audience, target_role, target_department_id), AnnouncementResponse (announcement_id, recipients_count, created_at), MarkReadResponse (id, read_at), MarkAllReadResponse (marked_count)
- [ ] T004 [P] Create TypeScript notification interfaces in formcraft-frontend/src/app/shared/models/notification.models.ts — Notification interface, NotificationsListResponse, UnreadCountResponse, NotificationPreference, PreferencesListResponse, PreferenceUpdate, AnnouncementCreate, AnnouncementResponse, NotificationType string union type

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core notification service, email service, bilingual content helpers, and email templates that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Create notification service in formcraft-backend/app/services/notification_service.py — implements create_notifications() method that: resolves recipient preferences (user-level then org defaults fallback), skips if both channels disabled, batch-inserts notification rows with correct email_status (pending/skipped), queues email background task for pending rows. Also implements get_notifications() with pagination and filters (type, read/unread, date_from, date_to), get_unread_count(), mark_as_read(), mark_all_as_read() methods. Uses Supabase client for all DB operations.
- [ ] T006 [P] Create email service in formcraft-backend/app/services/email_service.py — implements send_notification_email() using smtplib with email.mime, renders Jinja2 HTML templates, handles bilingual content based on recipient language preference from profiles table, generates signed unsubscribe JWT token. SMTP config from env vars (SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_FROM). Updates email_status and email_sent_at in notifications table on success.
- [ ] T007 [P] Create base email template in formcraft-backend/templates/email/base.html — Jinja2 HTML email template with org branding (logo URL, primary color from org settings), bilingual layout (Arabic RTL + English LTR sections), unsubscribe link in footer, "View in App" CTA button block, responsive design for email clients
- [ ] T008 [P] Create event-specific email templates in formcraft-backend/templates/email/ — template_submitted.html (extends base, shows template name and submitter), template_approved.html (template name, approver), template_rejected.html (template name, reviewer name, rejection comment), template_published.html (template name, version), system_announcement.html (announcement title and body). Each template uses Jinja2 blocks from base.html for content and CTA.
- [ ] T009 [P] Add bilingual notification title/body generation helpers in formcraft-backend/app/services/notification_service.py — create helper functions (e.g., build_notification_content(event_type, template_name, actor_name, comment)) that return title_ar, title_en, body_ar, body_en for each of the 9 event types. Used by transition hooks (T013) and all other notification creation call sites. Ensures consistent bilingual content across all event types.

**Checkpoint**: Foundation ready — notification creation, email delivery, bilingual content helpers, and templates all operational

---

## Phase 3: User Story 1 — In-App Notification Delivery & Bell Icon (Priority: P1) 🎯 MVP

**Goal**: Users receive in-app notifications for template transition events. Bell icon in nav bar shows unread count badge. Clicking opens dropdown with recent notifications. Clicking a notification navigates to deep-linked page.

**Independent Test**: Trigger a template approval, verify bell badge updates within 30s, click bell to see notification, click notification to navigate to template.

### Implementation for User Story 1

- [ ] T010 [US1] Create notification routes in formcraft-backend/app/api/routes/notifications.py — register new router with prefix /api/notifications. Implement: GET / (list with pagination + filters), GET /unread-count, PATCH /{notification_id}/read, POST /read-all. Each endpoint extracts user_id and org_id from auth token, delegates to notification_service. Add role gate (any authenticated user). Register router in formcraft-backend/app/main.py.
- [ ] T011 [US1] Remove old notification endpoints from formcraft-backend/app/api/routes/feedback.py — remove GET /notifications and PATCH /notifications/{id}/read from user_router (lines ~207-231). These are now served by the new notifications.py router. Keep ReplyService feedback_notifications write path untouched for now.
- [ ] T012 [US1] Hook notification creation into template transitions in formcraft-backend/app/services/template_service.py — in transition_status() method, after successful status change, call notification_service.create_notifications() using build_notification_content() helpers from T009 with: correct event type based on new status (submitted_for_review, approved, rejected, published, withdrawn), action_url pointing to template, source_id = template_id, source_type = 'template'. Resolve recipient_ids using R4 rules: submitted → branch_managers in department + admins, approved → template creator + admins, rejected → template creator, published → operators in department, withdrawn → branch_managers who were notified.
- [ ] T013 [P] [US1] Create notification Angular service in formcraft-frontend/src/app/shared/services/notification.service.ts — implements: polling via interval(30000) hitting GET /unread-count, unreadCount$ BehaviorSubject, notifications$ for dropdown list, fetchNotifications() for bell dropdown (GET / with page_size=20), markAsRead(id), markAllAsRead(), stopPolling(), startPolling(). Uses HttpClient. Auto-starts polling on construction, stops on destroy.
- [ ] T014 [US1] Create notification bell component in formcraft-frontend/src/app/shared/components/notification-bell/ — notification-bell.component.ts: injects NotificationService, subscribes to unreadCount$, toggles dropdown open/close, fetches notifications on open, handles notification click (markAsRead + router.navigate to action_url), markAllAsRead button. notification-bell.component.html: mat-icon-button with 'notifications' icon, mat-badge with unread count (hidden when 0, shows "99+" when >99), mat-menu or cdkOverlay dropdown panel showing notification list with: type-specific mat-icon, title (Arabic or English per i18n), relative time (pipe), read/unread bold styling, "Mark all as read" header action, "View all" footer link to /notifications. notification-bell.component.scss: dropdown panel max-height 400px with scroll, unread notification bold/highlighted styling, hover states.
- [ ] T015 [US1] Add notification bell to app nav bar in formcraft-frontend/src/app/app.component.html — insert <app-notification-bell> component in the top nav bar area, positioned before the user avatar/menu. Import NotificationBellComponent in app.component.ts or shared module. Ensure bell is only visible when user is authenticated.

**Checkpoint**: Bell icon visible, polls for unread count, dropdown shows notifications, clicking navigates to linked page. Template approval lifecycle creates correct notifications.

---

## Phase 4: User Story 2 — Notification Preferences (Priority: P2)

**Goal**: Users configure per-type, per-channel notification preferences. Org-level defaults inherited. Preferences respected during notification creation.

**Independent Test**: Disable email for "Template published", trigger publish, verify only in-app notification created (no email).

### Implementation for User Story 2

- [ ] T016 [US2] Add preferences endpoints to formcraft-backend/app/api/routes/notifications.py — implement GET /preferences (returns merged view: user overrides + org defaults with is_default flag for each type) and PATCH /preferences (upsert user preference rows). GET merges by iterating all NotificationType values, checking notification_preferences table for user row, falling back to org settings defaults if missing. PATCH uses Supabase upsert on (user_id, org_id, notification_type).
- [ ] T017 [US2] Create notification preferences component in formcraft-frontend/src/app/features/profile/notification-preferences/ — notification-preferences.component.ts: fetches GET /preferences on init, displays table of all 9 notification types with mat-slide-toggle for in_app and email channels, shows "(org default)" label when is_default=true, on toggle change calls PATCH /preferences with updated preference, shows success snackbar. notification-preferences.component.html: mat-table with columns: notification type label (bilingual), in-app toggle, email toggle. notification-preferences.component.scss: table styling with clear type labels and toggle alignment.
- [ ] T018 [US2] Add notification preferences route and navigation in formcraft-frontend — add route for /profile/notification-preferences in the profile routing module. Add link to notification preferences from user profile page or user menu dropdown.

**Checkpoint**: Users can view and toggle preferences per type/channel. Notification creation respects these preferences (skips disabled channels).

---

## Phase 5: User Story 3 — Email Notification Delivery (Priority: P2)

**Goal**: Email notifications sent for enabled types with org-branded bilingual HTML, retry logic, and unsubscribe link.

**Independent Test**: Trigger template rejection with email enabled, verify HTML email with org branding, rejection comment, and working unsubscribe link.

### Implementation for User Story 3

- [ ] T019 [US3] Implement email sending background task in formcraft-backend/app/services/email_service.py — add process_pending_emails() method that queries notifications with email_status='pending' and email_retry_count<3, renders appropriate Jinja2 template per notification type, sends via SMTP, updates email_status to 'sent' with email_sent_at timestamp on success, increments email_retry_count and sets email_error on failure. Add schedule_email_retry() for exponential backoff (1min, 5min, 15min). Wire into FastAPI BackgroundTasks from notification_service.create_notifications().
- [ ] T020 [US3] Add unsubscribe endpoint in formcraft-backend/app/api/routes/notifications.py — implement GET /unsubscribe with token query param. Token is a signed JWT containing user_id, org_id, notification_type. Verify token signature, extract claims, upsert notification_preferences row with email_enabled=false. Return simple HTML confirmation page. Add generate_unsubscribe_token() utility to email_service.py.
- [ ] T021 [US3] Integrate email service with notification creation flow — in notification_service.create_notifications(), after batch insert, collect notification IDs where email_status='pending', pass to background_tasks.add_task(email_service.process_pending_emails, notification_ids). Ensure org settings (logo_url, primary_color) and recipient profile (email, language) are loaded for email rendering.

**Checkpoint**: Emails sent with org branding, bilingual content, retry on failure. Unsubscribe link disables email for specific type.

---

## Phase 6: User Story 4 — Full Notification History (Priority: P3)

**Goal**: Full-page notification history at /notifications with filters by type, read status, date range, and pagination.

**Independent Test**: Generate 50 notifications, navigate to /notifications, verify pagination and all filters work.

### Implementation for User Story 4

- [ ] T022 [US4] Create notification history component in formcraft-frontend/src/app/features/notifications/ — notification-history.component.ts: fetches GET /notifications with pagination params, implements filter controls for type (mat-select with all NotificationType values), read status (mat-button-toggle: all/read/unread), date range (mat-date-range-picker), page size selector. Handles notification click (markAsRead + navigate). notification-history.component.html: filter bar at top, mat-list of notifications with type-specific mat-icon, bilingual title, body preview (truncated), relative timestamp, read/unread styling, mat-paginator at bottom. notification-history.component.scss: responsive layout, filter bar styling, notification item hover states.
- [ ] T023 [US4] Add notification history route in formcraft-frontend — add /notifications route in app routing module (lazy-loaded feature module). Add "View all notifications" link in bell dropdown footer that navigates to /notifications.

**Checkpoint**: Full history page shows all notifications with working filters and pagination.

---

## Phase 7: User Story 5 — System Announcements (Priority: P3)

**Goal**: Admins create system announcements targeting all users, a role, or a department. Announcements appear pinned in bell dropdown with distinct styling.

**Independent Test**: Admin creates announcement for all users, verify all see it pinned at top of bell dropdown with megaphone icon.

### Implementation for User Story 5

- [ ] T024 [US5] Add announcements endpoint in formcraft-backend/app/api/routes/notifications.py — implement POST /admin/announcements with admin-only role gate. Resolve recipient_ids based on target_audience: 'all' → all active users in org, 'role' → all users with target_role in org, 'department' → all users in target_department_id. Call notification_service.create_notifications() with type='system_announcement', is_announcement=true. Return recipients_count.
- [ ] T025 [US5] Create announcements admin component in formcraft-frontend/src/app/features/admin/announcements/ — announcements.component.ts: form with mat-input for title_ar, title_en, body_ar (optional), body_en (optional), mat-radio-group for target_audience (all/role/department), conditional mat-select for role or department based on selection. Submit calls POST /admin/announcements, shows success snackbar with recipient count. announcements.component.html: Angular reactive form layout with bilingual inputs and audience targeting. announcements.component.scss: form styling.
- [ ] T026 [US5] Add announcements route to admin routing in formcraft-frontend — add /admin/announcements route in admin routing module. Add navigation link in admin sidebar/menu.
- [ ] T027 [US5] Update notification bell dropdown to pin announcements — in notification-bell.component.html, separate announcements (is_announcement=true) into a pinned section at top of dropdown with megaphone mat-icon and distinct background color. Regular notifications appear below. Backend GET /notifications already sorts by is_announcement DESC.

**Checkpoint**: Admins can create announcements. All targeted users see them pinned in bell dropdown.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Bilingual frontend labels, feedback hooks, draft expiry, edge cases, NFR validation, and cleanup

- [ ] T028 [P] Add bilingual labels for all notification types in formcraft-frontend i18n files — add Arabic and English labels for all 9 notification types, notification preference labels, announcement form labels, bell dropdown UI strings, history page filter labels
- [ ] T029 Hook feedback reply notifications into new notification engine — in formcraft-backend/app/services/feedback/reply_service.py, when creating a reply, also call notification_service.create_notifications() with type=template_feedback_received (for designer) or template_feedback_resolved (for operator). Keep writing to feedback_notifications table for backward compatibility but primary delivery is now through new notifications table.
- [ ] T030 Implement draft_expiring notification trigger — add a utility function in formcraft-backend/app/services/notification_service.py that queries templates with status='draft' and updated_at older than the org's configured expiry threshold (default 30 days). For each expiring draft, call create_notifications() with type='draft_expiring', recipient = template created_by (draft owner), action_url pointing to the template. This function is designed to be called from a scheduled job or admin endpoint; for MVP, expose as POST /api/admin/check-draft-expiry (admin-only) that triggers the scan on demand.
- [ ] T031 Handle edge cases — implement: bell badge shows "99+" for 1000+ unread (frontend), deactivated user notifications created but email_status='skipped' (check profiles.is_active during create_notifications), email bounce handling sets email_delivery_failed flag after 3 failures, bulk insert rate limiting for 500+ recipients (batch size 100), preference timing (read preferences at creation time, not delivery time)
- [ ] T032 Validate NFR compliance — verify: unread-count endpoint responds <50ms, polling interval is 30s, bulk create of 500 notifications completes in <3s, email queued within 1s of event, all queries use org_id RLS scoping
- [ ] T033 Run quickstart.md scenarios 1-8 and API smoke tests to validate end-to-end functionality

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on T001 (migration), T002 (enums), T003 (schemas) — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion (T005-T009)
- **User Story 2 (Phase 4)**: Depends on Foundational phase. Can run in parallel with US1 (preference endpoints are independent)
- **User Story 3 (Phase 5)**: Depends on Foundational phase (especially T006 email service, T007-T008 templates). Can run in parallel with US1/US2
- **User Story 4 (Phase 6)**: Depends on US1 (uses same notification service and bell component's "View all" link)
- **User Story 5 (Phase 7)**: Depends on US1 (announcement display in bell dropdown)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational — no dependencies on other stories
- **US2 (P2)**: Can start after Foundational — independent of US1 (backend preferences work without bell icon)
- **US3 (P2)**: Can start after Foundational — independent (email delivery is a channel, not tied to bell UI)
- **US4 (P3)**: Depends on US1 (notification service + "View all" link in bell)
- **US5 (P3)**: Depends on US1 (announcement pinning in bell dropdown)

### Within Each User Story

- Models/schemas before services
- Services before endpoints/routes
- Backend before frontend
- Core implementation before integration

### Parallel Opportunities

- T002, T003, T004 can all run in parallel (different files)
- T006, T007, T008, T009 can run in parallel (email service + templates + content helpers)
- US1 and US2 backend tasks can run in parallel after Foundational
- US1 and US3 can run in parallel (in-app vs email channels)
- T028 (frontend i18n) can run in parallel with T029-T030 (backend hooks)

---

## Parallel Example: Phase 1 Setup

```bash
# All setup tasks after T001 can run in parallel:
Task T002: "Add NotificationType and EmailStatus enums in enums.py"
Task T003: "Create notification Pydantic schemas in notification.py"
Task T004: "Create TypeScript notification interfaces in notification.models.ts"
```

## Parallel Example: Phase 2 Foundational

```bash
# After T005 (notification service), these are parallel:
Task T006: "Create email service in email_service.py"
Task T007: "Create base email template in base.html"
Task T008: "Create event-specific email templates"
Task T009: "Add bilingual content helpers in notification_service.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (migration, enums, schemas, interfaces)
2. Complete Phase 2: Foundational (notification service, email service, content helpers, templates)
3. Complete Phase 3: User Story 1 (bell icon, dropdown, template transition hooks)
4. **STOP and VALIDATE**: Test bell icon, notifications on template approval, mark as read
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add US1 (Bell + In-App) → Test independently → Deploy (MVP!)
3. Add US2 (Preferences) → Test toggle behavior → Deploy
4. Add US3 (Email) → Test email delivery → Deploy
5. Add US4 (History) → Test full page → Deploy
6. Add US5 (Announcements) → Test admin flow → Deploy
7. Polish → Validate NFRs → Final deploy

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: US1 (Bell Icon + In-App)
   - Developer B: US2 (Preferences) + US3 (Email)
3. After US1 complete:
   - Developer A: US4 (History) + US5 (Announcements)
4. Polish phase together

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- The old feedback.py notification endpoints (T011) must be removed to avoid route conflicts with the new notifications.py router
