# FormCraft — Playwright Test Scenarios (Step-by-Step)

> Each feature described as a sequential test flow with capture points for screenshot evidence.
> Generated: 2026-06-01 (updated for specs 041–053)

---

## Prerequisites

| User Role | Login Email | Purpose |
|-----------|------------|---------|
| Platform Admin | platform@formcraft.io | Platform Console features |
| Org Admin | admin@bank.eg | Admin Console, Design Studio, all features |
| Designer | designer@bank.eg | Template design, canvas, AI suggestions |
| Operator | operator@bank.eg | Form Desk, filling, printing, history |

---

## 1. AUTHENTICATION & ACCESS

### Feature 1.1: User Login

1. Navigate to `/auth/login`.
2. Verify the login page loads with email and password fields.
3. Enter a valid email and password.
4. Click the Login button.
5. Verify redirect to the default dashboard based on user role.
6. Capture evidence: login page before submitting, dashboard after login.

### Feature 1.2: Language Toggle

1. Log in as any user.
2. Locate the language toggle in the top navigation bar.
3. Switch language from English to Arabic.
4. Verify the entire UI switches to RTL layout with Arabic labels.
5. Switch back to English.
6. Verify the UI returns to LTR layout with English labels.
7. Capture evidence: UI in English, UI in Arabic.

### Feature 1.3: User Profile

1. Log in as any user.
2. Navigate to `/auth/profile`.
3. Verify the profile page shows display name, email, language preference, and role.
4. Update the display name.
5. Click Save.
6. Verify the updated name appears in the navigation bar.
7. Capture evidence: profile form before and after saving.

### Feature 1.4: MFA Enrollment

1. Log in as an Admin user.
2. Navigate to `/mfa/enroll`.
3. Verify the QR code is displayed for authenticator app setup.
4. Verify backup codes are shown.
5. Capture evidence: enrollment page with QR code and backup codes.

### Feature 1.5: MFA Challenge

1. Log in as a user with MFA enabled.
2. Verify redirect to `/mfa/challenge`.
3. Enter a valid OTP code.
4. Verify successful login and redirect to dashboard.
5. Capture evidence: challenge page with OTP input.

---

## 2. DESIGN STUDIO — TEMPLATE MANAGEMENT

### Feature 2.1: View Template Library

1. Log in as a Designer.
2. Navigate to `/templates`.
3. Verify the template library loads with a grid of template cards.
4. Verify each card shows template name, status badge, and version number.
5. Verify the "Create" button is visible in the toolbar.
6. Capture evidence: template library with template cards.

### Feature 2.2: Create a New Template via Wizard

1. Log in as a Designer.
2. Navigate to `/templates`.
3. Click the "Create" button.
4. Verify redirect to `/templates/new` with the creation wizard.
5. **Step 1 — Basic Info**: Enter template name, description, select a category, and add tags.
6. Click Next.
7. **Step 2 — Locale**: Select language (Arabic), country (Egypt), and currency (EGP).
8. Click Next.
9. **Step 3 — Page Setup**: Select A4 size, Portrait orientation, and set margins.
10. Click Next.
11. **Step 4 — Starting Point**: Select "Blank Canvas".
12. Click Create.
13. Verify redirect to the Design Studio canvas (`/designer/:templateId`).
14. Capture evidence: each wizard step (Basic Info, Locale, Page Setup, Starting Point), and the canvas after creation.

### Feature 2.3: Clone an Existing Template

1. Log in as a Designer.
2. Navigate to `/templates`.
3. Locate a published template card.
4. Click the Clone icon button (content_copy) on the template card.
5. Verify the clone dialog opens.
6. Confirm the clone action.
7. Verify a new draft template appears in the template list with the cloned name.
8. Capture evidence: clone dialog, cloned template in the library.

### Feature 2.4: Delete a Draft Template

1. Log in as a Designer.
2. Navigate to `/templates`.
3. Locate a template with status "draft".
4. Click the Delete icon button on the template card.
5. Confirm the deletion in the confirmation dialog.
6. Verify the template is removed from the list.
7. Capture evidence: delete confirmation dialog, template list after deletion.

### Feature 2.5: Create New Version of Published Template

1. Log in as a Designer.
2. Navigate to `/templates`.
3. Locate a published template card.
4. Click the "New Version" button on the card.
5. Verify a new draft is created linked to the published template's lineage.
6. Verify the new draft opens in the canvas editor.
7. Capture evidence: new version button on card, canvas editor showing draft status.

---

## 3. DESIGN STUDIO — CANVAS EDITOR

### Feature 3.1: Add Elements to Canvas

1. Log in as a Designer.
2. Open a draft template in the canvas editor (`/designer/:templateId`).
3. Verify the element palette is visible on the left side with element types (text, number, date, currency, checkbox, dropdown, etc.).
4. Drag a "Text" element from the palette onto the canvas.
5. Verify the element appears on the canvas at the dropped position.
6. Click the element to select it.
7. Verify the properties panel opens on the right side.
8. Capture evidence: palette visible, element on canvas, properties panel open.

### Feature 3.2: Configure Element Properties

1. Log in as a Designer.
2. Open a draft template and select an element on the canvas.
3. In the properties panel, enter an Arabic label and an English label.
4. Set the field as required.
5. Add a validation rule (e.g., minimum length).
6. Set a default value and placeholder text.
7. Set the field direction to RTL.
8. Verify auto-save triggers (auto-saves after 2 seconds of inactivity).
9. Capture evidence: properties panel with all configured fields.

### Feature 3.3: Add Tafqeet Element

1. Log in as a Designer.
2. Open a draft template in the canvas editor.
3. Add a "Currency" element to the canvas.
4. Add a "Tafqeet" element to the canvas.
5. Select the Tafqeet element to open its property panel.
6. Link it to the Currency field as the source element.
7. Configure the output language (Arabic) and currency name (EGP).
8. Verify the canvas shows the Tafqeet element connected to the Currency field.
9. Capture evidence: tafqeet property panel with source field linked, canvas showing both elements.

### Feature 3.4: Configure Conditional Logic

1. Log in as a Designer.
2. Open a draft template in the canvas editor.
3. Add a "Dropdown" element (e.g., Account Type with options: Personal, Corporate).
4. Add a "Text" element (e.g., Company Name).
5. Select the Company Name element.
6. Open the condition builder in the properties panel.
7. Set a `visible_when` rule: `Account Type equals "Corporate"`.
8. Verify the condition is saved.
9. Capture evidence: condition builder with the rule configured.

### Feature 3.5: Add Signature Element

