# FormCraft — Playwright Screenshot Feature Map

> Every navigable page/route with its features, organized for automated Playwright screenshot capture.
> Generated: 2026-06-05 (updated for specs 041–057)

---

## Prerequisites

- **Roles needed**: Platform Admin, Org Admin, Designer, Operator
- **Test data**: At least 1 org, 1 published template, 1 submission, 1 draft, 1 customer, 1 reference list, 1 printer profile
- **Base URL**: `http://localhost:4200` (or configured domain)

---

## 1. AUTH — Public Routes (No Login Required)

### 1.1 Login Page
- **Route**: `/auth/login`
- **Features**:
  - Email/password login form
  - Language toggle (AR/EN)
  - Custom branding per org domain (`/auth/branding/:domain`)
  - "Forgot password" link
  - RTL/LTR layout switching

### 1.2 Invitation Accept
- **Route**: `/invite/:token`
- **Features**:
  - Accept invitation form (set password)
  - Org branding display
  - Token validation

### 1.3 Invitation Expired
- **Route**: `/invite/expired`
- **Features**:
  - Expired invitation message
  - Contact admin guidance

### 1.4 MFA Enrollment
- **Route**: `/mfa/enroll`
- **Features**:
  - TOTP authenticator setup (QR code)
  - Backup codes display

### 1.5 MFA Challenge
- **Route**: `/mfa/challenge`
- **Features**:
  - OTP input form
  - "Use backup code" option

### 1.6 Public Form Portal
- **Route**: `/forms/:org/:slug`
- **Features**:
  - Public form rendering (Flow Layout, mobile-friendly)
  - OTP phone verification (if configured)
  - All validation rules enforced
  - Tafqeet auto-computation
  - Conditional field logic
  - CAPTCHA integration
  - Language toggle (AR/EN)

### 1.7 Public Form Confirmation
- **Route**: `/forms/:org/:slug/confirmation`
- **Features**:
  - Submission reference number display
  - PDF download button (if enabled)
  - Email confirmation status

---

## 2. DESIGN STUDIO — Designer/Admin Routes

### 2.1 Template Library
- **Route**: `/templates`
- **Roles**: Admin, Designer
- **Features**:
  - Grid/list view of all templates
  - Filter by: status (draft/published/archived), category, language, country
  - Search by: name, description, tags
  - Sort by: name, created date, last modified
  - Template cards with status badge, version, quality score
  - "New Template" button (opens wizard)
  - Clone template action
  - Delete draft action
  - Pagination

### 2.2 Template Creation Wizard
- **Route**: `/templates/new`
- **Roles**: Admin, Designer
- **Features**:
  - Step 1: Basic info (bilingual name, description, category, tags)
  - Step 2: Locale (language, country, currency with org defaults)
  - Step 3: Page setup (page size in mm, orientation, margins)
  - Step 4: Starting point (blank canvas / clone existing / import from scan / import package)
  - Unsaved changes guard (canDeactivate)
  - Progress stepper

### 2.3 Canvas Editor (Design Studio)
- **Route**: `/designer/:templateId`
- **Roles**: Admin, Designer
- **Features**:
  - Konva.js canvas with mm-precision positioning
  - Element palette (text, number, date, currency, checkbox, radio, dropdown, image, QR, barcode, tafqeet, signature, table)
  - Properties panel (labels AR+EN, validation, formatting, direction, conditional logic)
  - Multi-page support (add/remove/reorder pages)
  - Grid snap (1/2/5/10 mm)
  - Undo/redo (50 steps)
  - Copy/paste, multi-select, alignment tools
  - Auto-save every 2 seconds
  - AI suggestion chip (field type + validation from label)
  - Tafqeet property panel (source field linking, currency, language)
  - Signature property panel
  - Table config panel (columns, rows)
  - Reference data binding panel (list selection, field mapping)
  - Status badge (draft/submitted/approved/published)
  - Version history panel
  - Version diff view
  - Template feedback panel (operator feedback list)
  - OCR detection overlay (accept/reject/modify detections)
  - Debug grid overlay (Ctrl+G)
  - Overlay print mode toggle (full/overlay/both)
  - Stationery scan upload (background image for overlay positioning)
  - Per-control font panel (family, size, weight override per element) — spec 057
  - Generic line-inset panel (number of lines, per-line left/right inset in mm) — spec 057
  - Overflow/fit policy selector (shrink-to-fit | clip) — spec 057
  - PDF preview button
  - Submit for review action
  - Publish action (admin only)
  - Conditional visibility rules (visible_when)
  - Conditional requirement rules (required_when)
  - Computed value formulas (computed_value)
  - Default value, placeholder text, help text, tab order, read-only toggle

