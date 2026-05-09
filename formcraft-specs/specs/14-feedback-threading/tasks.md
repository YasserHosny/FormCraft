# Tasks: Feedback Threading & Replies

**Input**: Design documents from `formcraft-specs/specs/14-feedback-threading/`
**Branch**: `014-feedback-threading` | **Date**: 2026-05-09
**Prerequisites**: plan.md ✅ · spec.md ✅ · data-model.md ✅ · contracts/api.md ✅ · research.md ✅ · quickstart.md ✅
**Depends on**: Feature 011 (`001-customer-feedback`) fully applied — `feedback_submissions` table, admin dashboard, and widget must exist

**Tests**: Included — consistent with feature 011/012/013 pattern.

**Organization**: Tasks grouped by user story (P1 Admin Replies → P2 My Feedback → P3 Notifications) so each story is independently implementable, testable, and deployable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[Story]**: User story label (US1 / US2 / US3)

## Path Conventions

- Backend: `formcraft-backend/`
- Frontend: `formcraft-frontend/src/app/`

---

## Phase 1: Setup

**Purpose**: Migration, empty file skeletons, and module scaffolding so subsequent phases have a stable base.

- [x] T001 Write migration `formcraft-backend/supabase/migrations/011_create_feedback_replies.sql` — full SQL from data-model.md: `ALTER TABLE feedback_submissions ADD COLUMN reply_count INT NOT NULL DEFAULT 0, ADD COLUMN has_unread_user_reply BOOLEAN NOT NULL DEFAULT FALSE`; `CREATE TABLE feedback_replies` with indexes and RLS; `CREATE TABLE feedback_notifications` with indexes and RLS
- [x] T002 [P] Create empty file skeletons: `formcraft-backend/app/schemas/reply.py` (empty), `formcraft-backend/app/services/feedback/reply_service.py` (empty), `formcraft-backend/tests/unit/feedback/test_reply_service.py` (empty), `formcraft-backend/tests/integration/feedback/test_reply_routes.py` (empty), `formcraft-frontend/src/app/features/feedback/models/reply.models.ts` (empty — canonical TypeScript interfaces shared across all frontend consumers of this feature), `formcraft-frontend/src/app/features/feedback/services/feedback-realtime.service.ts` (empty), `formcraft-frontend/src/app/shared/components/thread/thread.component.ts` (empty), `formcraft-frontend/src/app/features/my-feedback/my-feedback.module.ts` (empty), `formcraft-frontend/src/app/features/my-feedback/services/my-feedback.service.ts` (empty)

**Checkpoint**: Migration SQL written, empty modules in place — ready to define schemas and write tests

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Pydantic schemas, service stubs, and Angular service skeleton shared by all three user stories. Must be complete before any story begins.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Write all Pydantic models in `formcraft-backend/app/schemas/reply.py`: `ReplyCreateRequest(text_content: str)` — `@field_validator` enforces 1–2000 chars; `ReplyResponse(id: UUID, author_role: Literal['admin','user'], author_name: str, text_content: str, created_at: datetime)`; `ThreadResponse(replies: list[ReplyResponse], has_earlier: bool)`; `MyFeedbackItem(id: UUID, page_url: str, text_content: str, status: str, submitted_at: datetime, reply_count: int, has_unread_admin_reply: bool)`; `MyFeedbackResponse(results: list[MyFeedbackItem], total: int, page: int, page_size: int)`; `NotificationResponse(id: UUID, feedback_id: UUID, reply_id: UUID, created_at: datetime, delivered_at: datetime | None, read_at: datetime | None)`; `NotificationsResponse(notifications: list[NotificationResponse], unread_count: int)`
- [x] T004 [P] Create method stubs in `formcraft-backend/app/services/feedback/reply_service.py`: `get_replies(feedback_id, user_id, is_admin, limit, before_id) → ThreadResponse`, `post_reply(feedback_id, author_id, author_role, payload) → ReplyResponse`, `mark_submission_read(feedback_id)`, `get_my_feedback(user_id, page, page_size) → MyFeedbackResponse`, `get_notifications(user_id) → NotificationsResponse`, `mark_notification_read(notification_id, user_id)` — all bodies raise `NotImplementedError`
- [x] T005 [P] Two-part task: **(a) Write all TypeScript interfaces** in `formcraft-frontend/src/app/features/feedback/models/reply.models.ts` — `export interface ReplyResponse { id: string; author_role: 'admin' | 'user'; author_name: string; text_content: string; created_at: string; }`, `export interface ThreadResponse { replies: ReplyResponse[]; has_earlier: boolean; }`, `export interface MyFeedbackItem { id: string; page_url: string; text_content: string; status: string; submitted_at: string; reply_count: number; has_unread_admin_reply: boolean; }`, `export interface MyFeedbackResponse { results: MyFeedbackItem[]; total: number; page: number; page_size: number; }`, `export interface NotificationResponse { id: string; feedback_id: string; reply_id: string; created_at: string; delivered_at: string | null; read_at: string | null; }`, `export interface NotificationsResponse { notifications: NotificationResponse[]; unread_count: number; }` — this file is the **single source of truth** for all Angular consumers; **(b) Create `FeedbackRealtimeService` skeleton** in `formcraft-frontend/src/app/features/feedback/services/feedback-realtime.service.ts`: `@Injectable({ providedIn: 'root' })`; declare typed method signatures `subscribeToThread(feedbackId: string): Observable<ReplyResponse>`, `unsubscribeThread(feedbackId: string): void`, `notificationEvents$: Subject<NotificationResponse>`, `destroy(): void` — all bodies throw `Error('Not implemented')`; import `ReplyResponse` and `NotificationResponse` from `../models/reply.models`