1. Log in as a Designer.
2. Open a draft template in the canvas editor.
3. Add a "Signature" element from the palette.
4. Select the element and open the signature property panel.
5. Configure signature dimensions and label.
6. Capture evidence: signature element on canvas, signature property panel.

### Feature 3.6: Add Table Element

1. Log in as a Designer.
2. Open a draft template in the canvas editor.
3. Add a "Table" element from the palette.
4. Select the element and open the table config panel.
5. Define table columns (e.g., Item, Quantity, Amount).
6. Verify the table preview shows the configured columns.
7. Capture evidence: table config panel, table preview on canvas.

### Feature 3.7: Bind Reference Data to a Field

1. Log in as a Designer.
2. Open a draft template in the canvas editor.
3. Select a dropdown or text field element.
4. Open the Reference Data Binding panel.
5. Select a reference list (e.g., "Authorized Signatories").
6. Map list columns to form fields (e.g., list.name_ar → signatory_name field).
7. Verify the binding is saved.
8. Capture evidence: reference binding panel with list selected and mappings configured.

### Feature 3.8: View Version History

1. Log in as a Designer.
2. Open a template with multiple versions in the canvas editor.
3. Open the Version History panel.
4. Verify all versions are listed with version number, date, and publisher.
5. Click a version to view it.
6. Capture evidence: version history panel with version list.

### Feature 3.9: View Version Diff

1. Log in as a Designer.
2. Open a template with at least two versions.
3. Open the Version Diff view.
4. Select two versions to compare.
5. Verify the diff shows added, removed, and changed elements.
6. Capture evidence: version diff view showing changes.

### Feature 3.10: View Template Feedback Panel

1. Log in as a Designer.
2. Open a template that has received operator feedback.
3. Open the Feedback panel.
4. Verify the feedback list shows operator name, date, message, and affected field.
5. Click to acknowledge or resolve a feedback item.
6. Capture evidence: feedback panel with feedback items.

### Feature 3.11: OCR Detection Overlay

1. Log in as a Designer.
2. Open a template that was imported from a scanned form.
3. Verify the OCR detection overlay shows detected field bounding boxes.
4. Accept a detection (field becomes a canvas element).
5. Reject a detection (field is dismissed).
6. Capture evidence: canvas with OCR detection overlays, accept/reject controls.

### Feature 3.12: PDF Preview

1. Log in as a Designer.
2. Open a template in the canvas editor.
3. Click the "Preview PDF" button in the toolbar.
4. Verify the PDF opens in a browser overlay.
5. Verify all elements are rendered at correct positions with proper Arabic text shaping.
6. Close the preview overlay.
7. Capture evidence: PDF preview overlay.

### Feature 3.13: Configure Overlay Print Settings

1. Log in as a Designer.
2. Open a template in the canvas editor.
3. Open the Print Settings panel.
4. Change the print mode to "Overlay".
5. Upload a stationery scan image (pre-printed form background).
6. Verify the scan appears as a background layer on the canvas.
7. Toggle "Include in overlay" on specific elements.
8. Capture evidence: print settings panel, canvas with stationery scan background.

### Feature 3.14: Submit Template for Review

1. Log in as a Designer.
2. Open a completed draft template in the canvas editor.
3. Click "Submit for Review" in the toolbar.
4. Verify the template status changes to "Submitted for Review".
5. Verify the canvas becomes read-only.
6. Capture evidence: status badge showing "Submitted", read-only canvas.

### Feature 3.15: Publish a Template

1. Log in as an Admin.
2. Open an approved template in the canvas editor.
3. Click the "Publish" button.
4. Verify the template status changes to "Published".
5. Verify the version number increments.
6. Capture evidence: status badge showing "Published" with version number.

---

## 4. FORM DESK — DAILY OPERATIONS

### Feature 4.1: View Operator Dashboard

1. Log in as an Operator.
2. Navigate to `/desk`.
3. Verify the dashboard loads with: search bar, category/country/language filters.
4. Verify the "Pinned Forms" section shows starred templates.
5. Verify the "Recently Used" section shows last used templates.
6. Verify the "Drafts" section shows saved drafts with completion percentage.
7. Verify the history link is visible.
8. Capture evidence: full dashboard with all sections visible.

### Feature 4.2: Search and Filter Templates on Dashboard

1. Log in as an Operator.
2. Navigate to `/desk`.
3. Type a template name in the search bar.
4. Verify the template list filters instantly.
5. Select a category from the filter dropdown.
6. Verify the list filters by category.
7. Click "Clear Filters" to reset.
8. Verify all templates are shown again.
9. Capture evidence: filtered results, cleared results.

### Feature 4.3: Pin/Unpin a Template

1. Log in as an Operator.
2. Navigate to `/desk`.
3. Locate a template card and click the pin/star icon.
4. Verify the template appears in the "Pinned Forms" section.
5. Click the pin icon again to unpin.
6. Verify the template is removed from the "Pinned Forms" section.
7. Capture evidence: pinned templates section before and after.

### Feature 4.4: Fill a Form (Basic Flow)

1. Log in as an Operator.
2. Navigate to `/desk`.
3. Click a published template card.
4. Verify the form filler loads at `/desk/fill/:templateId`.
5. Verify the form toolbar is visible (Save Draft, Preview PDF, Print, Print & Next, Clear All, Cancel).
6. Fill in required text fields.
7. Fill in a national ID field and verify real-time validation (keystroke-level).
8. Fill in a currency amount and verify the linked Tafqeet field auto-computes the Arabic words.
9. Verify the error summary banner updates as fields are filled ("N required fields remaining").
10. Verify the Print button becomes enabled when all required fields are valid.
11. Capture evidence: empty form, partially filled form with validation errors, fully filled form with tafqeet.

### Feature 4.5: Conditional Fields During Filling

1. Log in as an Operator.
2. Open a form that has conditional logic (e.g., Account Type → Corporate fields).
3. Select "Personal" in the Account Type dropdown.
4. Verify corporate-only fields are hidden.
5. Change selection to "Corporate".
6. Verify corporate-only fields appear dynamically.
7. Capture evidence: form with "Personal" selected (fields hidden), form with "Corporate" selected (fields visible).

### Feature 4.6: Reference Data Dropdown During Filling

1. Log in as an Operator.
2. Open a form that has reference-data-bound fields (e.g., Signatory Name).
3. Click the signatory name field.
4. Verify a searchable dropdown appears with entries from the reference list.
5. Type to filter entries.
6. Select an entry.
7. Verify all mapped fields auto-fill (name, title, signature image).
8. Capture evidence: dropdown open with entries, fields auto-filled after selection.