---

## 3. FORM DESK — Operator Routes

### 3.1 Operator Dashboard
- **Route**: `/desk`
- **Roles**: Admin, Branch Manager, Operator
- **Features**:
  - Quick Actions search bar
  - Pinned (starred) templates section
  - Recently used templates section
  - Saved drafts section (with age + expiry warning)
  - All published templates grid
  - Filter by: category, language, country
  - Search by: template name
  - Template cards with version, last used date
  - Notification indicators (new versions, feedback responses)
  - Version notifications component

### 3.2 Form Filler
- **Route**: `/desk/fill/:templateId`
- **Roles**: Admin, Branch Manager, Operator
- **Features**:
  - Two layout modes: Flow Layout (keyboard-optimized) / Print Layout (WYSIWYG mm positions)
  - **Mobile**: Flow Layout fully functional on 360px phones and 768px tablets (spec 047)
  - All field types rendered as Angular form controls
  - Live validation on keystroke (national ID, IBAN, phone, VAT, custom)
  - Tafqeet auto-compute from linked currency fields
  - Conditional fields appear/disappear dynamically
  - Computed fields auto-calculate
  - Customer profile auto-populate ("Select Customer" button)
  - Reference data dropdowns with search/filter
  - Error summary banner ("N required fields remaining")
  - Save Draft button (Ctrl+S)
  - Preview PDF button
  - Print button (generates PDF + creates submission record)
  - Print & Next mode (high-throughput, form resets immediately)
  - Overlay print dialog (select printer profile, preview overlay vs composite)
  - Template feedback widget (report issues to designer)
  - Form-level validation blocking print until all pass
  - Bilingual error messages (AR+EN)

### 3.3 Submission History
- **Route**: `/desk/history`
- **Roles**: Admin, Branch Manager, Operator
- **Features**:
  - Table of all submitted/printed forms
  - Search by: reference number, date range, template, customer name, field values
  - Filter by: template, status, date range
  - Sort by: date (newest first)
  - Pagination (25/50/100)
  - View action (read-only submission detail)
  - Reprint action (PDF with REPRINT watermark)
  - Clone as New action (pre-fill form filler with past data)
  - Export action (JSON/CSV)

### 3.4 Customer List
- **Route**: `/desk/customers`
- **Roles**: Admin, Branch Manager, Operator
- **Features**:
  - Customer address book with search
  - Filter by name, identifier, status
  - "New Customer" button
  - Customer cards/rows with name (AR+EN), identifier, phone

### 3.5 Customer Detail
- **Route**: `/desk/customers/:id` (edit) or `/desk/customers/new` (create)
- **Roles**: Admin, Branch Manager, Operator
- **Features**:
  - Customer profile form (name AR+EN, identifier, phone, email, address, custom fields)
  - Identifier type selection (national ID, iqama, commercial register, passport)
  - Customer submission history (all forms filled for this customer)
  - Active/inactive toggle

### 3.6 Batch Queue List
- **Route**: `/desk/queue`
- **Roles**: Admin, Operator
- **Features**:
  - Active batch jobs with progress bars
  - Completed jobs with download links
  - Failed jobs with error summaries
  - "New Batch Job" button
  - Job status indicators (pending/validating/processing/completed/failed)

### 3.7 Batch Create Wizard
- **Route**: `/desk/queue/new`
- **Roles**: Admin, Operator
- **Features**:
  - Step 1: Select published template
  - Step 2: Upload data source (CSV/Excel/paste)
  - Step 3: Column mapping UI (auto-map + manual override)
  - Step 4: Validation preview (valid/invalid rows with errors)
  - Step 5: Generate progress bar

### 3.8 Batch Job Detail
- **Route**: `/desk/queue/:id`
- **Roles**: Admin, Operator
- **Features**:
  - Job metadata (template, rows, status, timestamps)
  - Progress tracking
  - Download ZIP/merged PDF
  - Error log
  - Cancel button (for running jobs)

---

## 4. ADMIN CONSOLE — Admin Routes