**Checkpoint**: Schemas compile, service stubs importable — user story implementation can now begin

---

## Phase 3: User Story 1 — Admin Replies to Feedback (Priority: P1) 🎯 MVP

**Goal**: Admins post and read text replies on any submission via the dashboard. The reply thread appears in the expanded row with live Realtime updates. An unread badge marks submissions with new user follow-ups and clears automatically when the admin expands the thread.

**Independent Test**: Post a reply as admin on any submission → verify reply appears in thread with author name, timestamp, and role label → verify `reply_count` incremented on submission row → expand a submission with a user follow-up → verify unread badge visible → verify badge clears within 1 second of expanding → submit empty reply → verify Send is blocked.

### Backend Tests — Write First, Must FAIL Before Implementation

- [x] T006 [P] [US1] Write unit tests for admin reply paths in `formcraft-backend/tests/unit/feedback/test_reply_service.py`: `get_replies` admin — returns up to 20, `before_id` cursor returns correct earlier page, `has_earlier=True` when more exist, `has_earlier=False` at end; `post_reply` admin — success, increments `reply_count`, does NOT set `has_unread_user_reply`, inserts `feedback_notifications` row for submission's `user_id`; `post_reply` empty text → 400; `post_reply` text > 2000 chars → 400; `mark_submission_read` — sets `has_unread_user_reply = false`; non-admin `get_replies` on unowned submission → 403; `get_replies` on missing submission → 404
- [x] T007 [P] [US1] Write integration tests in `formcraft-backend/tests/integration/feedback/test_reply_routes.py`: `GET /api/admin/feedback/{id}/replies` → 200 any submission; 403 non-admin; 404 bad id; `POST /api/admin/feedback/{id}/replies` → 201 with `ReplyResponse`; 403 non-admin; 404 bad id; 400 empty text; `PATCH /api/admin/feedback/{id}/read` → 204; 403 non-admin; 404 bad id

### Backend Implementation — US1