### Feature 4.7: Save and Resume a Draft

1. Log in as an Operator.
2. Open a form and partially fill some fields.
3. Click "Save Draft" (or press Ctrl+S).
4. Verify a success toast appears.
5. Navigate back to `/desk`.
6. Verify the draft appears in the "Drafts" section with completion percentage.
7. Click the draft to resume.
8. Verify the form filler loads with all previously entered data.
9. Capture evidence: save draft toast, draft in dashboard drafts section, resumed form with data.

### Feature 4.8: Print a Form

1. Log in as an Operator.
2. Open a form and fill all required fields with valid data.
3. Click the "Print" button.
4. Verify the browser print dialog opens with the generated PDF.
5. Verify a submission reference number is generated (e.g., FC-2026-05-0042).
6. Verify a success toast shows the reference number.
7. Capture evidence: filled form before print, success toast with reference number.

### Feature 4.9: Print & Next (High-Throughput Mode)

1. Log in as an Operator.
2. Open a form and fill all required fields.
3. Click the "Print & Next" button.
4. Verify the print dialog opens.
5. Verify the form immediately resets to blank after print confirmation.
6. Verify the success toast shows the reference number briefly.
7. Capture evidence: filled form, reset empty form after print.

### Feature 4.10: Overlay Print with Printer Profile

1. Log in as an Operator.
2. Open a form whose template has overlay print mode.
3. Fill all required fields.
4. Click "Print".
5. Verify the print dialog shows: printer profile dropdown, overlay preview toggle, composite preview toggle.
6. Select a printer profile from the dropdown.
7. Toggle between "Overlay Preview" (data only on transparent) and "Composite Preview" (data on stationery scan).
8. Capture evidence: print dialog with printer selection, overlay preview, composite preview.

### Feature 4.11: Submit Template Feedback from Form Filler

1. Log in as an Operator.
2. Open a form in the form filler.
3. Click the feedback icon in the form toolbar.
4. Verify the feedback dialog opens pre-populated with template name and version.
5. Type a feedback message (e.g., "This field should allow 15 digits now").
6. Submit the feedback.
7. Verify a success confirmation appears.
8. Capture evidence: feedback dialog with message, success confirmation.

### Feature 4.12: View Submission History

1. Log in as an Operator.
2. Navigate to `/desk/history`.
3. Verify the history table loads with columns: reference number, date, template, key fields, status.
4. Use the search field to search by reference number.
5. Verify matching submissions are shown.
6. Filter by template using the template dropdown.
7. Filter by date range using the date pickers.
8. Filter by status (printed/submitted).
9. Click "Clear Filters" to reset.
10. Capture evidence: history table, search results, filtered results.

### Feature 4.13: Reprint a Past Submission

1. Log in as an Operator.
2. Navigate to `/desk/history`.
3. Locate a past submission.
4. Click the "Reprint" action.
5. Verify the PDF regenerates with "REPRINT" watermark and reprint timestamp.
6. Capture evidence: reprint action, PDF with REPRINT watermark.

### Feature 4.14: Clone a Past Submission as New Form

1. Log in as an Operator.
2. Navigate to `/desk/history`.
3. Locate a past submission.
4. Click the "Clone as New" action.
5. Verify the form filler opens pre-filled with the past submission's data.
6. Verify a clone info banner shows the source reference number.
7. Modify some fields and submit/print.
8. Verify a new reference number is generated.
9. Capture evidence: clone info banner, pre-filled form, new reference number after submission.

---

## 5. FORM DESK — CUSTOMERS

### Feature 5.1: View Customer List

1. Log in as an Operator.
2. Navigate to `/desk/customers`.
3. Verify the customer list table loads with columns: Name (AR/EN), Identifier, Contact, Status.
4. Use the search field to search by name or identifier.
5. Verify matching customers are shown.
6. Capture evidence: customer list table, search results.

### Feature 5.2: Create a New Customer

1. Log in as an Operator.
2. Navigate to `/desk/customers`.
3. Click the "Add Customer" button.
4. Verify redirect to `/desk/customers/new`.
5. Enter Arabic name, English name, identifier type (National ID), identifier number, phone, email, and address.
6. Click Save.
7. Verify redirect back to customer list with the new customer visible.
8. Capture evidence: empty customer form, filled customer form, customer list with new entry.

### Feature 5.3: Edit an Existing Customer

1. Log in as an Operator.
2. Navigate to `/desk/customers`.
3. Click a customer row to open `/desk/customers/:id`.
4. Verify the customer detail form loads with existing data.
5. Update the phone number.
6. Click Save.
7. Verify the updated data is shown in the customer list.
8. Capture evidence: customer detail with existing data, updated field.

### Feature 5.4: Auto-Populate Form from Customer Profile

1. Log in as an Operator.
2. Open a form in the form filler (`/desk/fill/:templateId`).
3. Click "Select Customer" or start typing a customer name.
4. Verify the autocomplete dropdown shows matching customer profiles.
5. Select a customer.
6. Verify matching fields auto-fill (name, national ID, phone, address).
7. Fill the remaining form-specific fields.
8. Capture evidence: customer autocomplete dropdown, auto-filled fields.

---

## 6. FORM DESK — BATCH OPERATIONS

### Feature 6.1: View Batch Queue

1. Log in as an Operator.
2. Navigate to `/desk/queue`.
3. Verify the batch list loads with columns: Name, Status, Progress, Rows, Created date.
4. Verify status chips show correct colors (primary for completed, warn for failed, accent for processing).
5. Capture evidence: batch queue list with various job statuses.

### Feature 6.2: Create a New Batch Job

1. Log in as an Operator.
2. Navigate to `/desk/queue`.
3. Click the "New Job" button.
4. Verify redirect to `/desk/queue/new` with the batch wizard.
5. **Step 1 — Template**: Select a published template from the list.
6. Click Next.
7. **Step 2 — Data Source**: Upload a CSV file.
8. Click Next.
9. **Step 3 — Column Mapping**: Verify auto-mapped columns. Manually fix any unmatched columns.
10. Click Next.
11. **Step 4 — Validation**: Verify all rows are validated. Review any invalid rows (red with error details).
12. Click Next.
13. **Step 5 — Generate**: Click Generate. Verify the progress bar shows generation status.
14. Verify redirect back to queue list with the new job showing progress.
15. Capture evidence: each wizard step, progress bar during generation, completed job in queue.

### Feature 6.3: View Batch Job Detail

