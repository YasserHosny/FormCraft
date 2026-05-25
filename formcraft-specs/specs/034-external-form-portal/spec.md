# Feature Specification: External Form Portal

**Feature Branch**: `034-external-form-portal`  
**Created**: 2026-05-25  
**Status**: Draft  
**Vision Reference**: EXT-01

## Clarifications

### Session 2026-05-25

- Q: For OTP-gated public forms, what contact verification modes should be supported per template? → A: Admin selects allowed OTP modes; external user chooses among allowed modes.
- Q: What should happen if a public form's template is updated while an external user is already filling it? → A: Continue with the template version loaded when the session started.
- Q: If the SMS/email OTP provider is unavailable, what should the public portal do? → A: Block access and show a retry/support message.
- Q: How should rate limiting be keyed for public submissions? → A: Composite policy: IP + browser/session before OTP, verified contact after OTP.
- Q: What audit detail level should public portal submissions record? → A: Metadata plus bounded field summary/redacted preview.

## User Scenarios & Testing

### User Story 1 - Public Form Access & Submission (Priority: P1)

As a member of the public (external user), I need to access a published form via a public URL or QR code, fill it out with full validation, and submit it without creating a FormCraft account, so I can complete government or banking applications remotely.

**Why this priority**: Core value proposition — extends FormCraft beyond internal operators to serve the public, dramatically expanding the addressable use case.

**Independent Test**: Open a public form URL in an incognito browser, fill all fields, submit, receive confirmation with reference number.

**Acceptance Scenarios**:

1. **Given** a template has public access enabled, **When** an external user navigates to the public URL, **Then** the form renders in Flow Layout (responsive, mobile-friendly) with Arabic-first UI and language toggle.
2. **Given** the form has validation rules, **When** the user fills fields, **Then** all validators (Arabic national ID, IBAN, etc.) and conditional logic work identically to the internal Form Desk experience.
3. **Given** the user completes and submits the form, **When** submission succeeds, **Then** a confirmation page shows a unique reference number and optional PDF download.
4. **Given** the form requires tafqeet, **When** the user enters a currency amount, **Then** tafqeet auto-computes live in the same way as internal filling.
5. **Given** a public user starts filling a form, **When** the underlying template is updated before submission, **Then** the user continues and submits against the template version loaded at session start.
6. **Given** email confirmation is enabled and an email address is available, **When** submission succeeds, **Then** the system sends a confirmation email with the reference number and optional PDF link without blocking the submitted form if delivery fails.

---

### User Story 2 - OTP Verification for External Submissions (Priority: P2)

As an org admin, I need to require phone/email OTP verification before external users can fill sensitive forms, so I can verify submitter identity without requiring full account creation.

**Why this priority**: Security layer — prevents anonymous spam submissions for sensitive forms like banking applications.

**Independent Test**: Open a form with OTP required, enter phone number, receive OTP, verify, gain access to fill the form.

**Acceptance Scenarios**:

1. **Given** a form has OTP verification enabled with one or more allowed contact modes, **When** an external user opens the public URL, **Then** a verification gate asks the user to choose among the admin-allowed SMS/email modes.
2. **Given** the user selects an allowed contact mode and enters their phone number or email address, **When** they click "Send Code", **Then** an OTP is sent through that selected mode and the user enters it to proceed.
3. **Given** the user enters a valid OTP, **When** verified, **Then** the form loads and the submission is linked to the verified phone or email.
4. **Given** the user enters an invalid OTP 3 times, **When** the third failure occurs, **Then** the form is locked for 15 minutes with a retry message.
5. **Given** an OTP-gated form cannot send OTP because the provider is unavailable, **When** the user requests a code, **Then** access remains blocked and a retry/support message is shown.

---

### User Story 3 - Admin Portal Configuration (Priority: P3)

As an org admin, I need to enable/disable public access per template, configure verification requirements, set rate limits, enable CAPTCHA, and view portal-specific submission analytics, so I can control the public form experience.

**Why this priority**: Admin control — organizations must have full control over what's exposed publicly.

**Independent Test**: Navigate to `/admin/portal`, enable public access for a template, configure OTP + CAPTCHA, verify settings apply.

**Acceptance Scenarios**:

