# Wireframes: Customer Feedback

**Branch**: `001-customer-feedback` | **Date**: 2026-05-07 | **Spec**: [spec.md](spec.md)

---

## 1. Feedback Button (Persistent — all authenticated pages)

A floating action button fixed to the bottom-right corner of every page.

```
┌─────────────────────────────────────────────────────────────┐
│  [Page content]                                             │
│                                                             │
│                                                             │
│                                              ┌───────────┐  │
│                                              │ 💬 Feedback│  │
│                                              └───────────┘  │
└─────────────────────────────────────────────────────────────┘
```

- Fixed position: `bottom: 24px; right: 24px`
- Angular Material `mat-fab` extended button
- Visible only to authenticated users
- Clicking opens the Feedback Widget modal (Section 2)

---

## 2. Feedback Widget — Text Only (P1 baseline state)

```
┌────────────────────────────────────────────┐
│  Send Feedback                          ✕  │
├────────────────────────────────────────────┤
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │ Describe your feedback or issue…     │  │
│  │                                      │  │
│  │                                      │  │
│  │                                      │  │
│  └──────────────────────────────────────┘  │
│                              0 / 2000 ▸    │
│                                            │
│  ┌─────────────────┐  ┌─────────────────┐  │
│  │  🖼  Add image   │  │  🎤  Add audio   │  │
│  └─────────────────┘  └─────────────────┘  │
│                                            │
│  ┌────────────────────────────────────┐    │
│  │              Submit                │    │
│  └────────────────────────────────────┘    │
│             Cancel                         │
└────────────────────────────────────────────┘
```

**Behaviour notes**:
- Modal width: 480px (desktop); full-width on mobile (≥ 360px)
- Character counter updates in real time; turns red at 2000/2000
- Submit button disabled until text field is non-empty
- Cancel closes modal and discards all input

---

## 3. Feedback Widget — Image Attached (P2 state)

After the user selects a valid image file, a thumbnail replaces the "Add image" button.

```
┌────────────────────────────────────────────┐
│  Send Feedback                          ✕  │
├────────────────────────────────────────────┤
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │ The export button is missing on      │  │
│  │ mobile when I rotate the screen.     │  │
│  │                                      │  │
│  └──────────────────────────────────────┘  │
│                             52 / 2000 ▸    │
│                                            │
│  ┌────────────────┐  ┌─────────────────┐   │
│  │ ┌────────────┐ │  │  🎤  Add audio   │   │
│  │ │ [thumbnail]│ │  └─────────────────┘   │
│  │ │  screenshot│ │                        │
│  │ └────────────┘ │                        │
│  │       ✕ Remove │                        │
│  └────────────────┘                        │
│                                            │
│  ┌────────────────────────────────────┐    │
│  │              Submit                │    │
│  └────────────────────────────────────┘    │
│             Cancel                         │
└────────────────────────────────────────────┘
```

**Behaviour notes**:
- Client-side validation fires on file selection (before any upload)
- Unsupported format or > 5 MB: red inline error, no thumbnail shown
- "✕ Remove" clears the attachment and restores the "Add image" button

---

## 4. Feedback Widget — Image Validation Error

```
┌────────────────────────────────────────────┐
│  Send Feedback                          ✕  │
├────────────────────────────────────────────┤
│  ...                                       │
│                                            │
│  ┌─────────────────────────────────────┐   │
│  │  🖼  Add image                       │   │
│  └─────────────────────────────────────┘   │
│  ⚠ File must be JPEG, PNG, or WEBP         │
│    and under 5 MB.                         │
│                                            │
│  ...                                       │
└────────────────────────────────────────────┘
```

---

## 5. Feedback Widget — Audio: Recording State (P3)

After the user clicks "Add audio" → "Record" and grants microphone permission.

```
┌────────────────────────────────────────────┐
│  Send Feedback                          ✕  │
├────────────────────────────────────────────┤
│  ...                                       │
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │  ● Recording  0:42 / 2:00            │  │
│  │  ████████████░░░░░░░░░░░░░░░░░░░░░░  │  │
│  │                         [ Stop ]     │  │
│  └──────────────────────────────────────┘  │
│                                            │
│  ...                                       │
└────────────────────────────────────────────┘
```

**Behaviour notes**:
- Red pulsing dot indicates active recording
- Progress bar fills toward the 2-minute cap
- At 2:00, recording stops automatically and UI transitions to Section 6

---

## 6. Feedback Widget — Audio: Playback Preview State

After recording stops (or a file is uploaded).

```
┌────────────────────────────────────────────┐
│  Send Feedback                          ✕  │
├────────────────────────────────────────────┤
│  ...                                       │
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │  ▶  ░░░░░░░░░░░░░░░░░░░░░░░  0:42   │  │
│  │                                      │  │
│  │  [ Re-record ]   [ Upload file ↑ ]   │  │
│  └──────────────────────────────────────┘  │
│                                            │
│  ...                                       │
└────────────────────────────────────────────┘
```

**Behaviour notes**:
- Native `<audio>` element provides playback scrubbing
- "Re-record" discards current recording, returns to idle audio section
- "Upload file" opens file picker (MP3 / M4A / WAV / WebM, ≤ 10 MB) and replaces the recording

---

## 7. Feedback Widget — Audio: Browser Not Supported (Fallback)