1. Log in as an Operator.
2. Navigate to `/desk/queue`.
3. Click a completed batch job row.
4. Verify redirect to `/desk/queue/:id` with job details.
5. Verify metadata shows: template name, row count, status, timestamps.
6. Click the download button to download the ZIP of generated PDFs.
7. Capture evidence: batch job detail page with metadata and download button.

---

## 7. ADMIN CONSOLE — ORGANIZATION SETTINGS

### Feature 7.1: View and Edit Organization Settings

1. Log in as an Admin.
2. Navigate to `/admin/settings`.
3. Verify the settings page loads with: org name (AR+EN), logo upload, primary color, defaults (language, country, currency).
4. Update the organization's English name.
5. Click Save.
6. Verify the updated name appears.
7. Capture evidence: settings form with current values, saved confirmation.

### Feature 7.2: Manage Departments and Branches

1. Log in as an Admin.
2. Navigate to `/admin/departments`.
3. Verify the department list loads.
4. Click "Add Department" and enter Arabic and English names.
5. Save the department.
6. Verify the new department appears in the list.
7. Expand the department to view branches.
8. Click "Add Branch" under the department and enter branch details (name AR+EN, location).
9. Save the branch.
10. Verify the branch appears under the department.
11. Capture evidence: department list, add department form, department with branches.

### Feature 7.3: Manage Users

1. Log in as an Admin.
2. Navigate to `/admin/users`.
3. Verify the user list loads with columns: name, email, role, department, status.
4. Click a user to edit.
5. Change the user's role (e.g., from Operator to Designer).
6. Save the change.
7. Verify the updated role appears in the user list.
8. Capture evidence: user list, user edit form, updated user row.

### Feature 7.4: Send User Invitation

1. Log in as an Admin.
2. Navigate to `/admin/invitations`.
3. Click "Invite User".
4. Enter email, select role, and assign department.
5. Send the invitation.
6. Verify the invitation appears in the pending invitations list.
7. Capture evidence: invitation form, pending invitations list.

### Feature 7.5: Accept User Invitation

1. Open the invitation link (`/invite/:token`) in a browser (not logged in).
2. Verify the invitation accept page loads with the organization branding.
3. Set a password.
4. Submit.
5. Verify the account is activated and redirect to login.
6. Capture evidence: invitation accept page, successful activation.

---

## 8. ADMIN CONSOLE — TEMPLATE GOVERNANCE

### Feature 8.1: View Template Governance List

1. Log in as an Admin.
2. Navigate to `/admin/templates`.
3. Verify the governance table loads with all templates across all statuses.
4. Use the search field to search by template name.
5. Filter by status dropdown (e.g., select "Published").
6. Verify the list filters to show only published templates.
7. Capture evidence: full governance list, filtered by status.

### Feature 8.2: Bulk Archive Templates

1. Log in as an Admin.
2. Navigate to `/admin/templates`.
3. Select multiple templates using the checkboxes.
4. Click the "Archive Selected" button.
5. Confirm the archive action.
6. Verify the selected templates change status to "Archived".
7. Capture evidence: selected templates, archive confirmation, updated statuses.

### Feature 8.3: Review Queue — Approve a Template

1. Log in as an Admin.
2. Navigate to `/admin/reviews`.
3. Verify the review queue loads with templates in "Submitted for Review" status.
4. Verify overdue count badge is visible if applicable.
5. Filter by status and sort by days waiting.
6. Click a submitted template to open the review view.
7. Review the template in read-only canvas preview.
8. Click "Approve".
9. Verify the template status changes to "Approved".
10. Capture evidence: review queue list, read-only preview, approved status.

### Feature 8.4: Review Queue — Reject a Template

1. Log in as an Admin.
2. Navigate to `/admin/reviews`.
3. Click a submitted template.
4. Enter rejection comments.
5. Click "Reject".
6. Verify the template status changes to "Rejected" and returns to the designer.
7. Capture evidence: rejection comments, rejected status.

### Feature 8.5: View Review Timeline

1. Log in as an Admin.
2. Navigate to `/admin/review-timeline/:template_id` for a template with review history.
3. Verify the timeline shows all events: submission, review, approval/rejection.
4. Verify each event shows reviewer name, date, and comments.
5. Capture evidence: review timeline with multiple events.

### Feature 8.6: Governance Dashboard Metrics

1. Log in as an Admin.
2. Navigate to `/admin/governance`.
3. Verify the dashboard shows metric cards: pending reviews count, average turnaround days, approval rate, rejection rate.
4. Set the "since" date filter.
5. Verify metrics update for the selected date range.
6. Click "View Templates" to navigate to the governance list.
7. Capture evidence: governance dashboard with all metric cards.

### Feature 8.7: Template Feedback Overview

1. Log in as an Admin.
2. Navigate to `/admin/template-feedback`.
3. Verify the feedback overview lists all feedback across all templates.
4. Filter by status (new, acknowledged, resolved).
5. Verify most-reported templates and fields are highlighted.
6. Capture evidence: feedback overview list, filtered results.

---

## 9. ADMIN CONSOLE — REFERENCE DATA

### Feature 9.1: Create a Reference Data List

1. Log in as an Admin.
2. Navigate to `/admin/reference-data`.
3. Verify the reference data list page loads.
4. Click "Create" to open the form dialog.
5. Enter list name (e.g., "Authorized Signatories"), Arabic name, English name.
6. Set scope to "Organization".
7. Define schema columns (e.g., name_ar: text required, name_en: text, title_ar: text, authority_level: dropdown, max_amount: number).
8. Save the list.
9. Verify the new list appears in the catalog.
10. Capture evidence: create dialog with schema, list in catalog.

### Feature 9.2: Manage Reference Data Entries

1. Log in as an Admin.
2. Navigate to `/admin/reference-data`.
3. Click a reference list to open `/admin/reference-data/:listId/entries`.
4. Verify the entries table loads.
5. Click "Add Entry" to open the entry form dialog.
6. Fill in values according to the list schema.
7. Save the entry.
8. Verify the entry appears in the table.
9. Toggle an entry to "Inactive".
10. Verify the entry shows as inactive.
11. Capture evidence: entries table, add entry form, inactive entry.

### Feature 9.3: Bulk Import Reference Data Entries

1. Log in as an Admin.
2. Navigate to `/admin/reference-data/:listId/entries`.
3. Click "Import" to open the import dialog.
4. Upload a CSV file with entries matching the list schema.
5. Verify the import preview shows matched rows.
6. Confirm the import.
7. Verify new entries appear in the table.
8. Capture evidence: import dialog, imported entries in table.

