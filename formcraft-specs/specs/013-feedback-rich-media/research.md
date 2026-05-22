# Research: Feedback Rich Media

**Branch**: `013-feedback-rich-media` | **Phase**: 0

## Decision Log

---

### 1. Migration Numbering

**Decision**: `010_extend_feedback_rich_media.sql` — next sequential number after feature 012's `009_create_feedback_labels.sql`.

**Rationale**: Follows the established `001…00N` sequential convention. Feature 013 depends on both 011 (base submissions) and 012 (labels), so 010 is the next available slot.

**Alternatives considered**:
- Separate migrations for table create vs. alter: adds no value for a coordinated feature; one migration file keeps the schema change atomic.

---

### 2. Image Table vs. Column Array

**Decision**: A dedicated `feedback_images` table with one row per image, replacing the single `image_url` TEXT column on `feedback_submissions`.

**Rationale**: A normalised table supports independent retrieval (FR-006), ordered display (`display_order`), and future per-image metadata (alt text, caption) without schema changes. A PostgreSQL array column would require unnesting for queries and makes per-image deletion awkward.

**Alternatives considered**:
- `TEXT[]` array column: compact but loses per-image metadata and complicates DELETE of individual images.
- JSONB column: flexible but opaque to SQL queries and FK constraints.

---

### 3. Image display_order Strategy

**Decision**: `display_order` is a 0-based integer set by the client at submission time, reflecting the order images were attached. No auto-reorder on delete — gaps are acceptable.

**Rationale**: The admin view renders images in `display_order ASC`; the submitter controls the order by the sequence they attached files. Allowing gaps avoids a costly re-numbering UPDATE when an image is deleted or never submitted.

**Alternatives considered**:
- Server-assigned order (1, 2, 3... by inserted_at): loses client-side order intent when uploads complete out of order.
- Auto-reorder on delete: correct but expensive for a cosmetic concern; deferred to v2.

---

### 4. Client-Side Preview — Object URLs, No Pre-Upload

**Decision**: Image thumbnails are rendered via `URL.createObjectURL()` immediately after file selection, with no network upload until the user clicks Submit.

**Rationale**: SC-001 requires thumbnails within 3 seconds of selection; object URLs are synchronous. Uploading on attach would start network calls before the user confirms intent, wasting bandwidth and creating orphan files for every abandoned draft.

**Alternatives considered**:
- Upload on attach (eager): faster final submit, but creates orphans for abandoned widgets and consumes upload quota.
- FileReader `readAsDataURL`: base64 encoding is ~33% larger and blocks the main thread for large files; object URLs are more efficient.

---

### 5. Video Recording — VideoRecorderService Pattern

**Decision**: A new `VideoRecorderService` in `feedback.service.ts` (or a standalone service file) mirrors the `AudioRecorderService` pattern from feature 011: `MediaRecorder` + `MediaStream`, exposing `start()`, `stop()`, `cleanup()`, and an RxJS `recording$` observable. Capability detection via `MediaRecorder.isTypeSupported('video/webm;codecs=vp8')`.

**Rationale**: The AudioRecorderService abstraction is already proven in feature 011. Reusing the same pattern minimises new concepts, keeps the recording lifecycle consistent (start → collect chunks → stop → Blob → object URL → upload on submit), and makes testing straightforward with the same mock strategy.

**Alternatives considered**:
- Third-party library (RecordRTC, video.js): adds bundle weight and external dependency for capabilities the native MediaRecorder API already provides — same decision as feature 011 Decision 1.
- Merged AudioVideoRecorderService: would complicate the mutual-exclusion logic and make unit tests harder to isolate.

---

### 6. Audio / Video Mutual Exclusion

**Decision**: Mutual exclusion is enforced in the Angular submission-state service: once `audio_url` or `video_url` is set (after a file/recording is staged), the other media type's controls are disabled with an inline message. The constraint is also enforced at the Pydantic schema level (`@model_validator` raising 422 if both are present).

**Rationale**: Client-side enforcement gives instant feedback (FR-013). The Pydantic validator is a defence-in-depth backstop for API clients that bypass the UI. No DB-level check is needed because the schema has only one `audio_url` and one `video_url` column — they are already structurally independent.

**Alternatives considered**:
- DB CHECK constraint: would require a trigger (two separate nullable columns can both be NULL or both be set — PostgreSQL can't inspect both in a simple CHECK); overkill for a UI-enforced constraint.
- Only UI enforcement: insufficient; a programmatic POST could set both fields.

---

### 7. Upload Strategy for Images (Sequential vs. Parallel)

**Decision**: Images are uploaded sequentially on Submit, in `display_order` order. Each upload calls `POST /api/feedback/upload/image`; each successful upload's `storage_path` is collected into an array. If any upload fails, retry once; if still failing, surface an error per FR-004 pattern (existing image not affected).

**Rationale**: Sequential upload simplifies progress reporting and error attribution (the user can see which image failed). The 5-image cap means at most 5 sequential uploads — typically under 2 seconds on broadband (5 × 5 MB worst case is extreme; typical screenshots are < 500 KB). Parallel uploads would complicate error handling and order preservation.

**Alternatives considered**:
- Single multipart upload endpoint: requires a new backend endpoint and changes the storage path strategy; not worth it for ≤5 files.
- Parallel with Promise.all: faster in theory, but any single rejection leaves partial state that is harder to surface cleanly.

---

### 8. Video Upload — Bucket Configuration Update

**Decision**: Reuse the existing `feedback` Supabase Storage bucket; update its configuration to allow `video/mp4` and `video/webm` MIME types and raise the file size limit to 100 MB.

**Rationale**: A separate video bucket would require duplicating all RLS policies. The existing bucket already scopes uploads to `feedback/{user_id}/` paths; adding video MIME types is a configuration change, not a structural one. Client-side validation enforces the 5 MB cap for images independently — the bucket limit only catches bypass attempts.

**Alternatives considered**:
- Separate `feedback-video` bucket: cleaner separation, but doubles policy surface area with no functional benefit.
- CDN / pre-signed upload to third party: out of scope for v1.

---

### 9. Orphan Cleanup on Abort

**Decision**: On widget close / navigate-away / submission failure, the frontend calls `DELETE /api/feedback/upload/image` for each staged image and `DELETE /api/feedback/upload/video` for a staged video (if any). This mirrors the DELETE-on-abort pattern established in feature 011 Decision 8.

**Rationale**: Consistency with feature 011 — same two-step upload + cleanup contract, extended to cover the image array and the video file.

**Alternatives considered**:
- Server-side TTL / scheduled purge: acceptable as a safety net but not as the primary cleanup path; feature 011 already committed to client-side cleanup.