### 4.1 Organization Settings
- **Route**: `/admin/settings`
- **Roles**: Admin
- **Features**:
  - Org profile (name AR+EN, logo, primary color)
  - Defaults (language, country, currency)
  - Custom domain configuration
  - Subscription tier display
  - Draft expiry period setting
  - Notification preferences
  - Hijri date support toggle

### 4.2 User Management
- **Route**: `/admin/users`
- **Roles**: Admin
- **Features**:
  - User list with role, department, branch, status
  - Search and filter users
  - Edit user role/department/branch
  - Activate/deactivate user accounts
  - Force logout
  - User activity info (last login)

### 4.3 Invitations
- **Route**: `/admin/invitations`
- **Roles**: Admin
- **Features**:
  - Send new invitation (email + role + department)
  - Pending invitations list
  - Resend invitation
  - Revoke invitation
  - Invitation status tracking

### 4.4 Departments & Branches
- **Route**: `/admin/departments`
- **Roles**: Admin
- **Features**:
  - Department list (name AR+EN)
  - Create/edit/delete departments
  - Branches within each department
  - Create/edit branches (name AR+EN, location)
  - Hierarchical org structure view

### 4.5 Template Governance
- **Route**: `/admin/templates`
- **Roles**: Admin
- **Features**:
  - All templates across all statuses
  - Filter by: designer, status, department, category, version, stale/active, usage
  - Bulk actions (archive, reassign designer, change category)
  - Template quality scores overview
  - Stale template alerts (not updated in 6+ months)
  - Archive with usage impact warning

### 4.6 Review Queue (Approval Workflow)
- **Route**: `/admin/reviews`
- **Roles**: Admin
- **Features**:
  - Queue of templates submitted for review
  - Read-only canvas preview of submitted template
  - Approve / Reject / Request Changes actions
  - Reviewer comments (per-element and general)
  - Review history and audit trail

### 4.7 Review Timeline
- **Route**: `/admin/review-timeline/:template_id`
- **Roles**: Admin
- **Features**:
  - Visual timeline of all review actions for a template
  - Submission, review, approval, rejection events
  - Reviewer identity and comments
  - Timeline PDF export

### 4.8 Governance Dashboard
- **Route**: `/admin/governance`
- **Roles**: Admin
- **Features**:
  - Validator coverage percentage
  - Bilingual label coverage percentage
  - Help text coverage percentage
  - Tab order completeness
  - Overall quality scores
  - Stale templates list
  - Canvas-pinned review comments

### 4.9 Template Feedback Overview
- **Route**: `/admin/template-feedback`
- **Roles**: Admin
- **Features**:
  - Cross-template feedback list
  - Most-reported templates and fields
  - Feedback resolution rate metrics
  - Filter by: status, template, date range
  - Resolution time tracking

### 4.10 Printer Profiles
- **Route**: `/admin/printer-profiles`
- **Roles**: Admin
- **Features**:
  - Printer profile list (name, branch, offsets)
  - Create/edit printer profiles
  - Calibration offsets (X/Y mm)
  - Print calibration page button
  - Default printer toggle
  - Branch assignment

### 4.11 Reference Data Lists
- **Route**: `/admin/reference-data`
- **Roles**: Admin
- **Features**:
  - Reference list catalog (signatories, beneficiaries, cost centers, etc.)
  - Create new list with schema definition
  - List scope (org/department/branch)
  - Active/inactive toggle
  - List entry count

### 4.12 Reference Data Entries
- **Route**: `/admin/reference-data/:listId/entries`
- **Roles**: Admin
- **Features**:
  - Entries table for a specific reference list
  - Create/edit/deactivate entries
  - Bulk import from CSV/Excel
  - Effective from/to dates
  - Search and filter entries
  - Audit trail per entry

### 4.13 Data Export
- **Route**: `/admin/export`
- **Roles**: Admin
- **Features**:
  - Filter submissions by template, date range, department, branch, operator, status
  - Export format selection (CSV, Excel, JSON)
  - Column/field selection
  - Export preview (row count, field warnings)
  - Download or email delivery
  - Export history log

### 4.14 Export Schedules
- **Route**: `/admin/export/schedules`
- **Roles**: Admin
- **Features**:
  - Recurring export schedule configuration
  - Frequency selection (daily/weekly/monthly)
  - Approved email recipients
  - Format selection
  - Schedule enable/disable
  - Last run status