---

## 10. ADMIN CONSOLE — PRINTER PROFILES

### Feature 10.1: Create a Printer Profile

1. Log in as an Admin.
2. Navigate to `/admin/printer-profiles`.
3. Verify the printer profiles list loads.
4. Click "Add" to open the printer profile dialog.
5. Enter printer name (e.g., "Teller Window 3 — HP LaserJet").
6. Set X offset to +1.5 mm and Y offset to -0.8 mm.
7. Select a branch.
8. Save the profile.
9. Verify the profile appears in the list.
10. Capture evidence: add printer dialog, profile in list.

### Feature 10.2: Print Calibration Page

1. Log in as an Admin.
2. Navigate to `/admin/printer-profiles`.
3. Click the "Calibration Page" button for a printer profile.
4. Verify a calibration PDF is generated with crosshair grid at known mm positions.
5. Capture evidence: calibration page PDF.

---

## 11. ADMIN CONSOLE — DATA EXPORT

### Feature 11.1: Export Submission Data

1. Log in as an Admin.
2. Navigate to `/admin/export`.
3. Fill in the filter form: select a template ID, date range, branch, operator, status.
4. Select export format (CSV, Excel, or JSON).
5. Click "Preview" to see the export preview with row count.
6. Click "Export" to download the file.
7. Capture evidence: filter form filled, export preview, downloaded file.

### Feature 11.2: Configure Export Schedule

1. Log in as an Admin.
2. Navigate to `/admin/export/schedules`.
3. Create a new schedule: select template, format, frequency (weekly), and add recipient emails.
4. Save the schedule.
5. Verify the schedule appears in the list with next run time.
6. Capture evidence: schedule form, schedule list.

---

## 12. ADMIN CONSOLE — INTEGRATIONS

### Feature 12.1: Manage API Credentials

1. Log in as an Admin.
2. Navigate to `/admin/integrations`.
3. Verify the Credentials tab is active by default.
4. Verify existing credentials are listed with columns: Name, Prefix, Status, Actions.
5. Click "Create" to generate a new API credential.
6. Enter a name and scope.
7. Save and copy the generated key.
8. Verify the credential appears in the table with "active" status.
9. Click the Revoke icon to revoke a credential.
10. Verify the status changes to "revoked".
11. Capture evidence: credentials table, create dialog, revoked credential.

### Feature 12.2: Manage Webhooks

1. Log in as an Admin.
2. Navigate to `/admin/integrations`.
3. Switch to the Webhooks tab.
4. Click "Create" to add a new webhook.
5. Select event type (e.g., on_form_submitted).
6. Enter endpoint URL and custom headers.
7. Save the webhook.
8. Click "Test" to send a sample event.
9. Verify the delivery log shows the test result.
10. Capture evidence: webhook form, delivery log with test result.

---

## 13. ADMIN CONSOLE — PORTAL MANAGEMENT

### Feature 13.1: Enable Public Portal for a Template

1. Log in as an Admin.
2. Navigate to `/admin/portal`.
3. Verify the template list loads on the left sidebar.
4. Click a template to select it.
5. Toggle "Enable" to activate public access.
6. Configure the public slug.
7. Configure options: require OTP, allow PDF download, send email confirmation.
8. Save the configuration.
9. Verify the template shows an "enabled" chip.
10. Capture evidence: portal config panel with settings, enabled chip.

### Feature 13.2: Access Public Form as External User

1. Navigate to `/forms/:org/:slug` (no login required).
2. Verify the public form loads in mobile-friendly flow layout.
3. If OTP is required: enter phone number and verify with OTP code.
4. Fill all required fields with proper validation.
5. Submit the form.
6. Verify redirect to confirmation page with reference number.
7. Capture evidence: public form page, OTP verification (if applicable), confirmation page with reference number.

---

## 14. ADMIN CONSOLE — REPORTS

### Feature 14.1: Transaction Register Report

1. Log in as an Admin.
2. Navigate to `/admin/reports/transactions`.
3. Set filter criteria: date range, template, operator, branch.
4. Click "Generate" or "Search".
5. Verify the report table loads with columns: reference number, template, operator, customer, date, key fields, status.
6. Click "Export" and select format (Excel/CSV/PDF).
7. Capture evidence: filter panel, report table, export dialog.

### Feature 14.2: Daily Reconciliation Report

1. Log in as an Admin.
2. Navigate to `/admin/reports/reconciliation`.
3. Select a date and branch.
4. Verify the report shows: total submissions, total amount, breakdown by template and operator.
5. Capture evidence: reconciliation report with totals and breakdown.

### Feature 14.3: Period Summary Report

1. Log in as an Admin.
2. Navigate to `/admin/reports/period-summary`.
3. Select a period (month/quarter/year) and grouping (by branch/department/template).
4. Verify the report shows: count, total amount, average, min/max with period-over-period comparison arrows.
5. Capture evidence: period summary with trend indicators.

### Feature 14.4: Beneficiary Report

1. Log in as an Admin.
2. Navigate to `/admin/reports/financial/beneficiary`.
3. Search for a specific beneficiary.
4. Filter by date range and amount range.
5. Verify all transactions for that beneficiary are listed.
6. Capture evidence: beneficiary search, transaction results.

### Feature 14.5: Void & Reprint Register

1. Log in as an Admin.
2. Navigate to `/admin/reports/financial/void-reprint`.
3. Verify the report lists all voided, cancelled, and reprinted submissions.
4. Verify each entry shows: original reference, void reason, who voided/reprinted, date.
5. Verify fraud flags are shown for entries with more than 3 reprints.
6. Capture evidence: void/reprint register table.

### Feature 14.6: Signatory Usage Report

1. Log in as an Admin.
2. Navigate to `/admin/reports/financial/signatory-usage`.
3. Filter by signatory, date range, or template.
4. Verify the report shows: signatory name, transactions authorized, total amount, authority limit alerts.
5. Capture evidence: signatory usage report with alert indicators.

### Feature 14.7: Custom Report Builder

1. Log in as an Admin.
2. Navigate to `/admin/reports/builder`.
3. Select data dimensions (e.g., template name, submission date, amount).
4. Apply filters (date range, branch).
5. Choose aggregation (sum of amounts).
6. Choose visualization (bar chart).
7. Click "Preview" to generate the report.
8. Save the report with a name.
9. Capture evidence: report builder configuration, generated chart, save dialog.

### Feature 14.8: Schedule a Report

