# Feature Specification: Feedback Rich Media

**Feature Branch**: `013-feedback-rich-media`  
**Created**: 2026-05-07  
**Status**: Draft  
**Depends on**: Feature 011 (Customer Feedback) — single-image upload and audio must exist  
**Input**: Deferred from feature 011 out-of-scope: "Multi-image attachments" and "Video recording or video file upload"

## User Scenarios & Testing *(mandatory)*

### User Story 1 – Attach Multiple Images (Priority: P1)

A user reporting a multi-step visual bug needs to include several screenshots in a single submission — for example, a before-state and after-state. They attach up to five images to one feedback entry, see individual thumbnail previews, can remove any image independently, and submit.

**Why this priority**: Multi-image is a natural extension of single-image (feature 011 P2). It adds immediate value for detailed bug reports and is simpler to implement than video.

**Independent Test**: Can be tested by attaching three images, verifying three thumbnails appear, removing one, and submitting — then verifying the admin dashboard shows exactly two thumbnails for that entry.

**Acceptance Scenarios**:

1. **Given** a user composing feedback, **When** they attach up to five images (JPEG, PNG, or WEBP, max 5 MB each), **Then** a thumbnail preview appears for each attached image inside the widget.
2. **Given** a user composing feedback, **When** they attempt to attach a sixth image, **Then** the action is blocked and a message states the five-image limit has been reached.
3. **Given** a user who has attached images, **When** they click the remove button on a specific thumbnail, **Then** that image is removed and the remaining thumbnails are unaffected.
4. **Given** a user composing feedback, **When** they attach an oversized or unsupported image, **Then** that file is rejected before upload with a clear error message and existing attachments remain unaffected.
5. **Given** a user who submitted feedback with multiple images, **When** an admin views that entry, **Then** all image thumbnails are visible and each opens a full-size view on click.

---

### User Story 2 – Submit Video Feedback (Priority: P2)

A user wants to demonstrate an issue through a screen narration or camera recording that text and audio alone cannot capture clearly. They record a short video directly in the browser or upload an existing video file, see an inline playback preview, and submit it alongside their text.

**Why this priority**: Video is the richest attachment type and the most complex to implement. It shares the upload infrastructure introduced in feature 011 but requires new recording capabilities. Audio recording (feature 011 P3) must be in place first.

**Independent Test**: Can be tested by recording a video in the widget, playing back the preview, and submitting — then verifying the admin dashboard shows a video player for that entry.

**Acceptance Scenarios**:

1. **Given** a user composing feedback, **When** they click the video record button and grant camera/microphone permission, **Then** recording begins and an elapsed timer with a 2-minute cap is shown.
2. **Given** a user recording video, **When** they click Stop (or the 2-minute cap is reached), **Then** recording stops and a playable video preview appears in the widget.
3. **Given** a user composing feedback, **When** they upload a pre-recorded video file (MP4 or WebM, max 100 MB), **Then** a playable video preview appears in the widget.
4. **Given** a user with a video preview, **When** they click Re-record, **Then** the previous recording is discarded and a new recording can be started.
5. **Given** a user whose browser does not support in-browser video recording, **When** they open the widget, **Then** the record button is hidden and the video file upload input remains available.
6. **Given** a user who submitted feedback with a video, **When** an admin views that entry, **Then** an inline video player is shown in the expanded row.
7. **Given** a user who has already attached audio, **When** they view the video section, **Then** video attachment is disabled with a message explaining that only one media type (audio or video) can be attached per submission.

---

### Edge Cases

- What if a video upload is interrupted mid-transfer? → Retry once automatically; if the retry fails, surface an error and offer a "Remove video and submit without it" option — preserving text and any image attachments (mirrors the image retry pattern from feature 011).
- What if the device camera or microphone permission is denied during video recording? → Hide the record button, show a tooltip, and keep the file upload input available.
- What if the user attaches both audio and video? → Only one media type is allowed per submission; the system disables the other input once one is attached and explains the constraint.
- What if a video file exceeds 100 MB? → Reject before upload with a clear size error message.

## Requirements *(mandatory)*

### Functional Requirements

#### Multiple Image Attachments (User Story 1)

- **FR-001**: System MUST allow users to attach up to five image files (JPEG, PNG, or WEBP, max 5 MB each) per feedback submission.
- **FR-002**: System MUST display a thumbnail preview for each attached image, with an individual remove control per thumbnail.
- **FR-003**: System MUST block attachment of a sixth image and display a message stating the five-image limit has been reached.
- **FR-004**: Rejection of an oversized or unsupported image file MUST NOT affect other already-attached images.
- **FR-005**: Admin dashboard MUST display all image thumbnails for a multi-image submission; each thumbnail MUST open a full-size view on click.
- **FR-006**: System MUST store each image as a separate record associated with the feedback submission; images MUST be independently retrievable.

#### Video Feedback (User Story 2)

- **FR-007**: System MUST allow users to optionally record a video message of up to 2 minutes directly in the browser (camera + microphone) and attach it to their submission.
- **FR-008**: System MUST allow users to alternatively upload a pre-recorded video file (MP4 or WebM, max 100 MB) as the video attachment.
- **FR-009**: System MUST display a video playback preview inside the widget before submission.
- **FR-010**: Video recording MUST stop automatically at the 2-minute cap and transition to the playback preview state.
- **FR-011**: System MUST allow users to discard a recording and start a new one before submission.
- **FR-012**: Video recording MUST be hidden and gracefully disabled in browsers that do not support in-browser video capture; the file upload input MUST remain available.
- **FR-013**: A submission MUST carry at most one media attachment of the audio/video type; if a user has already attached audio, the video section MUST be disabled (and vice versa), with an explanatory message.
- **FR-014**: Admin dashboard MUST display an inline video player for submissions with a video attachment.
- **FR-015**: System MUST validate video file type and size client-side before any upload is attempted; invalid files MUST be rejected with a descriptive error message.

### Key Entities

- **FeedbackImage**: Represents one image attachment on a submission. Attributes: id, feedback_id, storage_path, display_order, uploaded_at. Replaces the single `image_url` field on FeedbackSubmission from feature 011.
- **FeedbackSubmission** (existing, extended): `image_url` column replaced by the FeedbackImage relation; `video_url` (nullable) column added.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All five image thumbnails are visible in the widget within 3 seconds of the last image being selected, using local object URLs (no upload required for preview).
- **SC-002**: Invalid or oversized image files are rejected immediately — before any upload is attempted — with a clear error message that does not affect already-attached images.
- **SC-003**: Video recordings of up to 2 minutes are captured and playable inside the widget before submission.
- **SC-004**: A video file of up to 100 MB uploads successfully and the playback preview is available within 10 seconds on a standard broadband connection.
- **SC-005**: Zero attachment data is lost after the user receives a submission success confirmation.

## Assumptions

- A submission may carry up to five images OR one audio/video — not both audio and video simultaneously.
- The five-image limit is sufficient for the common multi-screenshot bug-report use case.
- Video thumbnail generation (poster frame) is not required in v1; the browser's native video element will display the first frame.
- The existing Supabase Storage `feedback` bucket is reused for video files; only the MIME allowlist and size limit need updating.
- Client-side thumbnail previews use local object URLs — images are not uploaded until the user clicks Submit.

## Out of Scope

- Image reordering via drag-and-drop (display order is insertion order in v1).
- In-browser image annotation or cropping.
- Video trimming or editing before submission.
- Audio and video attachments on the same submission.
- Animated GIF support.
- Video thumbnail/poster-frame generation server-side.
