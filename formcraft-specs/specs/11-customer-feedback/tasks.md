# Tasks: Customer Feedback

**Input**: Design documents from `formcraft-specs/specs/11-customer-feedback/`  
**Branch**: `001-customer-feedback` | **Date**: 2026-05-07  
**Prerequisites**: plan.md ✅ · spec.md ✅ · data-model.md ✅ · contracts/api.md ✅ · research.md ✅ · wireframes.md ✅ · quickstart.md ✅

**Tests**: Included — plan.md Phase 2 specifies TDD (write tests first, ensure they fail before implementation).

**Organization**: Tasks grouped by user story (P1 → P2 → P3) so each story is independently implementable, testable, and deployable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[Story]**: User story label (US1 / US2 / US3)

## Path Conventions

- Backend: `formcraft-backend/`
- Frontend: `formcraft-frontend/src/app/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create the database schema, storage bucket, and empty file skeletons so all subsequent phases have a stable foundation to build on.

- [x] T001 Write migration `formcraft-backend/supabase/migrations/008_create_feedback_submissions.sql` — full SQL from data-model.md (table, indexes, RLS policies, `profiles` JOIN pattern)
- [x] T002 Document Supabase feedback storage bucket creation in `formcraft-specs/specs/11-customer-feedback/quickstart.md` (bucket name `feedback`, private, MIME allowlist, RLS)
- [x] T003 [P] Create backend file skeletons (empty modules): `formcraft-backend/app/schemas/feedback.py`, `formcraft-backend/app/services/feedback/__init__.py`, `formcraft-backend/app/services/feedback/service.py`, `formcraft-backend/app/api/routes/feedback.py`, `formcraft-backend/tests/unit/feedback/__init__.py`, `formcraft-backend/tests/integration/feedback/__init__.py`
- [x] T004 [P] Create frontend feature module skeleton: `formcraft-frontend/src/app/features/feedback/feedback.module.ts`, `formcraft-frontend/src/app/features/feedback/services/feedback.service.ts`, `formcraft-frontend/src/app/features/feedback/services/audio-recorder.service.ts`, stub component folders for `feedback-widget/` and `feedback-admin/`

**Checkpoint**: Migration file and empty modules in place — ready to write schemas and tests

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Pydantic schemas, service skeleton with Supabase client wiring, and Angular service HTTP skeleton. These are shared by all user stories and must be complete before any story implementation begins.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T005 Write all Pydantic request/response models in `formcraft-backend/app/schemas/feedback.py`: `FeedbackUploadResponse`, `FeedbackSubmitRequest`, `FeedbackSubmitResponse`, `FeedbackAdminItem`, `FeedbackAdminListResponse`, `FeedbackStatusUpdateRequest`, `FeedbackDeleteUploadRequest`
- [x] T006 [P] Wire Supabase client into `FeedbackService` class in `formcraft-backend/app/services/feedback/service.py` — constructor, client injection, no business logic yet
- [x] T007 [P] Declare Angular `FeedbackService` HTTP method stubs in `formcraft-frontend/src/app/features/feedback/services/feedback.service.ts` — `submitFeedback()`, `uploadImage()`, `uploadAudio()`, `deleteUpload()`, `listFeedback()`, `updateStatus()` (no implementation, return `EMPTY` observables)
- [x] T008 Register `feedback.router` in `formcraft-backend/app/main.py` under `/api/feedback`

**Checkpoint**: Schemas compiled, service skeleton importable, router registered — user story implementation can now begin

---

## Phase 3: User Story 1 — Submit Text Feedback (Priority: P1) 🎯 MVP

**Goal**: Authenticated users can open the floating widget, type a message, submit it, and receive a success confirmation. Admins can view all text-only submissions and update their status.

**Independent Test**: Open widget on any page → type message → click Submit → see success screen. Open `/admin/feedback` as admin → see the submission in the table.

### Backend Tests — Write First, Must FAIL Before Implementation

- [x] T009 [P] [US1] Write unit tests for `submit_feedback()` in `formcraft-backend/tests/unit/feedback/test_feedback_service.py`: cooldown blocks within 30 s, cooldown allows after 30 s, empty text rejected, text > 2000 chars rejected, null image/audio accepted
- [x] T010 [P] [US1] Write integration tests for submission route in `formcraft-backend/tests/integration/feedback/test_feedback_route.py`: `POST /api/feedback` → 201 valid, 429 cooldown, 401 unauthenticated, 400 empty text
- [x] T011 [P] [US1] Write integration tests for admin route in `formcraft-backend/tests/integration/feedback/test_admin_feedback_route.py`: `GET /api/admin/feedback` → 200 paginated (admin), 403 non-admin; `PATCH /api/admin/feedback/{id}` → 200 updated, 400 invalid status, 404 not found

### Backend Implementation — US1

- [x] T012 [US1] Implement `submit_feedback(user_id, payload)` in `formcraft-backend/app/services/feedback/service.py` — cooldown check via `(user_id, submitted_at)` index query, insert row, return id + submitted_at + status
- [x] T013 [US1] Implement `list_feedback(filters, page, limit)` in `formcraft-backend/app/services/feedback/service.py` — paginated query, JOIN `profiles` on `user_id` for `submitter_display_name` (fallback to email), return signed URLs for image/audio
- [x] T014 [US1] Implement `update_status(id, status)` in `formcraft-backend/app/services/feedback/service.py` — PATCH row, return id + status, 404 if not found
- [x] T015 [US1] Implement `POST /api/feedback` endpoint in `formcraft-backend/app/api/routes/feedback.py` — auth guard, call `submit_feedback()`, map 429 cooldown response
- [x] T016 [US1] Implement `GET /api/admin/feedback` and `PATCH /api/admin/feedback/{id}` in `formcraft-backend/app/api/routes/admin.py` — `require_role(Role.ADMIN)`, call service methods

### Frontend Implementation — US1

- [x] T017 [P] [US1] Build `FeedbackWidgetComponent` text-only state in `formcraft-frontend/src/app/features/feedback/components/feedback-widget/` — floating FAB (bottom-right), modal overlay, textarea with 2000-char counter, submit/cancel buttons, success state (wireframes §1, §2, §8)
- [x] T018 [US1] Implement error states in `FeedbackWidgetComponent` in `formcraft-frontend/src/app/features/feedback/components/feedback-widget/feedback-widget.component.ts`: (a) cooldown — show inline 429 message with countdown timer (wireframes §9); (b) offline — detect `navigator.onLine` before submit and listen for the `offline` event; if offline, show error "You appear to be offline — please check your connection and try again" and keep form content intact (EC-001: do not silently lose the submission)
- [x] T019 [US1] Wire `submitFeedback()` HTTP call in `formcraft-frontend/src/app/features/feedback/services/feedback.service.ts`
- [x] T020 [P] [US1] Build `FeedbackAdminComponent` text table in `formcraft-frontend/src/app/features/feedback/components/feedback-admin/` — columns: date, user, page, text (truncated + expand on click), status chip + dropdown; status filter chips (wireframes §10, §11)
- [x] T021 [US1] Wire `listFeedback()` and `updateStatus()` HTTP calls in `formcraft-frontend/src/app/features/feedback/services/feedback.service.ts`
- [x] T022 [US1] Mount `<fc-feedback-widget>` in `formcraft-frontend/src/app/app.component.html` — visible only to authenticated users
- [x] T023 [US1] Add `/admin/feedback` route with admin role guard in `formcraft-frontend/src/app/app-routing.module.ts`
- [x] T024 [US1] Add i18n keys for US1 (widget title, placeholder, char counter, submit, cancel, success message, cooldown message, admin column headers) to `formcraft-frontend/src/assets/i18n/ar.json` and `en.json`

**Checkpoint**: Text feedback fully functional end-to-end — widget submits, admin views and updates status → **MVP deliverable**

---

## Phase 4: User Story 2 — Attach an Image (Priority: P2)

**Goal**: Users can attach a JPEG/PNG/WEBP image (≤ 5 MB) to their feedback, see a thumbnail preview, and submit. Admins see image thumbnails in the dashboard.

**Independent Test**: Open widget → type message → attach a valid image → see thumbnail → submit → open admin dashboard → verify image thumbnail appears.

### Backend Tests — Write First, Must FAIL Before Implementation

- [x] T025 [P] [US2] Write unit tests for `upload_file()` and `delete_file()` in `formcraft-backend/tests/unit/feedback/test_feedback_service.py`: valid image stored, image URL linked to submission, oversized rejected, bad MIME rejected
- [x] T026 [P] [US2] Write integration tests for image upload in `formcraft-backend/tests/integration/feedback/test_feedback_route.py`: `POST /api/feedback/upload/image` → 200 valid, 413 oversized, 400 bad MIME, 401 unauth; `DELETE /api/feedback/upload` → 204 own file, 400 foreign path

### Backend Implementation — US2

- [x] T027 [US2] Implement `upload_file(user_id, file, bucket_path)` in `formcraft-backend/app/services/feedback/service.py` — MIME + size validation, Supabase Storage PUT, return storage path
- [x] T028 [US2] Implement `delete_file(user_id, storage_path)` in `formcraft-backend/app/services/feedback/service.py` — validate path belongs to user_id prefix, Supabase Storage DELETE
- [x] T029 [US2] Implement `POST /api/feedback/upload/image` and `DELETE /api/feedback/upload` in `formcraft-backend/app/api/routes/feedback.py` — JPEG/PNG/WEBP, ≤ 5 MB; DELETE validates ownership

### Frontend Implementation — US2

- [x] T030 [P] [US2] Add image section to `FeedbackWidgetComponent` in `formcraft-frontend/src/app/features/feedback/components/feedback-widget/feedback-widget.component.ts` — file picker, client-side MIME/size validation, thumbnail preview, remove button, validation error message (wireframes §3, §4)
- [x] T031 [US2] Wire `uploadImage()` and `deleteUpload()` in `formcraft-frontend/src/app/features/feedback/services/feedback.service.ts` with full failure handling (EC-002): on upload HTTP error, **retry once automatically**; if the retry also fails, surface inline error offering two options — "Remove image and submit text only" (calls `deleteUpload()` then proceeds) or "Try again"; on user-initiated cancel or navigation away after a successful upload, call `deleteUpload()` to remove the orphaned object (research.md Decision 8)
- [x] T032 [US2] Update `FeedbackAdminComponent` to render image thumbnail column with lightbox in `formcraft-frontend/src/app/features/feedback/components/feedback-admin/feedback-admin.component.html`
- [x] T033 [US2] Add i18n keys for image attachment (add image, remove, invalid format, file too large) to `formcraft-frontend/src/assets/i18n/ar.json` and `en.json`

**Checkpoint**: Image attachment end-to-end functional; orphan cleanup on abort works; admin thumbnail visible

---

## Phase 5: User Story 3 — Record and Submit Audio (Priority: P3)

**Goal**: Users can record a voice message (up to 2 min via MediaRecorder) or upload a pre-recorded file (MP3/M4A/WAV/WebM, ≤ 10 MB), preview playback, and submit. Browsers without MediaRecorder show file-upload only.

**Independent Test**: Open widget → click Record → speak → Stop → hear playback → submit → admin dashboard shows audio playback control.

### Backend Tests — Write First, Must FAIL Before Implementation

- [x] T034 [P] [US3] Write unit tests for audio upload in `formcraft-backend/tests/unit/feedback/test_feedback_service.py`: valid MP3 accepted, valid WebM accepted, oversized rejected, bad MIME rejected, audio URL linked to submission
- [x] T035 [P] [US3] Write integration tests for audio upload in `formcraft-backend/tests/integration/feedback/test_feedback_route.py`: `POST /api/feedback/upload/audio` → 200 valid MP3, 200 valid WebM, 413 oversized, 400 bad MIME, 401 unauth

### Backend Implementation — US3

- [x] T036 [US3] Implement `POST /api/feedback/upload/audio` in `formcraft-backend/app/api/routes/feedback.py` — MP3/M4A/WAV/WebM, ≤ 10 MB, reuse `upload_file()` service

### Frontend Implementation — US3

- [x] T037 [P] [US3] Build `AudioRecorderService` in `formcraft-frontend/src/app/features/feedback/services/audio-recorder.service.ts` — MediaRecorder lifecycle (start, stop, auto-stop at 2 min), elapsed timer, WebM blob output, browser-support detection
- [x] T038 [US3] Add audio section to `FeedbackWidgetComponent` in `formcraft-frontend/src/app/features/feedback/components/feedback-widget/feedback-widget.component.ts` — record button (shown only when MediaRecorder supported), recording state with elapsed/cap bar, playback preview with re-record, file upload input (MP3/M4A/WAV/WebM), browser-unsupported fallback (wireframes §5, §6, §7)
- [x] T039 [US3] Wire `uploadAudio()` in `formcraft-frontend/src/app/features/feedback/services/feedback.service.ts` — call delete on submission failure (orphan cleanup)
- [x] T040 [US3] Update `FeedbackAdminComponent` to show audio playback control column in `formcraft-frontend/src/app/features/feedback/components/feedback-admin/feedback-admin.component.html`
- [x] T041 [US3] Add i18n keys for audio recording (add audio, record, stop, re-record, upload file, recording in progress, microphone denied) to `formcraft-frontend/src/assets/i18n/ar.json` and `en.json`

**Checkpoint**: All three user stories fully functional; audio records, previews, submits, and appears in admin dashboard

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Hardening, responsiveness, and full end-to-end validation across all stories

- [x] T042 [P] Add 300 ms debounce on Submit button and disable-during-upload state in `formcraft-frontend/src/app/features/feedback/components/feedback-widget/feedback-widget.component.ts`
- [x] T043 [P] Verify responsive layout at 360px: image and audio buttons stack vertically, FAB shrinks to icon-only, modal fills viewport width per wireframes.md mobile section (FR-012) — update SCSS in `feedback-widget.component.scss`
- [x] T044 [P] Run full backend test suite and fix failures: `pytest formcraft-backend/tests/unit/feedback/ formcraft-backend/tests/integration/feedback/ -v`
- [x] T045 [P] Run `ruff check .` on all new backend Python files and fix any violations
- [x] T046 Manual E2E validation per `quickstart.md`: apply migration → create bucket → submit text-only → submit with image → submit with recorded audio → submit with uploaded audio file → check admin dashboard → change status → verify 30 s cooldown blocks rapid second submission

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    └── Phase 2 (Foundational)   ← BLOCKS all user stories
            ├── Phase 3 (US1 — Text)       🎯 MVP
            │       └── Phase 4 (US2 — Image)
            │               └── Phase 5 (US3 — Audio)
            └── Phase 6 (Polish) ← after all desired stories complete
```

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2 — no story dependencies
- **US2 (P2)**: Starts after Phase 2 — integrates with US1 widget and admin components (extends them, does not replace)
- **US3 (P3)**: Starts after Phase 2 — integrates with US1 widget and admin components (extends them, does not replace)