- [x] T008 [US1] Implement `get_replies(feedback_id, user_id, is_admin, limit, before_id)` in `formcraft-backend/app/services/feedback/reply_service.py`: if not `is_admin`, SELECT `user_id` from `feedback_submissions WHERE id = feedback_id` → 404 if missing, 403 if `user_id != current user`; SELECT from `feedback_replies WHERE feedback_id = ?` and `(created_at, id) < before_id cursor` ORDER BY `created_at DESC` LIMIT `limit + 1`; set `has_earlier = len(rows) > limit`, slice to `limit`; return `ThreadResponse`
- [x] T009 [US1] Implement `post_reply(feedback_id, author_id, author_role, payload)` in `formcraft-backend/app/services/feedback/reply_service.py`: SELECT submission → 404 if missing; if `author_role == 'user'` and `submission.user_id != author_id` → 403; INSERT into `feedback_replies`; UPDATE `feedback_submissions SET reply_count = reply_count + 1`; if `author_role == 'user'`: UPDATE `has_unread_user_reply = TRUE`; if `author_role == 'admin'`: INSERT into `feedback_notifications(recipient_user_id=submission.user_id, feedback_id, reply_id)`; return `ReplyResponse` with `author_name` resolved from `profiles` JOIN
- [x] T010 [US1] Implement `mark_submission_read(feedback_id)` in `formcraft-backend/app/services/feedback/reply_service.py`: SELECT submission → 404 if missing; UPDATE `feedback_submissions SET has_unread_user_reply = FALSE WHERE id = feedback_id`
- [x] T011 [US1] Add `GET /api/admin/feedback/{id}/replies` route to `formcraft-backend/app/api/routes/admin.py` — requires `Role.ADMIN`; query params `limit: int = 20`, `before_id: UUID | None = None`; calls `get_replies(feedback_id, user_id=current_user.id, is_admin=True, limit, before_id)`; returns `ThreadResponse`
- [x] T012 [US1] Add `POST /api/admin/feedback/{id}/replies` route to `formcraft-backend/app/api/routes/admin.py` — requires `Role.ADMIN`; body `ReplyCreateRequest`; calls `post_reply(feedback_id, author_id=current_user.id, author_role='admin', payload)`; returns `ReplyResponse` with status 201
- [x] T013 [US1] Add `PATCH /api/admin/feedback/{id}/read` route to `formcraft-backend/app/api/routes/admin.py` — requires `Role.ADMIN`; calls `mark_submission_read(feedback_id)`; returns 204 No Content

### Frontend Implementation — US1

- [x] T014 [US1] Create `ThreadComponent` in `formcraft-frontend/src/app/shared/components/thread/`: `thread.component.ts` — import `ReplyResponse` from `features/feedback/models/reply.models`; `@Input() replies: ReplyResponse[]`; `@Input() hasEarlier: boolean`; `@Input() loading: boolean`; `@Output() loadEarlier = new EventEmitter<string>()` (emits `before_id` of oldest visible reply); `@Output() sendReply = new EventEmitter<string>()` (emits `text_content`); local `replyText: string`; `onSend()` — validates non-empty and ≤ 2000 chars, emits, clears textarea; `thread.component.html` — `*ngFor` reply list with author chip (label driven by `author_role`), timestamp, text; "Load earlier messages" `<button>` at top (shown when `hasEarlier`); reply textarea + character counter `{{replyText.length}}/2000` + Send button; empty-thread message; `thread.component.scss` — reply bubble styles, author chip colours distinguishing admin vs user, character counter, load-earlier button
- [x] T015 [US1] Implement `subscribeToThread(feedbackId)` and `unsubscribeThread(feedbackId)` in `formcraft-frontend/src/app/features/feedback/services/feedback-realtime.service.ts`: `subscribeToThread` — creates Supabase channel `thread:{feedbackId}` subscribing to `postgres_changes INSERT` on `feedback_replies` with `filter: feedback_id=eq.{feedbackId}`; on event, parse new row as `ReplyResponse`; returns `Subject<ReplyResponse>` that completes on `unsubscribeThread`; `unsubscribeThread` — calls `supabase.channel('thread:{feedbackId}').unsubscribe()`, completes the subject; store active channel map `Map<string, {channel, subject}>`
- [x] T016 [US1] Update `formcraft-frontend/src/app/features/feedback/components/feedback-admin/feedback-admin.component.ts`: add `expandedSubmissionId: string | null`; `onRowExpand(id)` — fetch `GET /api/admin/feedback/{id}/replies` → populate `replies`, `hasEarlier`; call `FeedbackRealtimeService.subscribeToThread(id)` → pipe into `takeUntil(collapseSignal$)` → push new replies to local array; call `PATCH /api/admin/feedback/{id}/read`; `onRowCollapse(id)` — `FeedbackRealtimeService.unsubscribeThread(id)`; `onLoadEarlier(beforeId)` — fetch with `before_id` param, prepend to array; `onSendReply(text)` — call `POST /api/admin/feedback/{id}/replies`
- [x] T017 [US1] Update `formcraft-frontend/src/app/features/feedback/components/feedback-admin/feedback-admin.component.html` and `.scss`: mount `<app-thread>` in expanded row passing `[replies]`, `[hasEarlier]`, `[loading]`, `(loadEarlier)`, `(sendReply)` bindings; add `[matBadge]="submission.reply_count > 0 && submission.has_unread_user_reply ? '●' : null"` badge on submission rows; style unread badge in `.scss`; update `feedback-admin.component.ts` to clear `has_unread_user_reply` reactively when `PATCH /read` succeeds
- [x] T018 [P] [US1] Add US1 i18n keys to `formcraft-frontend/src/assets/i18n/en.json` and `ar.json`: `feedback.thread.reply`, `feedback.thread.send`, `feedback.thread.load_earlier`, `feedback.thread.empty`, `feedback.thread.char_count`, `feedback.thread.admin_label`, `feedback.thread.user_label`

