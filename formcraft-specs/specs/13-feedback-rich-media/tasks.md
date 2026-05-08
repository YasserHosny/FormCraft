# Tasks: Feedback Rich Media

**Input**: Design documents from `formcraft-specs/specs/13-feedback-rich-media/`  
**Branch**: `013-feedback-rich-media` | **Date**: 2026-05-09  
**Prerequisites**: plan.md ✅ · spec.md ✅ · data-model.md ✅ · contracts/api.md ✅ · research.md ✅ · quickstart.md ✅  
**Depends on**: Feature 011 (`001-customer-feedback`) fully applied — `feedback_submissions` table, single-image and audio upload endpoints, and submission widget must exist

**Tests**: Included — consistent with feature 011/012 pattern.

**Organization**: Tasks grouped by user story (P1 Multi-image → P2 Video) so each story is independently implementable, testable, and deployable.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no shared dependencies)
- **[Story]**: User story label (US1 / US2)

## Path Conventions

- Backend: `formcraft-backend/`
- Frontend: `formcraft-frontend/src/app/`

---

## Phase 1: Setup

**Purpose**: Migration, storage bucket config update, and empty file skeletons so subsequent phases have a stable base.

- [x] T001 Write migration `formcraft-backend/supabase/migrations/010_extend_feedback_rich_media.sql` — full SQL from data-model.md: create `feedback_images` table with indexes and RLS; `ALTER TABLE feedback_submissions ADD COLUMN video_url TEXT`; backfill `image_url` → `feedback_images`; `DROP COLUMN image_url`
- [x] T002 [P] Update Supabase Storage `feedback` bucket: raise file size limit to 100 MB; add `video/mp4` and `video/webm` to allowed MIME types — update `formcraft-backend/supabase/config.toml` (or equivalent seed/config file) per quickstart.md instructions
- [x] T003 [P] Create empty file skeletons: `formcraft-backend/tests/unit/feedback/test_rich_media_service.py` (empty), `formcraft-backend/tests/integration/feedback/test_rich_media_routes.py` (empty), `formcraft-frontend/src/app/features/feedback/services/video-recorder.service.ts` (empty)

**Checkpoint**: Migration and empty modules in place — ready to update schemas and write tests

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Updated Pydantic schemas and shared upload/delete service infrastructure. Both user stories depend on this phase.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Update Pydantic models in `formcraft-backend/app/schemas/feedback.py`: add **two** image response schemas — `FeedbackImageSubmitItem(id: UUID, storage_path: str, display_order: int)` (raw Storage path, used in submit response) and `FeedbackImageResponse(id: UUID, storage_url: str, display_order: int)` (signed URL, used in admin list response); update `FeedbackSubmitRequest` — remove `image_url`, add `image_paths: list[str] | None` (max 5 via `@field_validator`), add `video_url: str | None`, add `@model_validator` raising 422 if both `audio_url` and `video_url` are non-null; update `FeedbackSubmitResponse` — replace `image_url` with `images: list[FeedbackImageSubmitItem]`, add `video_url: str | None`; update `FeedbackAdminItem` — replace `image_url` with `images: list[FeedbackImageResponse]`, add `video_url: str | None`
- [x] T005 [P] Add empty method stubs to `formcraft-backend/app/services/feedback/service.py`: `upload_image(user_id, file)`, `upload_video(user_id, file)`, `delete_upload(user_id, storage_path)` — stub bodies raise `NotImplementedError`; update `submit_feedback()` signature to accept `image_paths` and `video_url`; update `list_feedback()` return type to use updated `FeedbackAdminItem` (no implementation yet)
- [x] T006 [P] Add HTTP method stubs to `formcraft-frontend/src/app/features/feedback/services/feedback.service.ts`: `uploadImage(file: File): Observable<{storage_path: string}>`, `uploadVideo(file: File | Blob): Observable<{storage_path: string}>`, `deleteUpload(type: 'image' | 'video', storagePath: string): Observable<void>` — return `EMPTY` observables; update `submitFeedback()` signature to accept `imagePaths: string[] | null` and `videoUrl: string | null` in place of `imageUrl`

**Checkpoint**: Schemas compile, service stubs importable — user story implementation can begin

