# Feature Specification: External Form Portal

**Feature Branch**: `034-external-form-portal`  
**Created**: 2026-05-25  
**Status**: Draft  
**Vision Reference**: EXT-01

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

---

### User Story 2 - OTP Verification for External Submissions (Priority: P2)

As an org admin, I need to require phone/email OTP verification before external users can fill sensitive forms, so I can verify submitter identity without requiring full account creation.

**Why this priority**: Security layer — prevents anonymous spam submissions for sensitive forms like banking applications.

**Independent Test**: Open a form with OTP required, enter phone number, receive OTP, verify, gain access to fill the form.

**Acceptance Scenarios**:

1. **Given** a form has OTP verification enabled, **When** an external user opens the public URL, **Then** a verification gate asks for phone number or email.
2. **Given** the user enters their phone number, **When** they click "Send Code", **Then** an OTP is sent via SMS and the user enters it to proceed.
3. **Given** the user enters a valid OTP, **When** verified, **Then** the form loads and the submission is linked to the verified phone/email.
4. **Given** the user enters an invalid OTP 3 times, **When** the third failure occurs, **Then** the form is locked for 15 minutes with a retry message.

---

### User Story 3 - Admin Portal Configuration (Priority: P3)

As an org admin, I need to enable/disable public access per template, configure verification requirements, set rate limits, enable CAPTCHA, and view portal-specific submission analytics, so I can control the public form experience.

**Why this priority**: Admin control — organizations must have full control over what's exposed publicly.

**Independent Test**: Navigate to `/admin/portal`, enable public access for a template, configure OTP + CAPTCHA, verify settings apply.

**Acceptance Scenarios**:

1. **Given** admin navigates to `/admin/portal`, **When** they select a published template, **Then** toggle options show: Enable Public Access, Require OTP, Allow PDF Download, Send Email Confirmation, Enable CAPTCHA.
2. **Given** admin enables rate limiting, **When** they set "max 10 submissions per IP per hour", **Then** the 11th submission from the same IP within an hour is blocked with a friendly message.
3. **Given** admin enables public access, **When** the system generates a public URL, **Then** the URL uses the org's custom domain if configured, or the default `forms.formcraft.io/{org}/{slug}` pattern.

---

### Edge Cases

- What happens when a public form's template is updated while a user is mid-fill?
- How does the system handle simultaneous submissions from the same OTP-verified user?
- What happens when the SMS/email provider is down during OTP delivery?
- How does rate limiting work behind shared corporate IP addresses (NAT)?
- What happens when a public form link is shared on social media and gets thousands of hits?

## Requirements

### Functional Requirements

- **FR-001**: System MUST generate public URLs for enabled templates using org custom domain or default pattern.
- **FR-002**: Public forms MUST render in responsive Flow Layout with Arabic-first UI and language toggle.
- **FR-003**: All validation rules, conditional logic, and tafqeet MUST work identically to internal Form Desk.
- **FR-004**: System MUST support OTP verification via SMS and email as a configurable gate.
- **FR-005**: System MUST support CAPTCHA integration (hCaptcha or reCAPTCHA) as configurable option.
- **FR-006**: System MUST support configurable rate limiting per IP per hour.
- **FR-007**: Submissions from the portal MUST be stored with `source: "public_portal"` for filtering.
- **FR-008**: System MUST show a confirmation page with reference number after successful submission.
- **FR-009**: System MUST support optional PDF download and email confirmation for submitted forms.
- **FR-010**: Admin MUST be able to enable/disable public access per template.
- **FR-011**: Public form submissions MUST be included in audit logs and operational reports.

### Key Entities

- **Portal Configuration**: Per-template settings for public access (enabled, verification type, rate limits, CAPTCHA, PDF download, email confirmation).
- **OTP Verification**: Phone/email, OTP code, expiry, attempt count, verification status.
- **Public Submission**: Extension of form_submission with source="public_portal", verified_contact, submission IP.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Public forms load and become interactive within 3 seconds on mobile 4G connections.
- **SC-002**: OTP delivery reaches the user within 30 seconds of request.
- **SC-003**: Public portal handles 100 concurrent form submissions without degradation.
- **SC-004**: 100% of public submissions are distinguishable from internal submissions via source field.
- **SC-005**: Rate limiting correctly blocks excessive submissions with zero false positives for legitimate users.