**Checkpoint**: Admin can post and read replies in the dashboard, Realtime updates appear within 1 s (SC-001), unread badge appears and clears automatically on expand → **MVP deliverable**

---

## Phase 4: User Story 2 — Users View Their Feedback History and Replies (Priority: P2)

**Goal**: Authenticated users access `/my-feedback` to see all their past submissions, expand any submission to read the full thread, post follow-up messages, and see an unread badge when an admin has replied.

**Independent Test**: Submit feedback as user → post admin reply → log in as user → navigate to `/my-feedback` → verify submission appears with `has_unread_admin_reply` badge → expand → verify admin reply is visible → type follow-up → Send → verify follow-up appears in thread and admin dashboard shows unread badge on that submission → verify unauthenticated access redirects to login.

### Backend Tests — Write First, Must FAIL Before Implementation

- [x] T019 [P] [US2] Write unit tests for user paths in `formcraft-backend/tests/unit/feedback/test_reply_service.py`: `get_my_feedback` — 5 submissions returned for owner, empty list for user with no submissions, `has_unread_admin_reply=true` when unread notification exists, `has_unread_admin_reply=false` when all notifications read; `post_reply` user path — success, increments `reply_count`, sets `has_unread_user_reply=true`, does NOT insert notification; `get_replies` non-owner → 403
- [x] T020 [P] [US2] Write integration tests in `formcraft-backend/tests/integration/feedback/test_reply_routes.py`: `GET /api/my-feedback` → 200 own submissions only; 401 unauthenticated; `GET /api/feedback/{id}/replies` → 200 own submission; 403 non-owner; 404 bad id; `POST /api/feedback/{id}/replies` → 201; 400 empty text; 403 non-owner; 401 unauthenticated

### Backend Implementation — US2

- [x] T021 [US2] Implement `get_my_feedback(user_id, page, page_size)` in `formcraft-backend/app/services/feedback/reply_service.py`: execute a **single query** — `SELECT s.*, EXISTS(SELECT 1 FROM feedback_notifications n WHERE n.feedback_id = s.id AND n.recipient_user_id = :user_id AND n.read_at IS NULL) AS has_unread_admin_reply FROM feedback_submissions s WHERE s.user_id = :user_id ORDER BY s.submitted_at DESC LIMIT :page_size OFFSET :offset` — one DB round-trip regardless of result count (avoids N+1 per row; satisfies SC-003 at 500 submissions); compute `total` via `SELECT COUNT(*) FROM feedback_submissions WHERE user_id = :user_id`; return `MyFeedbackResponse(results, total, page, page_size)`. Note: thread replies use `before_id` keyset cursor (Decision 5 in research.md); My Feedback uses OFFSET because the user's own submission list is stable and bounded per session
- [x] T022 [US2] Add `GET /api/my-feedback` route to `formcraft-backend/app/api/routes/feedback.py` — authenticated user; query params `page: int = 1`, `page_size: int = 20`; calls `get_my_feedback(user_id=current_user.id, page, page_size)`; returns `MyFeedbackResponse`
- [x] T023 [US2] Add `GET /api/feedback/{id}/replies` route to `formcraft-backend/app/api/routes/feedback.py` — authenticated user; query params `limit: int = 20`, `before_id: UUID | None`; calls `get_replies(feedback_id, user_id=current_user.id, is_admin=False, limit, before_id)`; 403 if non-owner (raised by service); returns `ThreadResponse`
- [x] T024 [US2] Add `POST /api/feedback/{id}/replies` route to `formcraft-backend/app/api/routes/feedback.py` — authenticated user; body `ReplyCreateRequest`; calls `post_reply(feedback_id, author_id=current_user.id, author_role='user', payload)`; 403 if non-owner (raised by service); returns `ReplyResponse` with status 201