---

## Phase 3: User Story 1 — Attach Multiple Images (Priority: P1) 🎯 MVP

**Goal**: Users attach up to 5 images (JPEG/PNG/WEBP, 5 MB each) to a single submission. Thumbnails appear instantly via object URLs before upload. Admins see all thumbnails in the dashboard expanded row.

**Independent Test**: Attach three images → verify three thumbnails appear via object URLs → remove one → submit → verify admin dashboard shows exactly two thumbnails for that entry; attach a sixth image → verify block message appears; attach an oversized file → verify rejection without affecting existing attachments.

### Backend Tests — Write First, Must FAIL Before Implementation

- [x] T007 [P] [US1] Write unit tests for image upload and multi-image submit in `formcraft-backend/tests/unit/feedback/test_rich_media_service.py`: `upload_image` success (JPEG), invalid MIME → 400, size > 5 MB → 400; `delete_upload` success, wrong owner → 403, not found → 404; `submit_feedback` with 3 image_paths → 201 with 3 `feedback_images` rows; 6 image_paths → 400; `list_feedback` admin → images array sorted by display_order, signed URLs present on each
- [x] T008 [P] [US1] Write integration tests in `formcraft-backend/tests/integration/feedback/test_rich_media_routes.py`: `POST /api/feedback/upload/image` → 200 with storage_path; invalid MIME → 400; size > 5 MB → 400; unauthenticated → 401; `DELETE /api/feedback/upload/image` → 204; wrong owner → 403; `POST /api/feedback` with `image_paths` (2 items) → 201 with `images` array length 2; more than 5 paths → 400; `GET /api/admin/feedback` → 200 with `images` array (not `image_url`)

### Backend Implementation — US1

- [x] T009 [US1] Implement `upload_image(user_id, file)` in `formcraft-backend/app/services/feedback/service.py` — validate `file.content_type` ∈ {image/jpeg, image/png, image/webp} (→ 400) and `file.size ≤ 5 MB` (→ 400); upload to Supabase Storage at path `feedback/{user_id}/{uuid}.{ext}`; return `storage_path`
- [x] T010 [US1] Implement `delete_upload(user_id, storage_path)` in `formcraft-backend/app/services/feedback/service.py` — verify path starts with `feedback/{user_id}/` (→ 403 otherwise); delete object from Supabase Storage; raise 404 if object not found
- [x] T011 [US1] Add `POST /api/feedback/upload/image` and `DELETE /api/feedback/upload/image` routes to `formcraft-backend/app/api/routes/feedback.py` — call `upload_image()` and `delete_upload()` respectively; validate ownership in DELETE; keep existing audio upload routes untouched
- [x] T012 [US1] Update `submit_feedback()` in `formcraft-backend/app/services/feedback/service.py`: after inserting the `feedback_submissions` row, count entries in `image_paths` (→ 400 if > 5); INSERT one `feedback_images` row per path with `display_order` = list index; return `FeedbackSubmitResponse` with `images: list[FeedbackImageSubmitItem]` — **raw `storage_path` values, no signed URLs** (the client has the file; signing is only needed for admin display)
- [x] T013 [US1] Update `list_feedback()` (admin) in `formcraft-backend/app/services/feedback/service.py`: LEFT JOIN `feedback_images` on `feedback_id`, aggregate into `images` list ordered by `display_order ASC`; generate Supabase signed URLs (1-hour expiry) for each `storage_path` → set as `storage_url` on `FeedbackImageResponse`; return `FeedbackAdminItem` with `images: list[FeedbackImageResponse]` — **signed URLs, not raw paths**; remove `image_url` from response; add `video_url: None` placeholder (US2 will populate)
- [x] T014 [US1] Update `GET /api/admin/feedback` route in `formcraft-backend/app/api/routes/admin.py` to serialise with updated `FeedbackAdminItem` (images array, no image_url); no new query params at this stage

### Frontend Implementation — US1

