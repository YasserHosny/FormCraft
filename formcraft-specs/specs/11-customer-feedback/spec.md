# Feature Specification: Customer Feedback

**Feature Branch**: `001-customer-feedback`  
**Created**: 2026-05-07  
**Status**: Draft  
**Input**: User description: "Customer feedback feature where customers can submit feedback as text, image uploads, or recorded audio"

## User Scenarios & Testing *(mandatory)*

### User Story 1 – Submit Text Feedback (Priority: P1)

A FormCraft user encounters a problem or has a suggestion while using the application. They open a persistent feedback widget (e.g., a "Feedback" button visible on all pages), type their message, and submit. The system records the submission and confirms receipt with a success message.

**Why this priority**: Text feedback is the most universal input method and the baseline for any feedback system. Without it the feature has no function at all.

**Independent Test**: Can be fully tested by opening the feedback widget, typing a message, and submitting — delivers a complete, usable feedback channel even without image or audio.

**Acceptance Scenarios**:

1. **Given** a logged-in user on any page, **When** they open the feedback widget, type a message, and click Submit, **Then** the feedback is saved and the user sees a success confirmation.
2. **Given** a user composing feedback, **When** the text field is empty and they attempt to submit, **Then** submission is blocked and a validation message is shown.
3. **Given** a user composing feedback, **When** the text reaches 2000 characters, **Then** no further input is accepted and the remaining character count reads 0.

---

### User Story 2 – Attach an Image (Priority: P2)

A user wants to report a visual bug or share a screenshot alongside their text feedback. They open the feedback widget, write their message, attach an image file from their device, see a thumbnail preview, and submit.

**Why this priority**: Images dramatically increase the actionability of bug reports. Text (P1) must exist before this adds value.

**Independent Test**: Can be tested by submitting feedback with an attached image and verifying the image is stored and linked to the feedback entry.

**Acceptance Scenarios**:

1. **Given** a user composing feedback, **When** they attach a supported image file (JPEG, PNG, or WEBP, max 5 MB) and submit, **Then** the image is stored and associated with the feedback entry.
2. **Given** a user composing feedback, **When** they attach a file exceeding 5 MB or in an unsupported format, **Then** the file is rejected before upload with a clear error message.
3. **Given** a user who has attached an image, **When** they view the widget, **Then** a thumbnail preview of the image is visible inside the widget.

---

### User Story 3 – Record and Submit Audio (Priority: P3)

A user prefers to describe their issue verbally. They open the feedback widget, click a microphone button, record their voice message (up to 2 minutes), hear a playback preview, and submit it alongside optional text.

**Why this priority**: Audio lowers the effort barrier for users who prefer speaking over typing, but is a premium enhancement — the feature is fully usable without it.

**Independent Test**: Can be tested by recording audio in the widget, playing it back, and submitting — verifying the audio file is stored and linked to the feedback entry.

**Acceptance Scenarios**:

1. **Given** a user composing feedback, **When** they click Record, grant microphone permission, speak, and click Stop, **Then** a playable audio preview appears in the widget.
2. **Given** a user who has recorded audio, **When** they submit, **Then** the audio file is stored and linked to the feedback entry.
3. **Given** a user recording audio, **When** the recording reaches 2 minutes, **Then** recording stops automatically and the user is notified.
4. **Given** a user whose browser does not support audio recording, **When** they open the widget, **Then** the record button is hidden and text/image inputs remain available.
5. **Given** a user who has recorded audio, **When** they click Re-record, **Then** the previous recording is discarded and a new one can be started.

---

### Edge Cases

- What happens when the user submits feedback while offline? → Show an error; do not silently lose the submission.
- What happens if image upload fails mid-submission? → Retry once; if it still fails, block submission and offer the option to remove the attachment and submit text only.
- What happens if audio recording permission is denied? → Hide the record button and show a tooltip explaining microphone access is required.
- What if a user submits multiple feedback entries rapidly? → Enforce a 30-second cooldown per user between submissions to prevent spam.
- What happens on mobile devices? → The widget must be fully usable on small screens; audio recording uses the device's built-in microphone.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a persistent feedback widget accessible from all pages of the application to authenticated users.
- **FR-002**: System MUST require a non-empty text message (up to 2000 characters) as the minimum content for every feedback submission.
- **FR-003**: System MUST allow users to optionally attach one image file (JPEG, PNG, or WEBP, max 5 MB) per submission.
- **FR-004**: System MUST display a thumbnail preview of an attached image inside the widget before submission.
- **FR-005**: System MUST allow users to optionally record a voice message of up to 2 minutes directly in the browser and attach it to their submission.
- **FR-006**: System MUST display an audio playback control for a recorded voice message inside the widget before submission.
- **FR-007**: System MUST store each submission with: submitting user identity, submission timestamp, page URL at time of submission, text content, optional image reference, and optional audio reference.
- **FR-008**: System MUST show a success confirmation to the user after a submission is saved.
- **FR-009**: System MUST validate file type and size client-side before any upload is attempted; invalid files MUST be rejected with a descriptive error message.
- **FR-010**: System MUST enforce a 30-second cooldown per user between feedback submissions.
- **FR-011**: System MUST provide an admin-only dashboard within FormCraft where authorized users can view all submitted feedback entries, including their text, attached images, and audio playback.
- **FR-012**: Feedback widget MUST be usable on all viewport sizes from 360px wide and above.
- **FR-013**: Audio recording MUST be hidden and gracefully disabled in browsers that do not support in-browser recording.
- **FR-014**: System MUST allow users to alternatively upload a pre-recorded audio file from their device (MP3, M4A, WAV, max 10 MB) as the audio attachment instead of live recording. Live recordings captured via the MediaRecorder API are transmitted as WebM/Opus blobs and MUST also be accepted by the upload endpoint.
- **FR-015**: Admin dashboard MUST display each feedback entry with: submitter identity, submission timestamp, source page URL, text content, image thumbnail (if present), and audio playback control (if present).
- **FR-016**: Admin dashboard MUST be restricted to users with an admin role; non-admin users MUST NOT access it.

### Key Entities

- **FeedbackSubmission**: Represents one feedback entry. Attributes: id, user_id, page_url, text_content, image_url (nullable), audio_url (nullable), submitted_at, status (new / reviewed / resolved).
- **User** (existing): The authenticated FormCraft user submitting feedback; linked by user_id.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can open the widget, type a message, and submit in under 60 seconds.
- **SC-002**: Invalid image files are rejected immediately — before any upload is attempted — with a clear error message.
- **SC-003**: Audio recordings of up to 2 minutes are captured and playable inside the widget before submission.
- **SC-004**: Zero feedback submissions are lost after the user receives a success confirmation.
- **SC-005**: The feedback widget becomes interactive within 1 second of the page becoming ready (measured from Angular's initial navigation completing).
- **SC-006**: The widget is fully functional on screens 360px wide and above.

## Assumptions

- Only authenticated users can submit feedback; unauthenticated visitors do not see the widget.
- One image attachment per submission is sufficient for the initial release.
- Audio input supports both live browser recording (via microphone) and uploading a pre-recorded audio file from the user's device; both paths attach the audio to the submission.
- The submitting user's identity is captured automatically from their session — no manual name or email input is required.
- Feedback content is internal only and never visible to other end-users.

## Out of Scope

- Advanced filtering, search, or analytics on the admin feedback dashboard → see feature 012.
- Feedback categories, labels, or tagging → see feature 012.
- Multi-image attachments → see feature 013.
- Video recording or video file upload → see feature 013.
- Anonymous or unauthenticated feedback.
- Feedback threading or replies from the team back to the user → see feature 014.