### 4.15 Integrations (Webhooks & API Keys)
- **Route**: `/admin/integrations`
- **Roles**: Admin
- **Features**:
  - Webhook configurations (event type, endpoint URL, headers)
  - Create/edit/delete webhooks
  - Test webhook button (send sample event)
  - Webhook delivery log (success/failure history)
  - API key management (create, revoke)
  - Key permissions scoping

### 4.16 Portal Admin
- **Route**: `/admin/portal`
- **Roles**: Admin
- **Features**:
  - Enable/disable public access per template
  - Public URL generation
  - Configure: require OTP, allow PDF download, send email confirmation
  - Rate limiting settings
  - CAPTCHA configuration
  - Portal submission dashboard

### 4.17 Batch Schedules
- **Route**: `/admin/batch-schedules`
- **Roles**: Admin
- **Features**:
  - Recurring batch job configuration
  - Template + data source + schedule (cron)
  - Enable/disable schedules
  - Last run status and next run time

### 4.18 Data Retention Policies
- **Route**: `/admin/retention/policies`
- **Roles**: Admin
- **Features**:
  - Retention policy list (per entity type)
  - Configure retention period (months/years)
  - Auto-archive and purge settings

### 4.19 Retention Jobs
- **Route**: `/admin/retention/jobs`
- **Roles**: Admin
- **Features**:
  - Retention job execution history
  - Job status, records affected
  - Pre-purge review

### 4.20 Legal Holds
- **Route**: `/admin/retention/holds`
- **Roles**: Admin
- **Features**:
  - Legal hold list (flagged records exempt from purge)
  - Create/release legal holds
  - Hold reason and scope

### 4.21 Archive Manifests
- **Route**: `/admin/retention/manifests`
- **Roles**: Admin
- **Features**:
  - Archived data manifests
  - Download archived data
  - Manifest metadata (date, scope, record count)

### 4.22 SSO Configuration
- **Route**: `/admin/sso`
- **Roles**: Admin
- **Features**:
  - Identity provider configuration (SAML 2.0, OIDC)
  - Provider details (entity ID, SSO URL, certificate)

### 4.23 SSO Domain Verification
- **Route**: `/admin/sso/verify`
- **Roles**: Admin
- **Features**:
  - Domain ownership verification
  - DNS record instructions
  - Verification status

### 4.24 SSO Attribute Mappings
- **Route**: `/admin/sso/mappings`
- **Roles**: Admin
- **Features**:
  - Map IdP attributes to FormCraft profile fields
  - Role mapping configuration
  - Department/branch auto-assignment

### 4.25 OCR Batch Onboarding List
- **Route**: `/admin/ocr-onboarding`
- **Roles**: Admin
- **Features**:
  - Batch OCR import jobs list
  - Job status and form count
  - Confidence scores

### 4.26 OCR Batch Create
- **Route**: `/admin/ocr-onboarding/new`
- **Roles**: Admin
- **Features**:
  - Upload multiple PDF/image files (up to 200)
  - Batch processing configuration

### 4.27 OCR Batch Detail
- **Route**: `/admin/ocr-onboarding/:batchId`
- **Roles**: Admin
- **Features**:
  - Per-form review dashboard
  - Thumbnail preview with confidence scores
  - Accept/reject/modify detections
  - Bulk approve high-confidence forms

### 4.28 Custom Locale Validators *(spec 048)*
- **Route**: `/admin/validators`
- **Roles**: Admin
- **Features**:
  - Validator list (name, pattern preview, field usage count)
  - Create/edit/delete org-scoped regex validators
  - Arabic + English error message per validator
  - Inline pattern tester (sample input → pass/fail preview)
  - Usage count: how many elements reference each validator

### 4.29 Granular Template Permissions *(spec 043)*
- **Route**: `/admin/template-permissions` or per-template Permissions tab
- **Roles**: Admin
- **Features**:
  - Permission rule list per template (grant + deny)
  - Add rule: scope (role / department / branch / user) + capabilities
  - Explicit deny rules that override any grant
  - Access diagnostic: "What can user X do with template Y?"
  - Decision trace: which rule granted or denied, in plain language

### 4.30 Enterprise SSO Configuration *(spec 042)*
- **Route**: `/admin/sso` (existing) — enhanced
- **Roles**: Admin
- **Features**:
  - SAML 2.0 and OIDC provider configuration (entity ID, SSO URL, certificate)
  - Domain-based sign-in routing (users on corp domain go directly to IdP)
  - Session timeout configuration (8h default, 30min idle)
  - Attribute → role / department / branch mapping