- [x] T015 [US1] Implement `uploadImage()` and the full `deleteUpload(type, storagePath)` method in `formcraft-frontend/src/app/features/feedback/services/feedback.service.ts`: `uploadImage` → `POST /api/feedback/upload/image` (multipart); `deleteUpload(type: 'image' | 'video', storagePath: string)` — when `type === 'image'` → `DELETE /api/feedback/upload/image` with body `{storage_path: storagePath}`; when `type === 'video'` → `DELETE /api/feedback/upload/video` with body `{storage_path: storagePath}` (video branch called in T029); update `submitFeedback()` to accept `imagePaths: string[] | null` in place of `imageUrl`
- [x] T016 [P] [US1] Add multi-image state to `formcraft-frontend/src/app/features/feedback/components/feedback-widget/feedback-widget.component.ts`: `stagedImages: { file: File; objectUrl: string; storagePath?: string }[]`; `addImage(file: File)` — validate MIME + size ≤ 5 MB, create `URL.createObjectURL()`, push to array (guard: length < 5); `removeImage(index: number)` — revoke object URL, call `deleteUpload('image', stagedImages[index].storagePath)` if `storagePath` is set, splice array; `clearImages()` for destroy/abort
- [x] T017 [US1] Add thumbnail grid to `formcraft-frontend/src/app/features/feedback/components/feedback-widget/feedback-widget.component.html`: `<input type="file" accept="image/jpeg,image/png,image/webp" multiple>`; CSS grid of thumbnails via `*ngFor` over `stagedImages`; individual `×` remove button per thumbnail; "5 image limit reached" inline message when `stagedImages.length >= 5`; update `feedback-widget.component.scss` for thumbnail grid and remove button styles
- [x] T018 [US1] Wire sequential image uploads on Submit in `feedback-widget.component.ts`: iterate `stagedImages` in order, call `uploadImage(file)` for each; on first attempt failure retry once (single retry per image); on persistent failure surface per-image error with "Remove image / Try again" option; collect `storage_path` values into `imagePaths` array for submit payload; preserve existing text + audio upload logic
- [x] T019 [US1] Wire abort/destroy cleanup for images in `feedback-widget.component.ts`: on widget close, navigation away (`ngOnDestroy`), or submission failure → call `deleteUpload('image', entry.storagePath)` for each `stagedImages` entry that has a `storagePath`; revoke all object URLs
- [x] T020 [US1] Update `formcraft-frontend/src/app/features/feedback/components/feedback-admin/feedback-admin.component.html` expanded row: replace single `<img>` / image link with a `*ngFor` thumbnail grid over `submission.images`; each thumbnail is a `<button>` that opens a full-size view (Angular Material dialog or `window.open` signed URL) on click; render nothing for submissions with empty `images` array
- [x] T021 [US1] Add US1 i18n keys to `formcraft-frontend/src/assets/i18n/en.json` and `ar.json`: `feedback.images.attach`, `feedback.images.remove`, `feedback.images.limit_reached`, `feedback.images.upload_failed`, `feedback.images.retry`, `feedback.images.view_full`

**Checkpoint**: Multi-image submission fully functional — up to 5 thumbnails appear instantly via object URLs, sequential upload on submit, orphan cleanup on abort, admin thumbnail grid with full-size view → **MVP deliverable**

---

## Phase 4: User Story 2 — Submit Video Feedback (Priority: P2)

**Goal**: Users record a video (up to 2 minutes) directly in the browser or upload an existing MP4/WebM file (up to 100 MB). A playback preview appears before submission. Audio and video are mutually exclusive per submission. Admins see an inline video player in the expanded row.

**Independent Test**: Record a 30-second video → verify elapsed timer shows → stop recording → play preview → submit → verify admin expanded row shows `<video controls>` player; confirm record button is hidden in a browser without MediaRecorder support; confirm video section is disabled when audio is already attached.

### Backend Tests — Write First, Must FAIL Before Implementation

