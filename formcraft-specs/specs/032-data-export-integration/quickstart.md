# Quickstart: Data Export & Integration

## Prerequisites

- Backend and frontend are running locally.
- User is authenticated as an org admin for export, recurring schedule, credential, and webhook scenarios.
- At least one published template has submissions with Arabic and mixed Arabic/English field values.
- At least one designer-accessible template has multiple pages/elements/validators/reference bindings for package tests.

## Scenario 1: Preview And Download A Direct Submission Export

1. Open `/admin/export`.
2. Select dataset `Submissions`.
3. Choose a template, date range, and status.
4. Select `CSV` and `Flattened`.
5. Preview the export.
6. Verify the preview shows matching record count and no large-export rejection.
7. Download the export.
8. Verify each submission is one row and form field keys are columns.
9. Verify Arabic and mixed-direction values are readable and associated with the correct fields.

Expected result:
- Allowed exports download directly.
- Oversized exports are rejected before generation with guidance to narrow filters.
- Audit log records the export action.

## Scenario 2: Download Structured JSON

1. Open `/admin/export`.
2. Choose filters that match known submissions.
3. Select `JSON` and `Structured`.
4. Download the export.
5. Verify each submission preserves original field grouping and metadata.

Expected result:
- JSON export is org-scoped and includes only matching submissions.
- Empty result sets return an empty structured file with a clear no-records indication.

## Scenario 3: Create And Run A Recurring Email Export

1. Open `/admin/export/schedules`.
2. Create a weekly submission export schedule.
3. Select filters, format, scope, and email recipients.
4. Save the schedule.
5. Run the schedule immediately.
6. Verify an export delivery record appears with queued/sent/failed state.
7. Verify recipients receive the export or no-data notice according to schedule settings.

Expected result:
- Recurring delivery is email-only.
- Export history shows delivery summary and failure details.
- SFTP/file-transfer fields are not present.

## Scenario 4: Export A Template Package

1. Open a template that contains pages, elements, validators, conditions, and reference bindings.
2. Select `Export Package`.
3. Download the `.formcraft` package.
4. Inspect the package manifest.

Expected result:
- Package includes template metadata, pages, elements, validators, conditions, reference-binding metadata, package version, and checksum.
- Package preserves exact mm coordinates.

## Scenario 5: Import A Template Package As New Draft

1. Use a `.formcraft` package whose lineage/name does not match an existing target template.
2. Open package import.
3. Upload the package.
4. Review warnings/remapping needs.
5. Confirm import.

Expected result:
- A new draft template is created.
- Invalid, corrupted, unsupported, or unauthorized packages are rejected without partial creation.

## Scenario 6: Import A Template Package As New Version

1. Use a `.formcraft` package whose lineage or name matches an existing target template.
2. Upload the package.
3. Confirm import after review.
4. Open the target template version history.

Expected result:
- Import creates a new version of the existing template.
- The currently published version is not replaced.
- Remapping warnings are visible before use.

## Scenario 7: Manage Integration Credentials

1. Open `/admin/integrations`.
2. Create a credential with a name, scopes, and optional expiry.
3. Copy the one-time secret.
4. Refresh the page and verify the secret is no longer visible.
5. Revoke the credential.

Expected result:
- Credential metadata remains visible.
- Secret is shown once only.
- Revoked credential stops granting access immediately.
- Audit log records create/rotate/revoke actions.

## Scenario 8: Configure And Test A Signed Webhook

1. Open `/admin/integrations/webhooks`.
2. Create a webhook with event type `form_submitted`, HTTPS target URL, and signing secret.
3. Trigger a test delivery.
4. Inspect delivery log.

Expected result:
- Active webhook requires a signing secret.
- Delivery includes a signature header.
- Delivery log stores full payload preview and is visible only to authorized org admins.

## Scenario 9: Webhook Retry And Failure History

1. Configure a webhook endpoint that returns an error.
2. Trigger the associated event.
3. Verify delivery attempts are recorded.
4. Wait for retries or trigger retry worker manually in the test environment.

Expected result:
- Failed delivery retries up to three attempts with exponential backoff.
- After the third failed attempt, status becomes failed.
- Response code/body preview and retry timestamps are visible in admin delivery history.

## API Smoke Examples

Preview export:

```bash
curl -X POST "$API_URL/api/admin/export/preview" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "filters": {"template_id": "00000000-0000-0000-0000-000000000000"},
    "format": "csv",
    "scope": "flattened"
  }'
```

Create webhook:

```bash
curl -X POST "$API_URL/api/admin/integrations/webhooks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Submitted forms",
    "event_type": "form_submitted",
    "target_url": "https://example.com/formcraft/webhook",
    "signing_secret": "change-me-to-a-long-secret"
  }'
```

## Validation Checklist

- Verify all UI strings are translation keys in Arabic and English.
- Verify RTL and LTR layouts for export filters, schedule forms, package import review, credential table, and webhook delivery log.
- Verify export files preserve Arabic and mixed-direction values.
- Verify org isolation for exports, packages, credentials, webhooks, and delivery logs.
- Verify all export/import/credential/webhook actions appear in audit logs.