### Frontend Implementation — US2

- [x] T025 [US2] Create `MyFeedbackService` in `formcraft-frontend/src/app/features/my-feedback/services/my-feedback.service.ts`: import `MyFeedbackResponse`, `ThreadResponse`, `ReplyResponse`, `NotificationsResponse` from `features/feedback/models/reply.models`; `getMyFeedback(page, pageSize): Observable<MyFeedbackResponse>` → `GET /api/my-feedback`; `getReplies(feedbackId, limit?, beforeId?): Observable<ThreadResponse>` → `GET /api/feedback/{id}/replies`; `postReply(feedbackId, text): Observable<ReplyResponse>` → `POST /api/feedback/{id}/replies`; `getNotifications(): Observable<NotificationsResponse>` → `GET /api/notifications`; `markNotificationRead(id): Observable<void>` → `PATCH /api/notifications/{id}/read`
- [x] T026 [US2] Create `MyFeedbackComponent` in `formcraft-frontend/src/app/features/my-feedback/components/my-feedback/`: `my-feedback.component.ts` — on `ngOnInit` call `MyFeedbackService.getMyFeedback()`; render `mat-expansion-panel` per `MyFeedbackItem`; on panel open → call `getReplies(id)`, subscribe to `FeedbackRealtimeService.subscribeToThread(id)` → append live replies, `takeUntil` close signal; on panel close → `FeedbackRealtimeService.unsubscribeThread(id)`; `onLoadEarlier(beforeId)` → `getReplies(id, 20, beforeId)` prepend; `onSendReply(text)` → `postReply(id, text)`, append returned reply; show `has_unread_admin_reply` badge per panel header; `my-feedback.component.html` — `*ngFor` over results as `mat-expansion-panel`; panel header shows `page_url`, `submitted_at`, `status`, unread badge; panel body shows original `text_content` then `<app-thread>`; empty-state when `results.length === 0`; `my-feedback.component.scss` — panel styles, unread badge, empty state
- [x] T027 [US2] Complete `MyFeedbackModule` in `formcraft-frontend/src/app/features/my-feedback/my-feedback.module.ts`: declare `MyFeedbackComponent`; import `CommonModule`, `MatExpansionModule`, `MatBadgeModule`, `MatProgressSpinnerModule`, `ThreadModule` (or `SharedModule`); provide `MyFeedbackService`; define internal routing with default route → `MyFeedbackComponent`
- [x] T028 [US2] Add `/my-feedback` lazy route to `formcraft-frontend/src/app/app-routing.module.ts`: `{ path: 'my-feedback', loadChildren: () => import('./features/my-feedback/my-feedback.module').then(m => m.MyFeedbackModule), canActivate: [AuthGuard] }` — `AuthGuard` only (NOT `RoleGuard`); add nav item to main sidebar/header template pointing to `/my-feedback`
- [x] T029 [P] [US2] Add US2 i18n keys to `formcraft-frontend/src/assets/i18n/en.json` and `ar.json`: `my_feedback.title`, `my_feedback.empty_state`, `my_feedback.submission_date`, `my_feedback.status`

**Checkpoint**: `/my-feedback` page loads all submissions within 2 s (SC-003), threads expand with live Realtime updates, user can post follow-ups, unread badges drive engagement

---

## Phase 5: User Story 3 — In-App Notifications for Thread Activity (Priority: P3)

**Goal**: Users receive an in-app notification within 5 seconds of an admin reply. Queued notifications surface on next login. The notification badge in the nav links to `/my-feedback`. Admins see unread badges on submissions with new user follow-ups.

**Independent Test**: Open two sessions — admin and user. Admin posts reply → verify user notification badge increments within 5 s (SC-002). Log out user, admin posts second reply, log back in → verify queued notification appears within 3 s (SC-004). Click notification → verify `/my-feedback` opens with correct submission expanded. Post user follow-up → verify admin dashboard shows unread badge. Admin expands thread → verify badge clears without additional action (FR-015, covered in US1).

### Backend Tests — Write First, Must FAIL Before Implementation