- [x] T022 [P] [US2] Write unit tests for video upload and submit in `formcraft-backend/tests/unit/feedback/test_rich_media_service.py`: `upload_video` success (MP4), success (WebM), size > 100 MB → 400, invalid MIME (e.g. video/avi) → 400; `submit_feedback` with `video_url` and no `audio_url` → 201; both `audio_url` and `video_url` non-null → 422; `list_feedback` admin → `video_url` signed URL present when set
- [x] T023 [P] [US2] Write integration tests in `formcraft-backend/tests/integration/feedback/test_rich_media_routes.py`: `POST /api/feedback/upload/video` → 200 with storage_path; invalid MIME → 400; size > 100 MB → 400; unauthenticated → 401; `DELETE /api/feedback/upload/video` → 204; wrong owner → 403; `POST /api/feedback` with `video_url` (no audio_url) → 201; `POST /api/feedback` with both `audio_url` and `video_url` non-null → 422; `GET /api/admin/feedback` → 200 with `video_url` signed URL on relevant rows

### Backend Implementation — US2

- [x] T024 [US2] Implement `upload_video(user_id, file)` in `formcraft-backend/app/services/feedback/service.py` — validate `file.content_type` ∈ {video/mp4, video/webm} (→ 400) and `file.size ≤ 100 MB` (→ 400); upload to Supabase Storage at path `feedback/{user_id}/{uuid}.{ext}`; return `storage_path`
- [x] T025 [US2] Add `POST /api/feedback/upload/video` and `DELETE /api/feedback/upload/video` routes to `formcraft-backend/app/api/routes/feedback.py` — call `upload_video()` and `delete_upload()` respectively; `DELETE` reuses the existing `delete_upload()` service method (path ownership validated)
- [x] T026 [US2] Update `submit_feedback()` in `formcraft-backend/app/services/feedback/service.py` to persist `video_url` on the `feedback_submissions` row; confirm the `@model_validator` in `FeedbackSubmitRequest` (T004) is exercised — no new validator code needed here, just ensure the service passes through 422 from Pydantic on mutual-exclusion violation
- [x] T027 [US2] Update `list_feedback()` (admin) in `formcraft-backend/app/services/feedback/service.py` to include `video_url` — generate Supabase signed URL (1-hour expiry) when `video_url` is non-null, pass `None` otherwise; no change needed to route handler (schema already updated in T004)

### Frontend Implementation — US2