### 4.31 MFA Management *(spec 042)*
- **Route**: `/admin/sso/mfa`
- **Roles**: Admin
- **Features**:
  - Org-wide MFA policy (required / optional / off)
  - TOTP enrollment status per user
  - SMS OTP channel configuration (provider + rate limits)
  - Force-re-enroll action per user

### 4.32 Connector Framework *(spec 049)*
- **Route**: `/admin/connectors`
- **Roles**: Admin
- **Features**:
  - Connector list (type, status, last delivery)
  - Add connector: DMS / CRM / Email / Banking Core
  - Configure: endpoint URL, auth (API key / OAuth), field mapping
  - Event subscription: form_submitted / form_printed / template_published / batch_completed
  - Delivery log: event history per connector (status, response code, payload preview)
  - Test connector button (send sample event)
  - Retry configuration (exponential backoff settings)

---

## 5. ANALYTICS — Admin/Designer Routes

### 5.1 Field Analytics
- **Route**: `/admin/analytics/fields`
- **Roles**: Admin, Designer
- **Features**:
  - Error rates per field
  - Most common validation errors
  - Fields most often left empty
  - Field-level performance metrics

### 5.2 Operator Analytics
- **Route**: `/admin/analytics/operators`
- **Roles**: Admin, Designer
- **Features**:
  - Forms processed per operator (day/week/month)
  - Average fill time per operator
  - Error rate per operator
  - Busiest hours heatmap
  - Operator comparison (side-by-side)

### 5.3 Compliance Analytics
- **Route**: `/admin/analytics/compliance`
- **Roles**: Admin, Designer
- **Features**:
  - Template quality scores across org
  - Validator coverage percentage
  - Bilingual label coverage percentage
  - Approval workflow adherence
  - Customer data access patterns

### 5.4 Template Usage Analytics
- **Route**: `/admin/analytics/templates`
- **Roles**: Admin, Designer
- **Features**:
  - Most-used templates ranked by fill count
  - Fill completion rate per template
  - Average fill time per template
  - Version adoption curve
  - Stale templates (90+ days unused)
  - Department/branch usage breakdown

---

## 6. REPORTS — Admin Routes

### 6.1 Transaction Register
- **Route**: `/admin/reports/transactions`
- **Roles**: Admin
- **Features**:
  - All submissions in a date range
  - Filter by: template, operator, branch, department, customer, status, amount range
  - Columns: ref number, template, operator, customer, date, key fields, status
  - Export: Excel, CSV, PDF

### 6.2 Daily Reconciliation
- **Route**: `/admin/reports/reconciliation`
- **Roles**: Admin
- **Features**:
  - Per-operator/branch totals for a single day
  - Total submissions, total amount, breakdown by template
  - End-of-day teller reconciliation view

### 6.3 Period Summary
- **Route**: `/admin/reports/period-summary`
- **Roles**: Admin
- **Features**:
  - Aggregate totals for week/month/quarter/year
  - Group by: department, branch, template, operator, cost center
  - Metrics: count, total amount, average, min/max
  - Period-over-period comparison with trend arrows

### 6.4 Custom Report Builder
- **Route**: `/admin/reports/builder`
- **Roles**: Admin
- **Features**:
  - Select dimensions (template fields, submission metadata, customer data)
  - Apply filters (date, branch, department, operator, template)
  - Choose aggregation (count, sum, average, distinct)
  - Group by any dimension
  - Choose visualization (table, bar chart, line chart, pie chart)
  - Save as named report
  - Export: Excel, CSV, PDF

### 6.5 Beneficiary Report
- **Route**: `/admin/reports/financial/beneficiary`
- **Roles**: Admin
- **Features**:
  - All transactions for a specific beneficiary
  - Filter by: date, template type, amount range
  - Cross-template beneficiary view

### 6.6 Void & Reprint Register
- **Route**: `/admin/reports/financial/void-reprint`
- **Roles**: Admin
- **Features**:
  - All voided, cancelled, or reprinted submissions
  - Original reference, void reason, who voided/reprinted
  - Fraud monitoring flags (>3 reprints)

### 6.7 Signatory Usage Report
- **Route**: `/admin/reports/financial/signatory-usage`
- **Roles**: Admin
- **Features**:
  - Which signatories authorized which transactions
  - Filter by: signatory, amount range, date, template
  - Authority limit alerts