- [x] T030 [P] [US3] Write unit tests in `formcraft-backend/tests/unit/feedback/test_reply_service.py`: `get_notifications` — undelivered notifications returned, `delivered_at` set on previously null rows, already-delivered rows included but `delivered_at` not reset, correct `unread_count` (rows where `read_at IS NULL`); `mark_notification_read` — success sets `read_at`, wrong owner → 403, not found → 404
- [x] T031 [P] [US3] Write integration tests in `formcraft-backend/tests/integration/feedback/test_reply_routes.py`: `GET /api/notifications` → 200 own notifications only, `delivered_at` set on previously null rows; 401 unauthenticated; `PATCH /api/notifications/{id}/read` → 204; 403 wrong owner; 404 not found

### Backend Implementation — US3

- [x] T032 [US3] Implement `get_notifications(user_id)` in `formcraft-backend/app/services/feedback/reply_service.py`: SELECT all `feedback_notifications WHERE recipient_user_id = ?` ORDER BY `created_at DESC`; in same transaction UPDATE `delivered_at = NOW() WHERE recipient_user_id = ? AND delivered_at IS NULL`; count rows where `read_at IS NULL` → `unread_count`; return `NotificationsResponse`
- [x] T033 [US3] Implement `mark_notification_read(notification_id, user_id)` in `formcraft-backend/app/services/feedback/reply_service.py`: SELECT notification → 404 if missing; 403 if `recipient_user_id != user_id`; UPDATE `read_at = NOW()`
- [x] T034 [US3] Add `GET /api/notifications` and `PATCH /api/notifications/{id}/read` routes to `formcraft-backend/app/api/routes/feedback.py`: `GET` → authenticated user, calls `get_notifications(current_user.id)`, returns `NotificationsResponse`; `PATCH` → authenticated user, calls `mark_notification_read(notification_id, current_user.id)`, returns 204

### Frontend Implementation — US3

- [x] T035 [US3] Implement `notificationEvents$` global channel and `destroy()` in `formcraft-frontend/src/app/features/feedback/services/feedback-realtime.service.ts`: on service init (constructor), create Supabase channel `notifications:{uid}` subscribing to `postgres_changes INSERT` on `feedback_notifications` with `filter: recipient_user_id=eq.{auth.uid()}`; on event, parse as `NotificationResponse` and emit on `notificationEvents$: Subject<NotificationResponse>`; `destroy()` — iterate all active channels, call `channel.unsubscribe()`, complete subjects, clear map (called on logout)
- [x] T036 [US3] Add notification badge to shell/nav in `formcraft-frontend/src/app/` (app shell component — `app.component.ts` or `shell/shell.component.ts`): on post-auth init call `MyFeedbackService.getNotifications()` → set `unreadCount` from `unread_count`; subscribe to `FeedbackRealtimeService.notificationEvents$` → increment `unreadCount` on each event; render `[matBadge]="unreadCount" matBadgeColor="warn"` on "/my-feedback" nav link; badge hidden when `unreadCount === 0`; unsubscribe on logout
- [x] T037 [US3] Wire notification read and deep-link auto-expand in `MyFeedbackComponent` and nav (implements FR-012 — notification MUST link directly to the relevant thread): **Navigation**: when user clicks notification badge → `router.navigate(['/my-feedback'], { queryParams: { expand: feedbackId } })` where `feedbackId` comes from the `NotificationResponse.feedback_id` of the most-recent unread notification; **Auto-expand on init**: in `MyFeedbackComponent.ngOnInit`, read `ActivatedRoute.queryParams.expand` — if present, after `getMyFeedback()` resolves, find the matching item and programmatically open its `MatExpansionPanel` (hold a `@ViewChildren(MatExpansionPanel)` query list, match by index/id, call `panel.open()`); scroll the panel into view via `panel._body.nativeElement.scrollIntoView({ behavior: 'smooth' })`; **Mark-read**: on `MyFeedbackComponent` init, call `MyFeedbackService.getNotifications()` to identify unread notifications for this session; when user expands a submission panel, call `MyFeedbackService.markNotificationRead(notificationId)` for each unread notification linked to that `feedback_id`; decrement parent `unreadCount` in shell; update local `has_unread_admin_reply` badge to false after mark-read
- [x] T038 [P] [US3] Add US3 i18n keys to `formcraft-frontend/src/assets/i18n/en.json` and `ar.json`: `notifications.badge_title`, `notifications.mark_read`