- [x] T028 [US2] Implement `VideoRecorderService` in `formcraft-frontend/src/app/features/feedback/services/video-recorder.service.ts`: `canRecord$: Observable<boolean>` via `MediaRecorder.isTypeSupported('video/webm;codecs=vp8')` (build-time browser capability check); `permissionError$: Subject<void>` — emitted when `getUserMedia()` rejects with `NotAllowedError` or `NotFoundError` (runtime permission denied — distinct from capability check); `start()` — request `getUserMedia({video: true, audio: true})`, catch `NotAllowedError`/`NotFoundError` → emit on `permissionError$` and return without starting recorder, create `MediaRecorder` (prefer `video/webm;codecs=vp8`, fallback `video/mp4`), collect `Blob` chunks, set 2-minute auto-stop `setTimeout`; `stop()` — stop recorder, assemble `Blob`, produce `objectUrl`, emit via `recordingBlob$: Subject<Blob>`; `elapsedSeconds$: Observable<number>` — RxJS `interval(1000)` active between `start()` and `stop()`; `cleanup()` — stop all `MediaStream` tracks, revoke object URL, clear timer
- [x] T029 [US2] Add `uploadVideo()` and `deleteUpload('video')` to `formcraft-frontend/src/app/features/feedback/services/feedback.service.ts`: `uploadVideo(file: File | Blob): Observable<{storage_path: string}>` → `POST /api/feedback/upload/video` (multipart); `deleteUpload('video', storage_path)` → `DELETE /api/feedback/upload/video`; update `submitFeedback()` to include `video_url` in payload
- [x] T030 [P] [US2] Add video state to `formcraft-frontend/src/app/features/feedback/components/feedback-widget/feedback-widget.component.ts`: `stagedVideo: { blob?: Blob; file?: File; objectUrl?: string; storagePath?: string } | null`; `startRecording()`, `stopRecording()`, `reRecord()` delegating to `VideoRecorderService`; `attachVideoFile(file: File)` — validate MIME + size ≤ 100 MB, create object URL, set `stagedVideo`; `clearVideo()` — call `deleteUpload('video')` if `storagePath` set, revoke object URL, reset state
- [x] T031 [US2] Add video controls to `formcraft-frontend/src/app/features/feedback/components/feedback-widget/feedback-widget.component.html` and `feedback-widget.component.ts`: Record button (hidden when `!(canRecord$ | async)`, replaced by tooltip "Browser does not support recording"); Stop button (shown during recording); elapsed timer display `mm:ss`; `<video controls>` preview when `stagedVideo.objectUrl` set; Re-record button; file upload `<input type="file" accept="video/mp4,video/webm">`; subscribe to `VideoRecorderService.permissionError$` in `ngOnInit` — when emitted, set local `recordingPermissionDenied = true`, hide Record button, show inline tooltip bound to `feedback.video.permission_denied` i18n key ("Camera/microphone access was denied — use the upload option instead."); file upload input remains enabled regardless of `recordingPermissionDenied`; update `feedback-widget.component.scss` for video preview + timer + permission-denied tooltip styles
- [x] T032 [US2] Implement audio/video mutual exclusion in `feedback-widget.component.ts` and `.html`: when `stagedVideo` is set → show disabled overlay on audio section with message `feedback.media.audio_exclusive`; when `audio_url` is staged → show disabled overlay on video section with message `feedback.media.video_exclusive`; use `[disabled]` binding and ARIA `aria-disabled` attribute
- [x] T033 [US2] Wire video upload on Submit in `feedback-widget.component.ts`: call `uploadVideo(stagedVideo.blob ?? stagedVideo.file)` when `stagedVideo` is set; retry once on failure; on persistent failure surface error with "Remove video and submit without it" recovery option (clears `stagedVideo` and proceeds with text + images + audio only); set `video_url` in submit payload on success
- [x] T034 [US2] Wire abort/destroy cleanup for video in `feedback-widget.component.ts`: on widget close, navigation away (`ngOnDestroy`), or submission failure → call `VideoRecorderService.cleanup()` (stops stream tracks, revokes object URL); call `deleteUpload('video')` if `storagePath` is set
- [x] T035 [US2] Update `formcraft-frontend/src/app/features/feedback/components/feedback-admin/feedback-admin.component.html` expanded row: add `<video controls [src]="submission.video_url" *ngIf="submission.video_url">` inline player; add fallback "Download video" link for browsers that cannot play the format
- [x] T036 [P] [US2] Add US2 i18n keys to `formcraft-frontend/src/assets/i18n/en.json` and `ar.json`: `feedback.video.record`, `feedback.video.stop`, `feedback.video.re_record`, `feedback.video.upload`, `feedback.video.no_support`, `feedback.video.permission_denied` (**NEW** — "Camera/microphone access was denied — use the upload option instead."), `feedback.video.preview`, `feedback.video.upload_failed`, `feedback.video.remove_and_submit`, `feedback.media.audio_exclusive`, `feedback.media.video_exclusive`

**Checkpoint**: Video fully functional — in-browser recording with 2-minute cap, file upload, playback preview, mutual exclusion with audio, admin inline player; delete-on-abort keeps storage clean

---

## Phase 5: Polish & Cross-Cutting Concerns

- [x] T037 [P] Run full backend test suite and fix failures: `pytest formcraft-backend/tests/unit/feedback/test_rich_media_service.py formcraft-backend/tests/integration/feedback/test_rich_media_routes.py -v`
- [x] T038 [P] Run `ruff check .` on all new/modified backend Python files and fix violations: `formcraft-backend/app/schemas/feedback.py`, `formcraft-backend/app/services/feedback/service.py`, `formcraft-backend/app/api/routes/feedback.py`, `formcraft-backend/app/api/routes/admin.py`
- [x] T039 [P] Verify thumbnail grid and video controls render correctly at 360px viewport width — check `feedback-widget.component.scss` for thumbnail wrapping and video preview sizing; verify admin expanded row renders thumbnails and video player without overflow
- [ ] T040 Manual E2E validation per `quickstart.md`: apply migration → attach 5 images (verify 5 thumbnails) → remove 1 → submit → verify admin shows 4 thumbnails with full-size click → abandon widget mid-draft (verify no orphan files) → attach audio → verify video section disabled → remove audio → record 2-min video (verify auto-stop at cap) → play preview → submit → verify admin inline player → verify Chrome, Firefox, Safari all render video player

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    └── Phase 2 (Foundational)   ← BLOCKS both user stories
            ├── Phase 3 (US1 — Multi-image)   🎯 MVP
            │       └── Phase 4 (US2 — Video)
            └── Phase 5 (Polish) ← after all desired stories complete