### Within Each User Story

1. Write tests first → confirm they FAIL
2. Models / schemas already done in Phase 2
3. Service methods before route handlers
4. Backend complete before wiring Angular HTTP calls
5. Angular service wired before building component interactions
6. i18n keys added as last step per story

---

## Parallel Opportunities

### Phase 1

```
T003 (backend skeletons) ‖ T004 (frontend skeletons)
```

### Phase 2

```
T006 (service skeleton) ‖ T007 (Angular service stubs)
```

### Phase 3 (US1)

```
# Tests (write in parallel):
T009 (unit tests) ‖ T010 (feedback route integration tests) ‖ T011 (admin route integration tests)

# Frontend (after backend complete):
T017 (widget text state) ‖ T020 (admin text table)
```

### Phase 4 (US2)

```
# Tests:
T025 (upload unit tests) ‖ T026 (upload integration tests)

# Frontend (after backend complete):
T030 (image picker widget) — T032 (admin thumbnail) — sequential (same component file)
```

### Phase 5 (US3)

```
# Tests:
T034 (audio unit tests) ‖ T035 (audio integration tests)

# Frontend (after backend complete):
T037 (AudioRecorderService) ‖ T038 (audio widget section — depends on T037)
```

### Phase 6

```
T042 (debounce) ‖ T043 (responsive) ‖ T044 (pytest) ‖ T045 (ruff)
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Phase 1: Setup (T001–T004)
2. Phase 2: Foundational (T005–T008)
3. Phase 3: US1 — Text Feedback (T009–T024)
4. **STOP and VALIDATE**: Submit text feedback end-to-end; admin views and changes status
5. Ship/demo MVP

### Incremental Delivery

| Milestone | Phases | Deliverable |
|-----------|--------|-------------|
| MVP | 1 + 2 + 3 | Text feedback widget + admin dashboard |
| v1.1 | + 4 | Image attachments |
| v1.2 | + 5 | Audio recording + file upload |
| v1 | + 6 | Hardened, responsive, E2E validated |

### Parallel Team Strategy

With two developers after Phase 2 completes:
- **Dev A**: Phase 3 backend (T009–T016) while **Dev B**: Phase 3 frontend (T017–T024)
- Phases 4 and 5 can each be split the same way

---

## Summary

| Phase | Tasks | Notes |
|-------|-------|-------|
| Phase 1 — Setup | T001–T004 | 4 tasks |
| Phase 2 — Foundational | T005–T008 | 4 tasks |
| Phase 3 — US1 Text | T009–T024 | 16 tasks (incl. 3 test files) |
| Phase 4 — US2 Image | T025–T033 | 9 tasks (incl. 2 test files) |
| Phase 5 — US3 Audio | T034–T041 | 8 tasks (incl. 2 test files) |
| Phase 6 — Polish | T042–T046 | 5 tasks |
| **Total** | **T001–T046** | **46 tasks** |

- [P] parallelizable: 22 tasks
- Tests: 7 test-writing tasks (T009, T010, T011, T025, T026, T034, T035)
- MVP scope: T001–T024 (24 tasks)