**Checkpoint**: In-app notification delivered within 5 s (SC-002), queued notifications surface on login within 3 s (SC-004), badge navigates to `/my-feedback`, unread indicators clear on interaction

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T039 [P] Run full backend test suite and fix failures: `cd formcraft-backend && .venv/bin/pytest tests/unit/feedback/test_reply_service.py tests/integration/feedback/test_reply_routes.py -v`
- [x] T040 [P] Run `ruff check .` on all new/modified Python files: `formcraft-backend/app/schemas/reply.py`, `formcraft-backend/app/services/feedback/reply_service.py`, `formcraft-backend/app/api/routes/feedback.py`, `formcraft-backend/app/api/routes/admin.py` — fix all reported issues
- [ ] T041 Manual E2E verification per `formcraft-specs/specs/14-feedback-threading/quickstart.md` Realtime guide: two browser windows (admin + user on `/my-feedback`) — admin posts reply, user thread updates < 1 s (SC-001); admin reply triggers notification badge increment < 5 s (SC-002); user follow-up triggers admin unread badge; admin expands → badge clears; offline notification queuing (SC-004); 25-reply thread → "Load earlier messages" shows 5 more above, scroll anchored
- [ ] T042 [P] Verify `ThreadComponent` renders correctly at 360px viewport — open browser DevTools, set width to 360px, expand a thread with > 5 replies; verify no horizontal overflow, reply textarea usable, Send button reachable, "Load earlier messages" button fully visible

**Checkpoint**: All tests pass, ruff clean, Realtime verified in two-window E2E, mobile viewport confirmed

---

## Dependencies

```
Phase 1 (T001–T002)
  └── Phase 2 (T003–T005)
        ├── Phase 3 US1 (T006–T018)  ← unblocks Phase 4 and Phase 5
        │     ├── T014 (ThreadComponent) ← required by Phase 4 T026
        │     └── T015 (subscribeToThread) ← required by Phase 4 T026
        ├── Phase 4 US2 (T019–T029)  ← depends on T014, T015 from Phase 3
        │     └── T025 (MyFeedbackService) ← required by Phase 5 T036, T037
        └── Phase 5 US3 (T030–T038)  ← depends on T025 from Phase 4
              └── T035 (notificationEvents$) ← completes FeedbackRealtimeService
```

**Cross-phase dependencies:**
- T026 depends on T014 (ThreadComponent) and T015 (subscribeToThread) — Phase 4 cannot begin its frontend tasks until T014 and T015 are complete
- T036 depends on T025 (MyFeedbackService.getNotifications) — shell badge init uses the service
- T009 implements `post_reply` for both admin and user roles in one function — T024 (user route) calls the same service method; no duplicate implementation needed

## Parallel Execution Examples

- **Dev A**: Phase 3 backend (T006–T013) while **Dev B**: Phase 3 frontend scaffolding (T014–T015)
- Once T014 + T015 done: **Dev A** Phase 4 backend (T019–T024) while **Dev B**: Phase 4 frontend (T025–T029)
- Phase 5 backend (T030–T034) and Phase 5 frontend (T035–T038) can be split similarly

---

## Summary

| Phase | Tasks | Notes |
|-------|-------|-------|
| Phase 1 — Setup | T001–T002 | 2 tasks |
| Phase 2 — Foundational | T003–T005 | 3 tasks |
| Phase 3 — US1 Admin Replies | T006–T018 | 13 tasks (incl. 2 test files) |
| Phase 4 — US2 My Feedback | T019–T029 | 11 tasks (incl. 2 test files) |
| Phase 5 — US3 Notifications | T030–T038 | 9 tasks (incl. 2 test files) |
| Phase 6 — Polish | T039–T042 | 4 tasks |
| **Total** | **T001–T042** | **42 tasks** |

- [P] parallelizable: 19 tasks
- Test-writing tasks: 6 (T006, T007, T019, T020, T030, T031)
- MVP scope: T001–T018 (18 tasks — US1 Admin Replies complete, Realtime push verified)
- T026 depends on T014 + T015 (ThreadComponent + subscribeToThread); T036 depends on T025 (MyFeedbackService)