When `navigator.mediaDevices.getUserMedia` is unavailable.

```
┌────────────────────────────────────────────┐
│  Send Feedback                          ✕  │
├────────────────────────────────────────────┤
│  ...                                       │
│                                            │
│  ┌──────────────────────────────────────┐  │
│  │  📎  Upload audio file               │  │
│  │      MP3 · M4A · WAV · up to 10 MB   │  │
│  └──────────────────────────────────────┘  │
│                                            │
│  ...                                       │
└────────────────────────────────────────────┘
```

- Record button is hidden entirely (FR-013)
- File upload input remains available

---

## 8. Feedback Widget — Success State

Shown after a successful submission (replaces form content).

```
┌────────────────────────────────────────────┐
│  Send Feedback                          ✕  │
├────────────────────────────────────────────┤
│                                            │
│           ✅                               │
│    Thank you for your feedback!            │
│    We'll review it shortly.                │
│                                            │
│  ┌────────────────────────────────────┐    │
│  │              Close                 │    │
│  └────────────────────────────────────┘    │
│                                            │
└────────────────────────────────────────────┘
```

---

## 9. Feedback Widget — Cooldown Error (429)

Shown when the user submits again within 30 seconds.

```
┌────────────────────────────────────────────┐
│  Send Feedback                          ✕  │
├────────────────────────────────────────────┤
│  ...form content...                        │
│                                            │
│  ⚠ Please wait 18 seconds before          │
│    submitting again.                       │
│                                            │
│  ┌────────────────────────────────────┐    │
│  │  Submit  (available in 18 s)       │    │  ← button disabled, countdown shown
│  └────────────────────────────────────┘    │
└────────────────────────────────────────────┘
```

---

## 10. Admin Feedback Dashboard — `/admin/feedback`

```
┌──────────────────────────────────────────────────────────────────────────┐
│  FormCraft Admin                                                         │
├───────────────┬──────────────────────────────────────────────────────────┤
│  Dashboard    │  Feedback Submissions                                    │
│  Users        │                                                          │
│  Forms        │  Filter by status: [ All ▾ ]   [ new ] [ reviewed ]      │
│  ► Feedback   │                    [ resolved ]                          │
│  Audit Log    │                                                          │
│               │  ┌──────┬────────────┬───────────┬──────────────────────┤
│               │  │ Date │ User       │ Page      │ Message              │
│               ├──┼──────┼────────────┼───────────┼──────────────────────┤
│               │  │05-07 │ Ahmed H.   │/designer/ │ The export button…  ▸│
│               │  │      │            │           │ 🖼 📎  ● new          │
│               ├──┼──────┼────────────┼───────────┼──────────────────────┤
│               │  │05-06 │ Sara K.    │/templates/│ Dark mode looks…    ▸│
│               │  │      │            │           │        ● reviewed    │
│               ├──┼──────┼────────────┼───────────┼──────────────────────┤
│               │  │05-05 │ Omar N.    │/forms/123 │ Cannot save draft… ▸│
│               │  │      │            │           │ 🖼     ● resolved    │
│               └──┴──────┴────────────┴───────────┴──────────────────────┘
│               │  ← Previous   Page 1 of 3   Next →                      │
└───────────────┴──────────────────────────────────────────────────────────┘
```

**Legend**: 🖼 = image attached · 📎 = audio attached

---

## 11. Admin Feedback Dashboard — Expanded Row

Clicking a row expands it inline to show full content.

```
  ┌──────┬────────────┬───────────┬──────────────────────────────────────────┐
  │05-07 │ Ahmed H.   │/designer/ │ The export button is missing on mobile   │
  │      │            │template-3 │ when I rotate the screen to landscape.   │
  │      │            │           │ It only appears after a full page reload. │
  │      │            │           │                                           │
  │      │            │           │ ┌──────────┐                              │
  │      │            │           │ │[thumbnail]│                             │
  │      │            │           │ └──────────┘                              │
  │      │            │           │                                           │
  │      │            │           │ ▶ ░░░░░░░░░░░░░░  0:42   (audio)         │
  │      │            │           │                                           │
  │      │            │           │ Status: [ new ▾ ]  → reviewed / resolved │
  └──────┴────────────┴───────────┴──────────────────────────────────────────┘
```

**Behaviour notes**:
- Thumbnail opens full image in a lightbox on click
- Status dropdown changes status immediately via `PATCH /api/admin/feedback/{id}`
- Row collapses when clicked again or another row is expanded

---

## Responsive Behaviour (≥ 360px — FR-012)

```
Mobile widget (360px wide):
┌──────────────────────┐
│ Send Feedback     ✕  │
├──────────────────────┤
│ ┌──────────────────┐ │
│ │ Your message…    │ │
│ │                  │ │
│ └──────────────────┘ │
│          0 / 2000    │
│ ┌──────────────────┐ │
│ │  🖼  Add image    │ │
│ └──────────────────┘ │
│ ┌──────────────────┐ │
│ │  🎤  Add audio    │ │
│ └──────────────────┘ │
│ ┌──────────────────┐ │
│ │     Submit       │ │
│ └──────────────────┘ │
│       Cancel         │
└──────────────────────┘
```

- Image and audio buttons stack vertically on narrow viewports
- Modal takes full viewport width with 16px horizontal padding
- FAB button shrinks to icon-only at < 400px