1. Log in as an Admin.
2. Navigate to `/admin/reports/schedules`.
3. Create a new schedule: select a saved report, set frequency (weekly), format (Excel+PDF), and add recipients.
4. Save the schedule.
5. Verify the schedule appears in the list.
6. Capture evidence: schedule form, schedule list.

---

## 15. ADMIN CONSOLE — DATA RETENTION

### Feature 15.1: Configure Retention Policy

1. Log in as an Admin.
2. Navigate to `/admin/retention/policies`.
3. Verify existing policies are listed by entity type.
4. Edit a policy to set retention period (e.g., archive submissions after 12 months).
5. Save the policy.
6. Capture evidence: policy list, policy edit form.

### Feature 15.2: View Retention Jobs

1. Log in as an Admin.
2. Navigate to `/admin/retention/jobs`.
3. Verify the job list shows past retention runs with status and records affected.
4. Capture evidence: retention jobs list.

### Feature 15.3: Manage Legal Holds

1. Log in as an Admin.
2. Navigate to `/admin/retention/holds`.
3. Create a new legal hold: specify scope and reason.
4. Verify the hold appears in the list.
5. Release the hold.
6. Capture evidence: legal hold creation, hold list, release action.

### Feature 15.4: View Archive Manifests

1. Log in as an Admin.
2. Navigate to `/admin/retention/manifests`.
3. Verify archived data manifests are listed with date, scope, and record count.
4. Click download on a manifest.
5. Capture evidence: manifest list, download action.

---

## 16. ADMIN CONSOLE — SSO CONFIGURATION

### Feature 16.1: Configure Identity Provider

1. Log in as an Admin.
2. Navigate to `/admin/sso`.
3. Verify the IdP configuration form loads.
4. Enter IdP details: entity ID, SSO URL, certificate.
5. Save the configuration.
6. Capture evidence: IdP configuration form.

### Feature 16.2: Verify Domain

1. Log in as an Admin.
2. Navigate to `/admin/sso/verify`.
3. Verify DNS record instructions are displayed.
4. Check the domain verification status.
5. Capture evidence: domain verification page with DNS instructions.

### Feature 16.3: Configure Attribute Mappings

1. Log in as an Admin.
2. Navigate to `/admin/sso/mappings`.
3. Map IdP attributes to FormCraft profile fields (e.g., displayName → display_name).
4. Configure role mapping.
5. Save mappings.
6. Capture evidence: attribute mapping configuration.

---

## 17. ADMIN CONSOLE — OCR BATCH ONBOARDING

### Feature 17.1: View OCR Batch List

1. Log in as an Admin.
2. Navigate to `/admin/ocr-onboarding`.
3. Verify the batch list shows past OCR import jobs with status and form count.
4. Capture evidence: OCR batch list.

### Feature 17.2: Create OCR Batch Import

1. Log in as an Admin.
2. Navigate to `/admin/ocr-onboarding/new`.
3. Upload multiple PDF/image files.
4. Start the batch processing.
5. Capture evidence: file upload area, processing start.

### Feature 17.3: Review OCR Batch Results

1. Log in as an Admin.
2. Navigate to `/admin/ocr-onboarding/:batchId`.
3. Verify each form is shown as a card with thumbnail, AI-suggested name, and confidence score.
4. Accept high-confidence detections.
5. Reject or modify low-confidence detections.
6. Capture evidence: batch detail with form cards, accept/reject controls.

---

## 18. ANALYTICS

### Feature 18.1: Field Analytics

1. Log in as an Admin.
2. Navigate to `/admin/analytics/fields`.
3. Verify charts/tables show: error rates per field, most common validation errors, fields most often left empty.
4. Capture evidence: field analytics dashboard.

### Feature 18.2: Operator Performance Analytics

1. Log in as an Admin.
2. Navigate to `/admin/analytics/operators`.
3. Verify the page shows: forms processed per operator, average fill time, error rate, busiest hours heatmap.
4. Capture evidence: operator analytics dashboard.

### Feature 18.3: Compliance Analytics

1. Log in as an Admin.
2. Navigate to `/admin/analytics/compliance`.
3. Verify the page shows: template quality scores, validator coverage %, bilingual label %, approval workflow adherence.
4. Capture evidence: compliance analytics dashboard.

### Feature 18.4: Template Usage Analytics

1. Log in as an Admin.
2. Navigate to `/admin/analytics/templates`.
3. Verify the page shows: most-used templates, fill completion rate, average fill time, version adoption curve, stale templates list.
4. Capture evidence: template usage analytics dashboard.

---

## 19. PLATFORM CONSOLE (Super-Admin)

### Feature 19.1: View Platform Dashboard

1. Log in as a Platform Admin.
2. Navigate to `/platform`.
3. Verify the dashboard shows: total organizations, total users, total submissions.
4. Verify charts show: organizations by tier, submission volume trend.
5. Verify alerts show: organizations approaching tier limits.
6. Capture evidence: platform dashboard with all metrics and charts.

### Feature 19.2: View Organization List

1. Log in as a Platform Admin.
2. Navigate to `/platform/organizations`.
3. Verify the organization table loads with columns: name, tier, active users, templates, submissions, status.
4. Search for an organization by name.
5. Filter by tier or status.
6. Capture evidence: organization list table, search/filter results.

### Feature 19.3: Create a New Organization

1. Log in as a Platform Admin.
2. Navigate to `/platform/organizations/create`.
3. Enter organization name (Arabic and English).
4. Select default language, country, and currency.
5. Select subscription tier.
6. Click Create.
7. Verify redirect to organization detail page.
8. Verify the first admin invitation is auto-generated.
9. Capture evidence: create organization form, organization detail after creation.

### Feature 19.4: View Organization Detail

1. Log in as a Platform Admin.
2. Navigate to `/platform/organizations/:id`.
3. Verify the detail page has tabs: Profile, Subscription, Users, Stats.
4. Click the Profile tab — verify org name, logo, domain, branding.
5. Click the Subscription tab — verify tier, limits, usage.
6. Click the Users tab — verify user counts by role.
7. Click the Stats tab — verify templates count, submissions, storage usage.
8. Capture evidence: each tab of the organization detail page.

### Feature 19.5: Suspend and Reactivate an Organization

1. Log in as a Platform Admin.
2. Navigate to `/platform/organizations/:id`.
3. Click the "Suspend" action.
4. Confirm the suspension.
5. Verify the organization status changes to "Suspended".
6. Click the "Reactivate" action.
7. Verify the status changes back to "Active".
8. Capture evidence: suspend confirmation, suspended status, reactivated status.

---

## 20. PRODUCT FEEDBACK