### 6.8 Report Schedules
- **Route**: `/admin/reports/schedules`
- **Roles**: Admin
- **Features**:
  - Scheduled report configurations
  - Frequency + recipients + format
  - Enable/disable schedules
  - Last run and next run timestamps

---

## 7. PLATFORM CONSOLE — Platform Admin Routes

### 7.1 Platform Dashboard
- **Route**: `/platform`
- **Roles**: Platform Admin (is_platform_admin=true)
- **Features**:
  - Total organizations, users, submissions (platform-wide)
  - Organizations by tier (chart)
  - Submission volume trend (chart)
  - Recently created organizations
  - Organizations approaching tier limits (alerts)

### 7.2 Organization List
- **Route**: `/platform/organizations`
- **Roles**: Platform Admin
- **Features**:
  - All organizations with search, filter, sort
  - Columns: name, tier, active users, templates, submissions, status
  - Filter by: tier, status, country
  - Create organization button
  - Suspend/reactivate actions

### 7.3 Create Organization
- **Route**: `/platform/organizations/create`
- **Roles**: Platform Admin
- **Features**:
  - Organization creation form (name AR+EN, language, country, currency)
  - Subscription tier selection
  - Auto-generate first admin invitation

### 7.4 Organization Detail
- **Route**: `/platform/organizations/:id`
- **Roles**: Platform Admin
- **Features**:
  - Profile tab (name, logo, domain, branding)
  - Subscription tab (tier, limits, usage)
  - Users tab (user count by role)
  - Stats tab (templates, submissions, storage)
  - Suspend/reactivate actions

---

## 8. FEEDBACK — Cross-Role Routes

### 8.1 Product Feedback Admin
- **Route**: `/admin/feedback`
- **Roles**: Admin
- **Features**:
  - All product feedback submissions
  - Search by text, filter by status/submitter/date/labels
  - Label management (create/assign up to 5 per submission)
  - Threaded conversation replies
  - Media previews (images, audio, video)
  - Unread indicators

### 8.2 My Feedback (User View)
- **Route**: `/my-feedback`
- **Roles**: Any authenticated user
- **Features**:
  - User's own feedback submissions
  - View admin replies (threaded conversation)
  - Submit new feedback
  - Attach media (images, audio, video)

---

## 9. MARKETPLACE — Admin Routes

### 9.1 Marketplace Browse
- **Route**: `/marketplace`
- **Roles**: Admin
- **Features**:
  - Browse published templates by country, category, compliance standard, price
  - Template cards with preview, quality score, ratings
  - "Use Template" button (clone to own org)

### 9.2 Marketplace Publish
- **Route**: `/marketplace/publish`
- **Roles**: Admin
- **Features**:
  - Mark template as marketplace available
  - Add description, tags, preview images
  - Set pricing (free/premium)
  - Compliance certifications

### 9.3 Marketplace Detail
- **Route**: `/marketplace/:id`
- **Roles**: Admin
- **Features**:
  - Template detail view
  - Read-only canvas preview
  - Sample PDF output
  - Ratings and reviews
  - Download count

### 9.4 Marketplace Review
- **Route**: `/marketplace/:id/review`
- **Roles**: Admin
- **Features**:
  - Quality review interface
  - Approval/rejection for marketplace listing

---

## 10. DIGITAL SIGNATURES

### 10.1 Digital Signatures Dashboard
- **Route**: `/admin/digital-signatures` (implied from routing)
- **Roles**: Admin
- **Features**:
  - Signature request management

### 10.2 Signature Workflows
- **Route**: `/admin/digital-signatures/workflows`
- **Features**:
  - Signature workflow configuration

### 10.3 Signature Request Detail
- **Route**: `/admin/digital-signatures/requests/:id`
- **Features**:
  - Signature request status and tracking

### 10.4 Signature Evidence
- **Route**: `/admin/digital-signatures/evidence/:id`
- **Features**:
  - Signature audit evidence view

### 10.5 Public Signature Page
- **Route**: `/admin/digital-signatures/sign/:token`
- **Features**:
  - External signer interface (token-based, no login)

---

## 11. UI REDESIGN — New Theme *(specs 041, 050, 051, 052–056)*

> All new-theme routes use **real API data** — no mocks. Spec 050 replaced all hardcoded placeholders with live backend calls.

### 11.1 Studio Templates (New Theme)
- **Route**: `/ui/studio/templates`
- **Features**: Same as `/templates` with new-theme shell; same real template data

