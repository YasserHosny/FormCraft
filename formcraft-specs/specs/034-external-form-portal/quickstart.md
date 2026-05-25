# Quickstart: External Form Portal

## Preconditions

- Backend and frontend dev environments are running.
- Supabase migrations through F034 are applied.
- At least one organization has a published template with fields, validation, and optional tafqeet.
- Admin user belongs to that organization.
- OTP and CAPTCHA providers can be mocked in development.

## Scenario 1: Enable Public Access

1. Sign in as an admin.
2. Open `/admin/portal`.
3. Select a published template.
4. Enable public access.
5. Configure:
   - Public slug: `loan-application`
   - OTP required: off
   - CAPTCHA: off
   - PDF download: on
   - Email confirmation: on
6. Save settings.
7. Verify the generated public URL uses the org custom domain if configured, otherwise `/forms/{org}/{slug}`.
8. Preview and download the generated QR code, then verify it encodes the same public URL.

Expected result: the template is available through a public URL and no FormCraft account is required.

## Scenario 2: Submit a Public Form

1. Open the public URL in an incognito browser.
2. Confirm Arabic-first UI renders in responsive Flow Layout.
3. Switch language to English and verify LTR layout mirrors correctly.
4. Fill all required fields.
5. Trigger a deterministic validation error, then correct it.
6. Submit the form.

Expected result: confirmation page shows a unique reference number. The submission is stored with public portal source metadata and pinned template version. If email confirmation is enabled and an email is available, the email confirmation status is recorded; delivery failure does not roll back the submission.

## Scenario 3: OTP-Gated Public Form

1. As admin, enable OTP verification for the same template.
2. Select allowed modes: SMS and email.
3. Open the public URL in incognito.
4. Choose email, enter an email address, and request a code.
5. Enter a wrong code three times.
6. Verify the session locks for 15 minutes.
7. Retry with a new session and valid code.

Expected result: form access is blocked until successful OTP. The submission records verified contact mode/hash without creating a user account.

## Scenario 4: OTP Provider Failure

1. Configure the development OTP provider mock to return provider unavailable.
2. Open an OTP-gated public URL.
3. Request a code.

Expected result: access remains blocked and the user sees a retry/support message.

## Scenario 5: Rate Limiting

1. Set rate limit to 2 submissions per 60 minutes.
2. Submit twice from the same browser/session before OTP.
3. Attempt a third submission.
4. Enable OTP and submit twice with the same verified contact.
5. Attempt a third verified submission.

Expected result: pre-OTP limiting uses IP plus browser/session. Post-OTP limiting uses verified contact.

## Scenario 6: Template Update During Fill

1. Open the public form and start filling it.
2. In another admin session, publish a new template version.
3. Submit the already-open public form.

Expected result: submission succeeds against the originally loaded template version, and PDF/download behavior uses that pinned version.

## Validation Commands

```bash
cd /media/yasserhosny/My\ Passport/Work/Projects/FormCraft/formcraft-backend
pytest tests/unit/test_portal_service.py tests/unit/test_portal_otp_service.py tests/unit/test_portal_rate_limit_service.py tests/integration/test_external_form_portal_routes.py
ruff check .
```

```bash
cd /media/yasserhosny/My\ Passport/Work/Projects/FormCraft/formcraft-frontend
npm run build
```
