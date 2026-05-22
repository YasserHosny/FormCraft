# Research: Customer Feedback Feature

**Branch**: `001-customer-feedback` | **Phase**: 0

## Decision Log

---

### 1. File Storage for Images and Audio

**Decision**: Use Supabase Storage — the same service already used by the PDF engine for template assets.

**Rationale**: No new storage infrastructure is needed. Supabase Storage provides per-bucket RLS policies, signed URLs, and direct upload from the backend. A dedicated `feedback` bucket will isolate feedback files from template assets.

**Alternatives considered**:
- AWS S3 / Cloudinary: more features, but adds a third-party dependency not yet in the stack.
- Store files in PostgreSQL as BYTEA: not suitable for large binary files; no CDN delivery.

---

### 2. In-Browser Audio Recording

**Decision**: Use the browser-native **MediaRecorder API** (Web API). No third-party recording SDK is required.

**Rationale**: MediaRecorder is supported in all modern browsers (Chrome, Firefox, Edge, Safari 14.1+). It produces a Blob that can be uploaded directly. Angular wraps it cleanly in a service.

**Fallback**: If the browser does not expose `navigator.mediaDevices.getUserMedia`, the record button is hidden and only audio file upload is shown (FR-013).

**Alternatives considered**:
- RecordRTC / vmsg: adds bundle weight (~200 KB+); unnecessary given native support.

---

### 3. Audio File Upload (Q2-C second path)

**Decision**: Accept MP3, M4A, WAV, and WebM, max 10 MB per file.

**Rationale**: MP3, M4A, and WAV are the three most common consumer audio formats for file upload. WebM/Opus is added because the browser-native MediaRecorder API (used for live recording) produces WebM blobs in Chrome and Firefox — rejecting WebM would break the live recording path. 10 MB is ~10 minutes at 128 kbps MP3, well beyond the 2-minute recording cap, giving file-upload parity.

---

### 4. Cooldown Enforcement

**Decision**: Enforce the 30-second cooldown **server-side** by querying the last `submitted_at` for the authenticated user before accepting a new submission.

**Rationale**: Client-side cooldown is trivially bypassed. Server-side is authoritative and consistent.

---

### 5. Admin Dashboard Placement

**Decision**: Extend the existing `/admin/` backend route module (`app/api/routes/admin.py`) with two new endpoints, and add a new Angular route `/admin/feedback` in the frontend features area.

**Rationale**: The admin pattern already exists (`require_role(Role.ADMIN)`, paginated list, `audit-logs` endpoint). Reusing this structure avoids a new module and keeps admin concerns co-located.

---

### 6. Feedback Submission Flow (image + audio)

**Decision**: Two-step upload — client uploads file(s) first to get storage URLs, then submits the feedback record with those URLs in a single JSON body.

**Rationale**: Avoids multipart complexity on the main submission endpoint. Upload endpoints can be independently rate-limited and retried. Consistent with how the existing PDF engine handles assets.

---

### 8. Orphan File Cleanup

**Decision**: On submission failure after a successful file upload, the frontend calls
`DELETE /api/feedback/upload` (passing the storage path) to remove the orphaned object
before showing the user the error. No background purge job is added in v1.

**Rationale**: The two-step flow (upload → submit) creates orphan objects in the `feedback`
bucket when Step 2 fails. Client-side cleanup on failure is the simplest solution: the
frontend already holds the storage path returned by the upload endpoint, and Supabase Storage
DELETE is a single API call. A scheduled purge (cron comparing storage objects vs DB rows)
is more complex and unnecessary if client-side cleanup is reliable. If the client crashes
without cleaning up, the orphan remains but causes no functional harm — it will not be
referenced by any feedback record and cannot be read by non-admins.

**v1 known limitation**: Orphans from crashed/aborted sessions will persist until a manual
admin cleanup or a future purge job. Volume is expected to be low.

**Alternatives considered**:
- Multipart single-request submission: avoids orphans entirely but makes the main endpoint
  significantly more complex (mixed JSON + file handling, partial failure modes).
- Scheduled purge job: correct long-term solution; deferred to a future iteration.

---

### 7. Supabase Storage Bucket

**Decision**: Create a new private `feedback` bucket with RLS:
- Write: authenticated users (for their own uploads during submission)
- Read: admin role only (for admin dashboard playback/preview)

**Rationale**: Feedback files are internal; no public CDN URL needed. Signed URLs generated server-side on admin dashboard read.