### Feature 20.1: Submit Product Feedback (Widget)

1. Log in as any user.
2. Locate the floating feedback widget on any page.
3. Click the widget to open the feedback form.
4. Type a feedback message.
5. Attach an image (up to 5 images supported).
6. Submit the feedback.
7. Verify a confirmation message appears.
8. Capture evidence: feedback widget open, filled form with attachment, confirmation.

### Feature 20.2: View My Feedback

1. Log in as a user who has submitted feedback.
2. Navigate to `/my-feedback`.
3. Verify the feedback list shows all submitted items with page URL, date, status, and reply count.
4. Expand a feedback item to view the original text and admin replies.
5. Type a reply in the thread.
6. Submit the reply.
7. Capture evidence: my feedback list, expanded item with thread.

### Feature 20.3: Admin Feedback Dashboard

1. Log in as an Admin.
2. Navigate to `/admin/feedback`.
3. Verify the feedback admin dashboard shows all submissions.
4. Filter by status chips (All, New, Reviewed, Resolved).
5. Filter by label and submitter.
6. Search by text content.
7. Click a feedback item to view details and thread.
8. Assign labels to the feedback.
9. Reply to the user in the thread.
10. Mark the feedback as resolved.
11. Capture evidence: feedback admin list, filters active, threaded reply, label assignment.

---

## 21. MARKETPLACE

### Feature 21.1: Browse Marketplace

1. Log in as an Admin.
2. Navigate to `/marketplace`.
3. Verify the marketplace loads with template cards.
4. Filter by country, category, language, and price type (free/premium).
5. Sort by quality score.
6. Capture evidence: marketplace browse page with filters.

### Feature 21.2: View Marketplace Template Detail

1. Log in as an Admin.
2. Navigate to `/marketplace/:id`.
3. Verify the detail page shows: template description, preview images, quality score, ratings.
4. Click "Use Template" to clone it into the organization.
5. Verify a new draft template is created in the template library.
6. Capture evidence: marketplace detail page, confirmation of template clone.

### Feature 21.3: Publish a Template to Marketplace

1. Log in as an Admin.
2. Navigate to `/marketplace/publish`.
3. Select a published template.
4. Add description, tags, preview images.
5. Set pricing (free or premium).
6. Submit for marketplace listing.
7. Capture evidence: publish form, submission confirmation.

---

## 22. DIGITAL SIGNATURES

### Feature 22.1: View Signature Requests

1. Log in as an Admin.
2. Navigate to the digital signatures section.
3. Verify the request list shows all signature requests with status.
4. Capture evidence: signature request list.

### Feature 22.2: View Signature Request Detail

1. Log in as an Admin.
2. Navigate to a specific signature request.
3. Verify the detail page shows: document, signers, status per signer, timestamps.
4. Capture evidence: signature request detail page.

### Feature 22.3: Configure Signature Workflow

1. Log in as an Admin.
2. Navigate to signature workflows configuration.
3. Configure signing order and required signers.
4. Save the workflow.
5. Capture evidence: workflow configuration form.

### Feature 22.4: Sign as External Signer

1. Open the signer portal link (`/admin/digital-signatures/sign/:token`) without logging in.
2. Verify the document is displayed for review.
3. Draw or upload a signature.
4. Submit the signature.
5. Capture evidence: signer portal with document, signature pad.

### Feature 22.5: View Signature Evidence

1. Log in as an Admin.
2. Navigate to signature evidence for a completed request.
3. Verify the evidence shows: signer identity, timestamp, IP address, signature image.
4. Capture evidence: evidence viewer page.

---

## 23. BATCH SCHEDULES (Admin)

### Feature 23.1: Manage Batch Schedules

1. Log in as an Admin.
2. Navigate to `/admin/batch-schedules`.
3. Verify the schedule list loads with configured recurring batch jobs.
4. Create or edit a schedule: select template, data source, cron expression.
5. Enable/disable a schedule.
6. Verify last run status and next run time.
7. Capture evidence: batch schedule list, schedule form.

---

## 24. NOTIFICATIONS

### Feature 24.1: View Notifications

1. Log in as any user.
2. Click the notification bell icon in the navigation bar.
3. Verify the notification dropdown shows recent notifications with unread count.
4. Click "Mark all as read".
5. Verify the unread count resets to zero.
6. Click a notification to navigate to the relevant page.
7. Capture evidence: notification dropdown with unread items, after marking all read.

---

## 25. CUSTOM LOCALE VALIDATORS (spec 048)

### Feature 25.1: Create a Custom Validator

1. Log in as an Admin.
2. Navigate to `/admin/validators`.
3. Verify the validators list loads with any existing custom validators.
4. Click "New Validator".
5. Enter a name (e.g., "Egyptian National ID"), select locale `ar-EG`, choose field type `text`.
6. Write a regex pattern `^\d{14}$` and an error message in Arabic.
7. Click Save.
8. Verify the new validator appears in the list with its name and locale.
9. Capture evidence: validator form, list after creation.

### Feature 25.2: Use a Custom Validator in the Canvas

1. Log in as a Designer.
2. Open any template in the Canvas Editor.
3. Select a text field element.
4. In the field properties panel, locate the "Validation" section.
5. Choose the custom validator created in 25.1 from the dropdown.
6. Save the template.
7. Verify the field panel shows the custom validator name.
8. Capture evidence: field properties panel with validator selected.

### Feature 25.3: Fill-Time Validation with Custom Validator

1. Log in as an Operator.
2. Open the Desk and start filling the template updated in 25.2.
3. Enter an invalid value in the validated field (e.g., fewer than 14 digits).
4. Attempt to proceed to the next page or submit.
5. Verify the custom error message appears in Arabic (or locale-appropriate language).
6. Enter a valid 14-digit number and verify the error clears.
7. Capture evidence: field with error, field without error.

---

## 26. GRANULAR TEMPLATE PERMISSIONS (spec 043)

### Feature 26.1: Restrict Template to a Department

1. Log in as an Admin.
2. Navigate to the Template Management list.
3. Select a template and open its Settings / Permissions panel.
4. Under "Access Control", restrict the template to a specific department.
5. Save the permissions.
6. Capture evidence: permissions panel with department restriction saved.

### Feature 26.2: Restrict Template to a Branch

1. Log in as an Admin.
2. Repeat 26.1 but restrict by branch instead of department.
3. Save and verify the branch restriction appears.
4. Capture evidence: permissions panel showing branch filter.

### Feature 26.3: Access Diagnostic