### 11.2 Studio Wizard (New Theme)
- **Route**: `/ui/studio/wizard`
- **Features**: Same as `/templates/new` with new-theme shell

### 11.3 Studio Designer (New Theme)
- **Route**: `/ui/studio/designer`
- **Features**: Same as `/designer/:templateId` with new-theme shell

### 11.4 Desk Dashboard (New Theme) *(spec 050)*
- **Route**: `/ui/desk`
- **Features**:
  - Live KPI cards: submission count, draft count, template count (real API — no mocks)
  - Recent activity feed: 10 real items with "View All" link
  - Actual operator drafts from `/api/desk/drafts`
  - Pinned and frequent templates from real API data
  - Same filters, search, and navigation as classic `/desk`
  - Data fetches on-load (no background polling)

### 11.5 Desk Form Filler (New Theme) *(specs 052–053)*
- **Route**: `/ui/desk/fill/:templateId`
- **Features**:
  - Full parity with classic filler: all field types, validation, conditional logic, drafts, submit
  - Auto-save on navigation (no explicit Save Draft button needed)
  - Submission-confirmed screen shows reference number inline
  - Draft resumption via slide-out list panel discovery
  - Canvas-drawn signature pad (touch + mouse)
  - Audit log entry on each signature captured
  - *Classic-only (not in new theme)*: Print & Next mode, offline sync, Clone as New

### 11.6 Desk Customers (New Theme)
- **Route**: `/ui/desk/customers`
- **Features**: Same as `/desk/customers` with new-theme shell

### 11.7 Admin Analytics (New Theme) *(spec 054)*
- **Route**: `/ui/admin/analytics`
- **Features**:
  - Real KPIs and charts from live aggregation queries (no mock data) — spec 054
  - 5-minute TTL cache on aggregation results (fast dashboards, bounded staleness)
  - Same date-range / department / branch filters as classic analytics

### 11.8 Custom Validators Admin (New Theme)
- **Route**: `/ui/admin/validators`
- **Features**: Same as `/admin/validators` with new-theme shell

### 11.9 Admin Export (New Theme) *(spec 055)*
- **Route**: `/ui/admin/export`
- **Features**: Spark3 Export admin page — data export configuration and history

### 11.10 Admin Portal (New Theme) *(spec 055)*
- **Route**: `/ui/admin/portal`
- **Features**: Spark3 external-form Portal admin page — portal configuration

### 11.11 Admin Integrations (New Theme) *(spec 055)*
- **Route**: `/ui/admin/integrations`
- **Features**: Spark3 Integrations admin page — connector/integration management

### 11.12 Add Customer (New Theme) *(spec 056)*
- **Route**: `/ui/desk/customers/new`
- **Features**:
  - Two-column reactive form (Spark theme)
  - Field-level validation messages
  - Inline 409 (duplicate customer) error handling — no full-page error
  - Backed by existing `CustomerService`

---

## 12. SHARED UI COMPONENTS (Screenshot on Any Page)

### 12.1 Navigation Bar
- **Features**:
  - Mode switcher tabs (Design Studio / Form Desk / Admin / Platform)
  - Notification bell with unread count
  - Language toggle (AR/EN)
  - User profile menu
  - Platform tab (only if is_platform_admin=true)

### 12.2 Notification Panel
- **Features**:
  - Recent notifications dropdown
  - Mark as read / mark all as read
  - Deep links to relevant pages
  - Filter by type, read status

### 12.3 User Profile
- **Route**: `/auth/profile`
- **Features**:
  - Display name, email, language preference
  - Role and department/branch display
  - Theme preference (classic/redesigned)
  - Notification preferences per type per channel

### 12.4 Product Feedback Widget
- **Features** (persistent floating widget on every page):
  - Feedback text input
  - Image attachment (up to 5)
  - Audio/video recording or upload
  - Auto-captures page URL and user context

---

## Summary — Total Routes for Playwright

| Section | Route Count |
|---------|:-----------:|
| Auth & Public | 7 |
| Design Studio | 3 |
| Form Desk | 8 |
| Admin Console | 27 |
| Analytics | 4 |
| Reports | 8 |
| Platform Console | 4 |
| Feedback | 2 |
| Marketplace | 4 |
| Digital Signatures | 5 |
| UI Redesign | 11 |
| Shared Components | 4 |
| **Total** | **87** |