1. **Given** admin navigates to `/admin/portal`, **When** they select a published template, **Then** toggle options show: Enable Public Access, Require OTP, Allow PDF Download, Send Email Confirmation, Enable CAPTCHA.
2. **Given** admin enables rate limiting, **When** unauthenticated users submit before OTP verification, **Then** limits are evaluated by IP plus browser/session; after OTP verification, limits are evaluated by verified contact.
3. **Given** admin enables public access, **When** the system generates a public URL, **Then** the URL uses the org's custom domain if configured, or the default `forms.formcraft.io/{org}/{slug}` pattern.
4. **Given** admin enables public access, **When** the public URL is generated, **Then** the admin can preview and download a QR code that encodes the generated public URL.

---

### Edge Cases

- Mid-fill template updates MUST NOT change the user's active form; submission uses the template version loaded at session start.
- Simultaneous sessions from the same OTP-verified contact are allowed subject to verified-contact rate limits; each portal session may submit only once and duplicate submits return a conflict response.
- OTP provider outages MUST fail closed for OTP-gated forms: access remains blocked and the portal shows a retry/support message.
- Rate limiting MUST use IP plus browser/session before OTP verification and verified contact after OTP verification to reduce false positives behind shared corporate IP addresses.
- Public link bursts from social sharing MUST be handled with cacheable form configuration responses, CAPTCHA when enabled, server-side rate limits, and friendly retry messages for limited users.

## Requirements

### Functional Requirements

- **FR-001**: System MUST generate public URLs for enabled templates using org custom domain or default pattern.
- **FR-002**: Public forms MUST render in responsive Flow Layout with Arabic-first UI and language toggle.
- **FR-003**: All validation rules, conditional logic, and tafqeet MUST work identically to internal Form Desk.
- **FR-004**: System MUST support OTP verification via SMS and email as a configurable gate where admins select the allowed modes per template and external users choose among those allowed modes.
- **FR-005**: System MUST support CAPTCHA integration (hCaptcha or reCAPTCHA) as configurable option.
- **FR-006**: System MUST support configurable rate limiting using IP plus browser/session before OTP verification and verified contact after OTP verification.
- **FR-007**: Submissions from the portal MUST be stored with `source: "public_portal"` for filtering.
- **FR-008**: System MUST show a confirmation page with reference number after successful submission.
- **FR-009**: System MUST support optional PDF download and email confirmation for submitted forms; email delivery failure MUST NOT roll back the submission and MUST be audited.
- **FR-010**: Admin MUST be able to enable/disable public access per template.
- **FR-011**: Public form submissions MUST be included in audit logs and operational reports with metadata plus bounded field summary/redacted preview, not full raw submitted payloads.
- **FR-012**: Public form sessions MUST pin the template version at load time and submit against that pinned version even if a newer template version is published before submission.
- **FR-013**: OTP-gated forms MUST NOT allow access without successful OTP verification when the OTP provider is unavailable.
- **FR-014**: Each public portal session MUST allow at most one successful submission; duplicate submit attempts MUST return a conflict response without creating another submission.
- **FR-015**: Public form load and submit paths MUST enforce burst protection through rate limiting and CAPTCHA checks where configured.
- **FR-016**: System MUST generate a QR code for each enabled public form URL for admin preview and download.
- **FR-017**: Public portal endpoints after initial form discovery MUST require a valid opaque portal session token or scoped download token; anonymous access is limited to resolving enabled public form metadata and creating the initial pinned session.

### Key Entities

- **Portal Configuration**: Per-template settings for public access (enabled, verification type, rate limits, CAPTCHA, PDF download, email confirmation).
- **OTP Verification**: Selected contact mode, phone/email, OTP code, expiry, attempt count, verification status.
- **Public Submission**: Extension of form_submission with source="public_portal", verified_contact, submission IP, pinned template version, email confirmation status, and audit-safe bounded/redacted field summary.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Public forms load and become interactive within 3 seconds on mobile 4G connections.
- **SC-002**: OTP delivery reaches the user within 30 seconds of request.
- **SC-003**: Public portal handles 100 concurrent form submissions without degradation.
- **SC-004**: 100% of public submissions are distinguishable from internal submissions via source field.
- **SC-005**: Rate limiting correctly blocks excessive submissions with zero false positives for legitimate users.