1. Log in as an Operator who belongs to a different department/branch than the one allowed.
2. Navigate to the Form Desk.
3. Verify the restricted template does NOT appear in the template picker.
4. Log in as an Operator in the allowed department/branch.
5. Verify the template IS visible in the picker.
6. Capture evidence: template picker for disallowed user (template absent), for allowed user (template present).

---

## 27. MOBILE OFFLINE DESK (spec 047)

### Feature 27.1: Open and Fill a Form Offline

1. Open a Chromium browser with a mobile viewport (`375×812`).
2. Log in as an Operator and navigate to `/ui/desk`.
3. Open a template to start a new draft.
4. Using Chrome DevTools (or Playwright's `context.setOffline(true)`), simulate going offline.
5. Verify the app shows an offline indicator but the form remains interactive.
6. Fill in several fields and navigate between pages.
7. Verify the data persists in the form without network access.
8. Capture evidence: offline indicator visible, form still functional.

### Feature 27.2: Sync After Reconnect

1. Continue from 27.1 with the offline draft partially filled.
2. Re-enable network (set offline to false).
3. Verify the app detects reconnection and shows a "Syncing…" or "Draft saved" indicator.
4. Refresh the page and reopen the draft.
5. Verify all previously entered values are intact.
6. Capture evidence: sync indicator, draft reloaded with all values.

---

## 28. CONNECTOR FRAMEWORK (spec 049)

### Feature 28.1: Configure a Connector

1. Log in as an Admin.
2. Navigate to `/admin/connectors`.
3. Verify the connector list loads.
4. Click "New Connector" and select a connector type (e.g., HTTP Webhook).
5. Fill in the endpoint URL, authentication method, and any header mappings.
6. Click "Test Connection" and verify a success response.
7. Save the connector.
8. Capture evidence: connector form, test result, connector in list.

### Feature 28.2: Attach a Connector to a Template

1. Log in as an Admin or Designer.
2. Open a template's Settings panel.
3. Navigate to the "Integrations / Connectors" tab.
4. Select the connector created in 28.1 and configure the trigger event (e.g., on submit).
5. Map form fields to connector payload fields.
6. Save the template.
7. Capture evidence: connector mapping UI, saved state.

### Feature 28.3: View Delivery Log

1. Log in as an Operator and submit a form that has the connector attached.
2. Navigate to the submission detail page.
3. Open the "Delivery Log" or "Connector Events" tab.
4. Verify the log shows a successful delivery event with timestamp and response code.
5. Capture evidence: delivery log with a successful entry.

---

## 29. NEW THEME — REAL DATA (spec 050)

### Feature 29.1: KPI Cards Show Live Data

1. Log in as an Operator.
2. Navigate to the new-theme Desk home at `/ui/desk`.
3. Verify KPI cards (e.g., "Drafts In Progress", "Completed Today", "Pending Review") display non-zero or realistic counts that match the database state.
4. Submit or complete a form from the classic theme.
5. Return to `/ui/desk` and hard-refresh.
6. Verify the relevant KPI count has incremented.
7. Capture evidence: KPI cards before and after a form completion.

### Feature 29.2: Draft List Shows Live Drafts

1. Log in as an Operator.
2. Navigate to `/ui/desk`.
3. Verify the draft list shows the same drafts visible in the classic desk (`/desk`).
4. Create a new draft via the classic desk.
5. Return to `/ui/desk` and refresh.
6. Verify the new draft appears in the new-theme draft list with the correct name and `completion_percent`.
7. Capture evidence: draft list in new theme showing live items.

### Feature 29.3: Activity Feed Shows Recent Events

1. Log in as an Operator.
2. Navigate to `/ui/desk`.
3. Verify the activity feed shows recent actions (e.g., "Draft saved", "Form submitted") with correct timestamps.
4. Perform an action (save a draft or submit a form).
5. Refresh the activity feed.
6. Verify the new event appears at the top.
7. Capture evidence: activity feed with at least one real event.

---

## 30. CROSS-THEME FORM FILLER (specs 052–053)

### Feature 30.1: Open Form Filler in New Theme

1. Log in as an Operator.
2. Navigate to `/ui/desk`.
3. Click a draft or start a new form from a template.
4. Verify the Form Filler opens at `/ui/desk/fill` (new-theme route) rather than the classic `/desk/fill`.
5. Verify the page header, navigation controls, and field layout match the new-theme design.
6. Capture evidence: form filler at `/ui/desk/fill` with new-theme styling.

### Feature 30.2: All Field Types Render Correctly

1. Open a template with diverse field types (text, number, date, dropdown, tafqeet, signature, attachment) in the new-theme filler.
2. Verify each field type renders and is interactive.
3. Fill each field with a valid value.
4. Verify no console errors related to missing components or theme mismatches.
5. Capture evidence: form with all field types filled, browser console showing no errors.

### Feature 30.3: i18n Parity with Classic Filler

1. In the new-theme filler, switch the UI language to Arabic.
2. Verify all labels, placeholders, error messages, and button text are in Arabic (no untranslated keys visible as raw strings like `desk.fill_button`).
3. Switch back to English and verify the same.
4. Capture evidence: filler in Arabic and in English.

### Feature 30.4: Submit and Verify Data Saved

1. Fill all required fields in the new-theme filler.
2. Click the submit/complete button.
3. Verify the success screen or redirect matches the new-theme design.
4. Navigate to the Admin submission list and verify the submission record was created with correct field values.
5. Capture evidence: success state, submission record in admin.

---

## Summary

| Section | Scenario Count |
|---------|:--------------:|
| Authentication & Access | 5 |
| Template Management | 5 |
| Canvas Editor | 15 |
| Form Desk Operations | 14 |
| Customers | 4 |
| Batch Operations | 3 |
| Organization Settings | 5 |
| Template Governance | 7 |
| Reference Data | 3 |
| Printer Profiles | 2 |
| Data Export | 2 |
| Integrations | 2 |
| Portal Management | 2 |
| Reports | 8 |
| Data Retention | 4 |
| SSO Configuration | 3 |
| OCR Batch Onboarding | 3 |
| Analytics | 4 |
| Platform Console | 5 |
| Product Feedback | 3 |
| Marketplace | 3 |
| Digital Signatures | 5 |
| Batch Schedules | 1 |
| Notifications | 1 |
| Custom Locale Validators | 3 |
| Granular Template Permissions | 3 |
| Mobile Offline Desk | 2 |
| Connector Framework | 3 |
| New Theme — Real Data | 3 |
| Cross-Theme Form Filler | 4 |
| **Total** | **119** |