```

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2 — no story dependencies
- **US2 (P2)**: Starts after Phase 2 — requires storage bucket update (T002) for video MIME types; extends submit payload and admin response built in US1 (`submit_feedback()` from T012, `list_feedback()` from T013 are extended rather than replaced in T026 and T027); `FeedbackService` video methods (T029) extend the service file touched in T015

### Within Each User Story

1. Write tests first → confirm they FAIL
2. Pydantic schemas (Phase 2) before service implementation
3. Service methods before route handlers
4. Backend complete before wiring Angular HTTP calls
5. Angular service wired before building component interactions
6. i18n keys added as last step per story

---

## Parallel Opportunities

### Phase 1

```
T002 (bucket config) ‖ T003 (file skeletons)
```

### Phase 2

```
T005 (service stubs) ‖ T006 (Angular service stubs)
```

### Phase 3 (US1)

```
# Tests (write in parallel):
T007 (unit tests) ‖ T008 (integration tests)

# Frontend (after backend complete):
T015 (component state) ‖ T016 (not yet — T016 needs T015's template data) → sequential
T015 → T016 → T017 → T018 (sequential: each depends on prior)
T020 (admin row) ‖ T021 (i18n) — independent of widget implementation
```

### Phase 4 (US2)

```
# Tests (write in parallel):
T022 (unit tests) ‖ T023 (integration tests)

# Backend:
T024 (upload_video) ‖ T025 (routes) — T025 depends on T024, but can draft simultaneously
T026 (submit video_url) depends on T012 (submit_feedback base)
T027 (admin video_url) depends on T013 (list_feedback base)

# Frontend (after backend complete):
T028 (VideoRecorderService) ‖ T029 (FeedbackService video methods) — independent files
T030 (component state) → T031 (template) → T032 (mutual exclusion) → T033 (upload on submit)
T035 (admin player) ‖ T036 (i18n) — independent of widget
```

### Phase 5

```
T037 (pytest) ‖ T038 (ruff) ‖ T039 (responsive check)
```

---

## Implementation Strategy

### MVP First (US1 Only)

1. Phase 1: Setup (T001–T003)
2. Phase 2: Foundational (T004–T006)
3. Phase 3: US1 — Multiple Images (T007–T021)
4. **STOP and VALIDATE**: Up to 5 thumbnails via object URLs, sequential upload, orphan cleanup, admin multi-thumbnail grid
5. Ship/demo MVP

### Incremental Delivery

| Milestone | Phases | Deliverable |
|-----------|--------|-------------|
| MVP | 1 + 2 + 3 | Multi-image attachment with instant previews, admin grid |
| v1 | + 4 | Video recording/upload, 2-min cap, inline admin player, mutual exclusion |
| Release | + 5 | Hardened, cross-browser, E2E validated |

### Parallel Team Strategy

With two developers after Phase 2 completes:

- **Dev A**: Phase 3 backend (T007–T014) while **Dev B**: Phase 3 frontend (T015–T021)
- Phase 4 can be split the same way; T026 must follow T012, T027 must follow T013

---

## Summary

| Phase | Tasks | Notes |
|-------|-------|-------|
| Phase 1 — Setup | T001–T003 | 3 tasks |
| Phase 2 — Foundational | T004–T006 | 3 tasks |
| Phase 3 — US1 Multi-image | T007–T021 | 15 tasks (incl. 2 test files) |
| Phase 4 — US2 Video | T022–T036 | 15 tasks (incl. 2 test files) |
| Phase 5 — Polish | T037–T040 | 4 tasks |
| **Total** | **T001–T040** | **40 tasks** |

- [P] parallelizable: 18 tasks
- Test-writing tasks: 4 (T007, T008, T022, T023)
- MVP scope: T001–T021 (21 tasks — US1 complete)
- T026 depends on T012 (submit_feedback base); T027 depends on T013 (list_feedback base) — must be sequential within their branches
