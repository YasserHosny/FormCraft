# FormCraft — Complete Platform Functionality & Business Value

> A user-centric view of every function, its business value, and the closed-cycle flows that connect them.
> Date: 2026-05-16 | Last validated: 2026-05-25

Validated against `formcraft-specs/specs/001-auth-users` through `formcraft-specs/specs/040-enhanced-analytics`, with later roadmap items represented as vision-level capabilities when they do not yet have full plan/task artifacts.

---

## Table of Contents

1. [Platform Identity](#platform-identity)
2. [The Closed Cycle](#the-closed-cycle)
3. [User Roles & Their Primary Cycles](#user-roles--their-primary-cycles)
4. [Function Map with Business Value](#function-map-with-business-value)
   - [Stage 1: ONBOARD — Digitize Existing Forms](#stage-1-onboard--digitize-existing-forms)
     - F-SCAN: Form Scanning & OCR Import
     - F-BATCH-SCAN: Batch Form Library Digitization
   - [Stage 2: DESIGN — Create & Perfect Templates](#stage-2-design--create--perfect-templates)
     - F-CREATE: Template Creation
     - F-CANVAS: Visual Form Design
     - F-AI: AI-Powered Field Suggestions
     - F-TAFQEET: Amount-to-Words Conversion
     - F-VALIDATE: Arabic-Specific Validation
     - F-CONDITIONAL: Smart Form Logic
     - F-VERSION: Template Versioning & Lifecycle
     - F-APPROVE: Template Approval Workflow
     - F-GOVERNANCE: Template Governance
     - F-PDF: PDF Rendering Engine
     - F-REFDATA: Reference Data Manager
   - [Stage 3: OPERATE — Fill, Print, Archive](#stage-3-operate--fill-print-archive)
     - F-DESK: Operator Dashboard
     - F-FILL: Form Filler
     - F-PRINT: Print & Submit
     - F-OVERLAY: Overlay Print Mode
     - F-DRAFT: Save & Resume
     - F-HISTORY: Submission History & Reprint
     - F-CUSTOMER: Customer Profiles
     - F-BATCH: Batch Operations & Print Queue
     - F-SEARCH: Form Desk Search & Quick Fill
     - F-FEEDBACK: Template Feedback
   - [Stage 4: ANALYZE — Measure & Optimize](#stage-4-analyze--measure--optimize)
     - F-ANALYTICS-TEMPLATE: Template Analytics
     - F-ANALYTICS-OPERATOR: Operator Performance
     - F-ANALYTICS-COMPLIANCE: Compliance Analytics
     - F-ANALYTICS-ORG: Organizational Analytics
     - F-REPORT: Scheduled Reports
     - F-REPORT-OPS: Operational Reports
   - [Stage 5: GOVERN — Control & Secure](#stage-5-govern--control--secure)
     - F-PLATFORM: Platform Admin Console
     - F-ORG: Organization & Tenant Management
     - F-USERS: User & Access Management
     - F-AUDIT: Audit Trail & Compliance
     - F-NOTIFY: Notification System
     - F-USER-FEEDBACK: Product Feedback & Support Loop
   - [Stage 6: INTEGRATE — Connect & Extend](#stage-6-integrate--connect--extend)
     - F-API: REST API & Programmatic Access
     - F-WEBHOOK: Event Webhooks
     - F-PORTAL: External Form Portal
     - F-EXPORT: Data Export & Portability
     - F-MARKETPLACE: Template Marketplace
5. [Complete User Journeys](#complete-user-journeys-end-to-end-closed-cycles)
6. [Closed Cycle Summary](#closed-cycle-summary)
7. [Business Value Summary by Stakeholder](#business-value-summary-by-stakeholder)

---

## Platform Identity

**FormCraft** is the Arabic-first enterprise form platform that covers the entire document lifecycle: scan existing paper forms, design pixel-perfect templates, fill them with live validation, print or distribute digitally, and analyze operations — all in one platform.

**Target market**: Banks, government ministries, insurance companies, and enterprises in Egypt, Saudi Arabia, and the UAE.

**Core promise**: Eliminate paper form chaos. One platform replaces the disconnected workflow of scanning, designing in Word/InDesign, manually filling forms, and tracking submissions in spreadsheets.

---

## The Closed Cycle

Every function in FormCraft serves one continuous cycle. The platform has no dead ends — every output feeds the next stage.

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                                                                              │
│   ┌──────────┐    ┌───────────┐    ┌──────────┐    ┌──────────┐            │
│   │  ONBOARD │───>│  DESIGN   │───>│  OPERATE │───>│  ANALYZE │            │
│   │          │    │           │    │          │    │          │            │
│   │ Scan     │    │ Create    │    │ Fill     │    │ Measure  │            │
│   │ Digitize │    │ Validate  │    │ Print    │    │ Optimize │            │
│   │ Import   │    │ Approve   │    │ Overlay★ │    │ Report★  │            │
│   │          │    │ Ref Data★ │    │ Archive  │    │ Reconcile│            │
│   └──────────┘    └───────────┘    └──────────┘    └──────────┘            │
│        ^                                                  │                  │
│        │                                                  │                  │
│        └──────────────────────────────────────────────────┘                  │
│                        FEEDBACK LOOP                                          │
│              (Analytics inform redesign; operator feedback                    │
│               triggers template updates; new versions                         │
│               flow back to operations)                                        │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## User Roles & Their Primary Cycles

| Role | Primary Mode | Daily Activity | Business Responsibility |
|------|:------------:|----------------|------------------------|
| **Platform Admin** | Platform Console | Create, monitor, suspend, and support tenant organizations | SaaS operations, tenant health, subscription oversight |
| **Org Admin** | Admin Console | Configure org, manage users, approve templates, review analytics | Governance, compliance, operational oversight |
| **Designer** | Design Studio | Create and iterate form templates, respond to feedback | Form accuracy, regulatory compliance, design quality |
| **Reviewer capability** | Admin Console | Branch managers and admins review submitted templates, approve or reject with comments | Quality gate, compliance verification |
| **Operator** | Form Desk | Fill forms for customers, print, manage queue | Daily operations, customer service, throughput |
| **Branch Manager** | Admin Console | Monitor branch analytics, manage local operators | Branch performance, staffing, training |
| **External User** | Public Portal | Fill public forms online, download receipts | Self-service, reduced branch visits |

---

## Function Map with Business Value

### Stage 1: ONBOARD — Digitize Existing Forms

> **Business problem solved**: "We have 300 paper forms accumulated over 20 years. Recreating them all manually would take months."

#### F-SCAN: Form Scanning & OCR Import

```
User flow:
    Admin or Designer uploads scanned form (PDF or image)
    -> Azure Document Intelligence detects all fields (bounding boxes + type classification)
    -> AI suggests: field type, label, validation rules per detected field
    -> Canvas displays detection overlays
    -> User reviews each detection: Accept / Reject / Modify
    -> Accepted detections become FormCraft elements with suggested properties
    -> Result: paper form digitized into editable template in minutes, not days
```

| Business Value | Metric |
|----------------|--------|
| Reduces onboarding time | From 6 months (manual) to 1-2 weeks (OCR-assisted) |
| Preserves institutional knowledge | Legacy forms captured exactly as they exist |
| Lowers migration resistance | "We don't have to start from zero" removes adoption barrier |
| Demonstrates immediate ROI | Customer sees results on day 1 of engagement |

#### F-BATCH-SCAN: Batch Form Library Digitization

```
User flow:
    Admin uploads up to 200 scanned forms at once
    -> Background OCR job processes all forms
    -> Progress dashboard shows: processing, completed, needs review
    -> AI auto-classifies form types and suggests categories
    -> Review dashboard: each form as a card with confidence score
    -> Bulk approve high-confidence forms (>90%)
    -> Manual review for low-confidence forms
    -> Result: entire organizational form library digitized in days
```

| Business Value | Metric |
|----------------|--------|
| Enterprise sales enabler | "We digitize your entire form library in a week" |
| Reduces professional services cost | Self-service import vs. paid consultants |
| Accelerates time-to-value | Organization operational on FormCraft within first month |

---

### Stage 2: DESIGN — Create & Perfect Templates

> **Business problem solved**: "Our forms must be pixel-perfect for print, comply with regulations, support Arabic/English, and be updated whenever rules change — without breaking existing operations."

#### F-CREATE: Template Creation

```
User flow:
    Designer clicks "New Template"
    -> Multi-step wizard:
        1. Basic Info: bilingual-aware name, description, category, tags
        2. Locale: language, country, currency, with org defaults pre-selected
        3. Page Setup: preset/custom page size in mm, orientation, margins
        4. Starting Point: blank canvas / clone existing / import from scan / import package
    -> Template created in "draft" status with one default page
    -> Designer enters Design Studio canvas with wizard settings already applied

    Starting points:
    -> Blank Canvas: new empty template
    -> Clone Existing: preserves pages, elements, properties, validators, conditions, bindings
    -> Import from Scan: launches OCR detection review flow
    -> Import Package: validates portable FormCraft package and warns about missing references

Business value:
    - Structured creation prevents incomplete templates
    - Category and tagging enable searchability at scale (when org has 200+ templates)
    - Country selection auto-configures relevant validators (EG vs SA vs AE rules)
    - Clone from existing eliminates redundant work for similar forms
    - Import package supports dev/staging/prod promotion and template reuse across orgs
```

#### F-CANVAS: Visual Form Design (Design Studio)

```
User flow:
    Designer works on a full canvas editor:
    -> Drag elements from palette onto canvas (text, number, date, currency,
       checkbox, radio, dropdown, image, QR, barcode, tafqeet, signature, table)
    -> Position elements at exact mm coordinates (grid snap: 1/2/5/10 mm)
    -> Configure each element: labels (AR+EN), validation rules, formatting,
       direction, default values, conditional logic, help text
    -> Multi-page support: add/remove/reorder pages
    -> Undo/redo (50 steps), copy/paste, multi-select, alignment tools
    -> Auto-save every 2 seconds of inactivity
    -> Live PDF preview at any time

Business value:
    - mm-precision guarantees print output matches screen exactly
    - Bilingual labels (AR+EN) on every field = one template serves both languages
    - WYSIWYG editing: non-technical users can design forms (no InDesign/Illustrator needed)
    - Undo/redo + auto-save = fearless editing, no lost work
```

#### F-AI: AI-Powered Field Suggestions

```
User flow:
    Designer types a field label (e.g., "رقم الهوية الوطنية")
    -> System checks deterministic validators first (known patterns = instant, 100% confidence)
    -> If no match: AI (Claude Haiku via AWS Bedrock) suggests field type + validation rules
    -> Suggestion chip appears: "Suggested: National ID — 14 digits (confidence: 98%)"
    -> Designer clicks Accept (auto-fills properties) or Dismiss (no change)
    -> AI never auto-applies — designer always in control

Business value:
    - Reduces design time by 40-60% (auto-configures validation, formatting, type)
    - Ensures compliance: AI knows that "رقم الهوية" in Egypt = 14-digit national ID
    - Deterministic-first: known fields (IBAN, national ID, VAT) always correct, never hallucinated
    - Consistency: same field label always gets same suggestion across all templates
```

#### F-TAFQEET: Amount-to-Words Conversion

```
User flow:
    Designer drags "Tafqeet" element onto canvas
    -> Links it to a source currency/number field on the same page
    -> Configures: output language (Arabic / English / Both), currency name, prefix/suffix
    -> Canvas shows live preview: "1500.25" -> "ألف وخمسمائة جنيه مصري وخمسة وعشرون قرشاً"
    -> Overflow warning if text exceeds bounding box

    At fill time (Form Desk):
    -> Operator types amount -> tafqeet field auto-computes instantly
    -> PDF output includes the tafqeet text at exact position

Business value:
    - Legal requirement on cheques and financial documents in MENA
    - Eliminates manual errors in amount-to-words conversion
    - Supports multiple currencies (EGP, SAR, AED) with proper Arabic grammar
    - Reduces cheque rejection rate due to amount-words mismatch
```

#### F-VALIDATE: Arabic-Specific Validation

```
User flow:
    Designer assigns validation rules to fields (automatic via AI or manual):
    -> Egyptian National ID: exactly 14 digits, starts with 2 or 3
    -> Saudi Iqama: exactly 10 digits, starts with 1 or 2
    -> UAE IBAN: "AE" + 21 characters
    -> Egyptian phone: +20 prefix + 10 digits
    -> Saudi VAT: 15 digits, starts and ends with 3
    -> Custom validators: org-defined regex patterns

    At fill time (Form Desk):
    -> Validation fires on each keystroke
    -> Invalid input: red border + bilingual error message
    -> Form cannot be submitted until all validations pass

Business value:
    - Prevents data entry errors at the source (not caught downstream)
    - Country-specific: same platform works correctly in EG, SA, and AE
    - Reduces form rejection rate (bank rejects cheque with invalid IBAN = customer frustration)
    - Compliance: regulatory bodies require proper format enforcement
    - Custom validators: each org can add their own rules without code changes
```

#### F-CONDITIONAL: Smart Form Logic

```
User flow:
    Designer configures conditional rules on elements:
    -> visible_when: { field: "account_type", equals: "corporate" }
       (Corporate-only fields hidden until account_type is "corporate")
    -> required_when: { field: "amount", greater_than: 10000 }
       (Manager approval field required only for amounts > 10,000)
    -> computed_value: { formula: "subtotal * 0.14" }
       (Tax field auto-calculates from subtotal)

    At fill time (Form Desk):
    -> Fields appear/disappear dynamically as operator fills the form
    -> Required indicators update in real-time
    -> Computed fields auto-calculate (no manual entry needed)

Business value:
    - Reduces form complexity: operators only see relevant fields
    - Prevents errors: computed fields eliminate manual calculation mistakes
    - Enables complex multi-purpose forms: one template handles multiple scenarios
    - Reduces template proliferation: one smart form replaces 5 static variants
```

#### F-VERSION: Template Versioning & Lifecycle

```
User flow:
    Designer creates template (v0 draft)
    -> Designer submits for review
    -> Reviewer approves (or rejects with comments)
    -> Admin publishes -> becomes v1.0
    -> Regulatory change requires update:
        -> Designer clones v1.0 into new draft
        -> Modifies fields to comply with new regulation
        -> Submits for review -> approved -> published as v2.0
    -> v1.0 marked as deprecated (warning shown to operators)
    -> Operators automatically see v2.0 in Form Desk
    -> Old submissions retain reference to v1.0 (audit trail intact)

    Version diff:
    -> Admin or designer views side-by-side comparison of v1.0 vs v2.0
    -> Shows: added fields, removed fields, changed properties, moved elements

Business value:
    - Regulatory compliance: prove which form version was in use on any date
    - Zero disruption updates: new version goes live without breaking existing drafts
    - Audit trail: every change tracked, every reviewer identified
    - Rollback capability: if v2.0 has issues, v1.0 still accessible
    - Template lineage: complete history from creation through all revisions
```

#### F-APPROVE: Template Approval Workflow

```
User flow:
    Designer completes template -> clicks "Submit for Review"
    -> Template status changes to "submitted" (no longer editable)
    -> Branch manager / admin reviewer receives notification
    -> Reviewer opens template in read-only preview mode:
        -> Views canvas layout
        -> Checks validation rules
        -> Verifies bilingual labels
        -> Sees AI quality score
    -> Reviewer decision:
        Approve -> template moves to "approved" queue
        Reject -> template returns to designer with per-element comments
        Request Changes -> specific element-level notes (like code review)
    -> Admin sees approved templates -> publishes with one click
    -> Full audit trail: who submitted, who reviewed, when, what comments
    -> Designer may withdraw before review decision; withdrawal returns template to draft

Business value:
    - Compliance: no single person can create and publish a financial form
    - Quality gate: catches errors before forms reach operators
    - Accountability: every approval decision documented
    - Banking regulation: many jurisdictions require multi-person authorization for form changes
    - Reduces errors reaching production: 4-eyes principle enforced
```

#### F-GOVERNANCE: Template Governance

```
User flow:
    Org Admin opens /admin/governance
    -> Single template oversight list across all statuses
    -> Filters by status, department, category, designer, stale/active, and usage
    -> Bulk actions:
        Archive selected templates
        Reassign designer
        Change category
    -> Published-template archive warns about recent usage impact before proceeding

    Review quality tools:
    -> Submitted templates open with read-only canvas preview
    -> Reviewer pins comments to exact canvas coordinates in millimeters
    -> Updated templates show version diff against the previous published version
    -> Designer resolves comments before resubmission

    Compliance dashboard:
    -> Validator coverage %
    -> Bilingual label %
    -> Help text coverage %
    -> Tab order completeness
    -> Overall quality score
    -> Stale templates not updated in 6+ months
    -> Regulatory rule-change impact across affected templates

Business value:
    - Gives admins one place to manage template health across the organization
    - Makes reviews faster because comments are anchored to the actual visual design
    - Prevents forgotten templates from drifting out of compliance
    - Turns quality standards into measurable governance metrics
    - Audit trail captures bulk actions, review comments, and compliance decisions
```

#### F-PDF: PDF Rendering Engine

```
User flow:
    Designer clicks "Preview PDF" at any time during design
    -> Backend generates PDF with WeasyPrint
    -> All elements rendered at exact mm positions matching canvas
    -> Arabic text properly shaped (arabic-reshaper + python-bidi)
    -> Noto Naskh Arabic font embedded for consistent output
    -> PDF opens in browser overlay for verification

    At operation time:
    -> Operator fills form and prints -> PDF generated with actual data
    -> Batch processing -> 500 PDFs generated from CSV in background

Business value:
    - Print-perfect output: what's on screen matches what's on paper, every time
    - Arabic typography: proper glyph shaping, no broken characters
    - Font embedding: PDFs look identical on any printer, any OS
    - Fast generation: < 3 seconds for standard A4 form
    - Replaces expensive desktop publishing software for form production
```

#### F-REFDATA: Reference Data Manager

```
User flow:
    Admin opens /studio/reference-data -> "New List"
    -> Defines list: name, scope (org/department/branch), columns:
        Example: "Authorized Signatories"
            name_ar (text, required)
            name_en (text, required)
            title_ar (text)
            signature_image (file)
            authority_level (dropdown: branch/regional/executive)
            max_amount (currency)
    -> Populates entries: manual entry or bulk import from CSV/Excel
    -> Each entry has: active/inactive toggle, effective from/to dates

    Designer binds list to form fields:
    -> In Canvas Editor, selects a field (e.g., "Signatory Name")
    -> Properties: Data Source = "Reference List" -> "Authorized Signatories"
    -> Maps columns to form fields:
        signatory_name <- list.name_ar
        signatory_title <- list.title_ar
        signature_image <- list.signature_image
    -> One selection auto-populates all mapped fields

    At fill time (Form Desk):
    -> Operator reaches bound field -> searchable dropdown of active entries
    -> Types to filter -> selects entry -> all mapped fields auto-fill
    -> Audit log records which entry was selected

    Cascading lists:
    -> Department -> Cost Centers (filtered by department) -> Approver (filtered by cost center)

    Common organizational lists:
    -> Authorized signatories (name, title, signature, authority limit)
    -> Beneficiaries / payees (name, ID, bank account, IBAN)
    -> Cost centers / GL accounts (code, name, department)
    -> Currencies with tafqeet configuration
    -> Department heads / approvers (name, title, approval limit)

Business value:
    - Eliminates re-typing: signatory names, beneficiary details entered once, used everywhere
    - Enforces authorized values: operators can only pick from approved lists
    - Auditability: every transaction traceable to which signatory/beneficiary was selected
    - Governance: deactivate a signatory on leave — immediately unavailable on all forms
    - Reduces errors: no more misspelled beneficiary names or wrong account numbers
    - Cascading filters: operators see only relevant options, reducing selection time
    - Central management: one update to a list entry propagates to all templates using it
```

---

### Stage 3: OPERATE — Fill, Print, Archive

> **Business problem solved**: "Our 500 branch operators fill the same forms hundreds of times daily. They need speed, accuracy, and a record of everything they've processed."

#### F-DESK: Operator Dashboard

```
User flow:
    Operator logs in -> lands on Form Desk dashboard
    -> "Quick Actions": search bar + recent templates
    -> "Pinned Forms": operator's favorites (starred) for one-click access
    -> "Recent": last 10 forms filled — click to refill same template
    -> "Drafts": partially filled forms waiting to be completed (with age + expiry warning)
    -> Notifications: new template versions, feedback responses, batch completions
    -> Click any form card -> enters Form Filler

Business value:
    - Reduces time-to-first-keystroke: operator finds their form in < 5 seconds
    - Personalized workspace: each operator sees their most-used forms first
    - Draft awareness: prevents forgotten incomplete forms from expiring
    - Notification-driven: operators learn about new template versions immediately
```

#### F-FILL: Form Filler (the daily workhorse)

```
User flow:
    Operator selects a published template
    -> Form Filler loads all fields as interactive form controls
    -> Two layout modes:
        Flow Layout: fields stacked vertically, optimized for keyboard speed
        Print Layout: fields at exact mm positions matching PDF output (WYSIWYG)
    -> Operator fills fields:
        -> Tab key moves between fields in logical order
        -> Validation fires on each keystroke (national ID, IBAN, phone, etc.)
        -> Tafqeet fields auto-compute as amounts are typed
        -> Conditional fields appear/disappear based on entered values
        -> Computed fields auto-calculate (tax, totals, etc.)
    -> Error summary banner: "2 required fields remaining"
    -> All required fields filled + all validations pass = Print button enables

    Customer auto-populate (optional):
    -> Operator clicks "Select Customer" or types customer name
    -> Customer profile selected from address book
    -> Known fields auto-fill (name, ID, phone, address)
    -> Operator fills only the remaining fields
    -> Reduces fill time from 3 minutes to 30 seconds for repeat customers

Business value:
    - Speed: keyboard-optimized flow layout enables 10x faster filling than paper
    - Accuracy: real-time validation catches errors before print (no rejected forms)
    - Consistency: every operator produces the same quality output
    - Customer experience: auto-populate from profiles = faster service at the counter
    - Training reduction: help text and validation guide new operators
```

#### F-PRINT: Print & Submit

```
User flow:
    Operator clicks "Print" (or Ctrl+P)
    -> Final validation check (all required fields, all validators pass)
    -> If errors: scroll to first error, highlight it, block print
    -> If valid:
        -> PDF generated with filled data
        -> Browser print dialog opens
        -> On print confirmation:
            -> Submission record created with unique reference number (FC-2026-05-0042)
            -> Submission linked to: template version, operator, branch, customer (if selected)
            -> Audit log: FORM_PRINTED event with all metadata
            -> Toast: "Printed successfully. Ref: FC-2026-05-0042"

    "Print & Next" mode (high-throughput):
    -> Same as Print but form resets immediately for next customer
    -> No intermediate confirmation screen
    -> Optimized for bank teller processing 50+ forms per hour

    "Submit without Print" mode (digital workflows):
    -> Form data saved as submission without generating PDF
    -> Use case: data collection where PDF comes later or goes to another system

Business value:
    - Reference numbers enable tracking and customer follow-up
    - Audit trail: every form printed is permanently recorded (who, when, what, where)
    - Print & Next: maximizes throughput in high-volume environments
    - Flexibility: support both print-heavy and digital-first workflows
    - Branch accountability: submissions tagged with branch for performance tracking
```

#### F-OVERLAY: Overlay Print Mode (printing on pre-printed stationery)

```
User flow:
    Designer configures template print mode (in Design Studio):
    -> Template Settings: Print Mode = "Full" | "Overlay" | "Both"
    -> For Overlay mode:
        -> Uploads scan of blank pre-printed form (cheque book, certificate, letterhead)
        -> Scan displayed as canvas background for positioning reference
        -> Designer positions data fields at exact mm coordinates on top of scan
        -> Scan is design-time only — excluded from printed output
    -> Per-element: "Include in overlay" toggle
        -> Data fields: included (default)
        -> Static labels/borders: excluded (already on pre-printed paper)
        -> Exceptions: org stamp or logo that should print even in overlay mode

    Printer calibration (one-time per physical printer):
    -> Operator opens /desk/settings/printers -> "Add Printer Profile"
    -> Names the printer (e.g., "Teller Window 3 — HP LaserJet")
    -> Clicks "Print Calibration Page"
        -> A4 page with crosshair grid at known mm positions prints
        -> Operator compares printed grid to expected positions
        -> Enters offset: X = +1.5 mm, Y = -0.8 mm
    -> Profile saved — offsets applied automatically on future prints

    Print flow (operator, Form Desk):
    -> Operator fills form in Form Filler
    -> Clicks "Print" -> system detects overlay mode
    -> Dialog: "Select printer" (dropdown of saved profiles for this branch)
    -> Preview toggle:
        "Overlay Preview" — only filled data on transparent background
        "Composite Preview" — filled data overlaid on stationery scan (verification)
    -> Operator loads pre-printed stationery into printer tray
    -> Clicks "Print Overlay" -> only data values sent to printer at calibrated positions
    -> Result: filled data lands at exact mm positions on pre-printed paper

Business value:
    - THE critical feature for bank cheque printing: banks have pre-printed cheque books
      with security paper, watermarks, and MICR lines — they cannot print the background
    - Government certificates: data printed onto pre-printed official forms with seals
    - Insurance: claim forms printed on multi-part carbonless paper
    - Printer calibration: eliminates the #1 complaint about misaligned prints
    - Composite preview: operators verify alignment before wasting stationery
    - Multiple printer profiles: each teller window can have different calibration
    - Saves stationery cost: accurate first print = no wasted pre-printed forms
    - mm-precision: same accuracy guarantee as full print mode
```

#### F-DRAFT: Save & Resume

```
User flow:
    Operator partially fills a form (e.g., waiting for customer to return with documents)
    -> Clicks "Save Draft" (or Ctrl+S)
    -> Draft saved with: all entered data, completion percentage, auto-generated name
    -> Operator can close browser entirely

    Later (minutes, hours, or days):
    -> Operator opens /desk/drafts
    -> Sees all saved drafts: template name, completion %, last modified, expiry date
    -> Clicks draft -> form filler loads with all previously entered data
    -> Continues where they left off
    -> Submits/prints when ready

    Auto-save:
    -> Form state auto-saves every 60 seconds while open
    -> If browser crashes: operator's work preserved
    -> Drafts auto-expire after configurable period (7 days default)
    -> Warning notification 24 hours before expiry

Business value:
    - No lost work: browser crash, power outage, or lunch break = safe
    - Supports interrupted workflows: "customer will return tomorrow with the deed"
    - Reduces frustration: operators never re-enter data they already typed
    - Auto-expiry prevents stale data accumulation
```

#### F-HISTORY: Submission History & Reprint

```
User flow:
    Operator opens /desk/history
    -> Table of all forms they have submitted/printed
    -> Search by: reference number, date range, template, customer name, field values
    -> Each row shows: ref number, date, template, key fields, status

    Actions on past submissions:
    -> "View": read-only display of all filled data
    -> "Reprint": regenerate PDF from stored data (marked with REPRINT watermark + timestamp)
    -> "Clone as New": open form filler pre-filled with this submission's data
        -> Creates new submission with new reference number
        -> Use case: "same form type, different customer — start from the last one"
    -> "Export": download submission data as JSON or CSV

Business value:
    - Reprint on demand: customer lost their copy? Reprint in seconds (not re-enter everything)
    - Audit compliance: every reprint logged with reason
    - Clone as New: dramatically speeds up repetitive form processing
    - Searchable archive: find any form ever processed, by any criterion
    - Customer service: "Let me look up your form from last week" takes 10 seconds
```

#### F-CUSTOMER: Customer Profiles

```
User flow:
    Operator opens /desk/customers -> "New Customer"
    -> Enters: name (AR+EN), identifier (national ID), phone, email, address, custom fields
    -> Customer profile saved

    OR: Auto-created from form submission:
    -> Operator fills form with new customer data
    -> On submit: system auto-creates customer profile from filled fields
    -> Next time this customer visits: profile is available for auto-populate

    Customer lookup during form filling:
    -> Operator starts typing customer name or ID number
    -> Autocomplete suggests matching profiles
    -> Select profile -> relevant fields auto-fill instantly
    -> Operator fills remaining form-specific fields only

    Customer history:
    -> Click customer -> see all forms ever filled for this customer
    -> Cross-template view: "Ahmed has 2 KYC submissions, 5 cheques, 1 loan application"

Business value:
    - Speed: returning customers served in fraction of the time
    - Accuracy: pre-filled data from verified profile = fewer typos
    - Relationship visibility: operator sees customer's complete history
    - Compliance: know-your-customer data maintained in one place
    - Data quality: single source of truth for customer information (no re-keying)
```

#### F-BATCH: Batch Operations & Print Queue

```
User flow:
    Admin or Operator navigates to /desk/queue -> "New Batch Job"
    -> Select template (published only)
    -> Upload data source: CSV, Excel, paste from clipboard, or pull from API
    -> Column mapping UI: map CSV columns to template field keys
        -> Auto-map by matching headers to field labels
        -> Manual override for unmatched columns
    -> Validation preview: all rows checked against template rules
        -> Valid rows: green checkmarks
        -> Invalid rows: red with specific error per field per row
        -> Options: "Fix errors inline", "Skip invalid", "Cancel"
    -> Generate:
        -> Background job produces N PDFs
        -> Progress: "Generated 247/500 — estimated 3 min remaining"
        -> Each PDF = one form_submission record with batch_job_id
    -> Download: individual PDFs as ZIP, or merged single PDF, or send to print queue

    Scheduled batches:
    -> Admin configures recurring job: template + API data source + schedule (daily at 6am)
    -> System runs automatically, sends completion notification
    -> Use case: daily bank statement generation, monthly certificate issuance

Business value:
    - Mass document production: 500 personalized forms in 5 minutes (vs. 500 manual fills)
    - Bank statements, tax certificates, notification letters at scale
    - Scheduled automation: daily/weekly/monthly runs without human intervention
    - Error handling: invalid rows identified before generation (no wasted prints)
    - Integrates with core banking: pull data from API, generate forms automatically
```

#### F-SEARCH: Form Desk Search & Quick Fill

```
User flow:
    Global search bar at top of /desk:
    -> Operator types in universal search box
    -> Instant results across three categories:
        Templates: matching template names -> click to start filling
        Submissions: matching reference numbers -> jump to submission detail
        Customers: matching customer names/IDs -> show customer's recent forms

    Quick Fill mode:
    -> Operator selects template + selects customer profile in one step
    -> Customer's known data auto-populated into all matching fields
    -> Reference Data entries from last usage pre-selected (e.g., same cost center)
    -> Operator only fills remaining empty fields (amount, date, specifics)
    -> Reduces fill time from minutes to seconds for repeat customers

    Search within history:
    -> Operator searches past submissions by:
        Reference number (exact match)
        Customer name (fuzzy match)
        Date range
        Amount range (for financial forms)
        Any field value (full-text search across field_data JSONB)
    -> Results sortable, paginated, exportable

    Keyboard-first:
    -> Ctrl+K or / opens search from anywhere in Form Desk
    -> Arrow keys navigate results, Enter selects
    -> Designed for operators who process 50+ forms/hour

Business value:
    - Speed: finding a form or submission takes < 3 seconds (vs. scrolling through lists)
    - Quick Fill: repeat customer + same form type = 80% of fields pre-filled automatically
    - Universal search: one box searches everything (no need to know where to look)
    - Keyboard shortcuts: maximizes throughput for high-volume operators
    - History search by field value: "find the cheque for 50,000 EGP last Tuesday" = instant
```

#### F-FEEDBACK: Template Feedback (from operators to designers)

```
User flow:
    Operator encounters an issue while filling a form:
    -> Clicks feedback icon on Form Filler toolbar
    -> Widget pre-populates: template name, version, current field
    -> Operator types description of issue ("This field should allow 15 digits now")
    -> Optionally attaches screenshot
    -> Submits -> notification sent to template designer

    Designer receives feedback:
    -> Opens template -> Feedback panel shows all submissions
    -> Sees: operator name, date, field reference, message, screenshot
    -> Can link feedback to specific canvas element
    -> Resolves with comment: "Fixed in v3.0 — updating national ID to 15 digits"
    -> Operator receives notification that feedback was addressed

Business value:
    - Closed feedback loop: operators inform designers about real-world issues
    - Tied to template versions: designers know exactly which version has the problem
    - Faster iteration: no need for separate ticketing system or email chains
    - Quality improvement: most-reported fields surface for priority fixes
    - Operator engagement: "my feedback matters" improves morale and adoption
```

---

### Stage 4: ANALYZE — Measure & Optimize

> **Business problem solved**: "We process 10,000 forms per month but have no visibility into which templates have issues, which operators need training, or how to improve efficiency."

#### F-ANALYTICS-TEMPLATE: Template Analytics

```
User flow:
    Admin opens /admin/analytics -> Template tab
    -> Sees:
        - Most-used templates (ranked by fill count)
        - Fill completion rate per template (started vs. printed)
        - Average fill time per template
        - Version adoption curve (how quickly operators move to new versions)
        - Stale templates (not used in 90+ days — candidate for archival)
    -> Drill down into specific template:
        - Fill count over time (trend line)
        - Fill time distribution (histogram)
        - Most common errors by field
        - Field-level empty rate, error rate, and average fill time
        - Feedback volume and resolution rate
        - Completion funnel: started -> saved draft -> printed/submitted
        - Department and branch usage breakdown
    -> Anomaly indicators highlight unusual spikes in errors, abandonment, or fill time

Business value:
    - Identify problematic templates: high error rate = bad design, needs iteration
    - Measure regulatory response time: how fast are new versions adopted?
    - Archive decisions: data-backed evidence for retiring unused templates
    - Design benchmarking: compare fill times to identify best-practice templates
    - Field-level analytics tells designers exactly which controls need improvement
```

#### F-ANALYTICS-OPERATOR: Operator Performance

```
User flow:
    Admin or Branch Manager opens /admin/analytics -> Operators tab
    -> Sees:
        - Forms processed per operator per day/week/month
        - Average fill time per operator (benchmarked against team average)
        - Error rate per operator (validations failed before successful submit)
        - Busiest hours and days (heatmap)
        - Operator comparison: side-by-side performance
    -> Drill down into specific operator:
        - Performance trend over time
        - Templates most frequently used
        - Error patterns (which fields cause most failures for this operator)
        - Training recommendations (based on error patterns)

Business value:
    - Identify training needs: operators with high error rates need coaching
    - Staffing optimization: know which hours need more coverage
    - Performance recognition: top operators identified for rewards/promotion
    - Onboarding tracking: new operator's error rate should decrease over time
    - Branch comparison: which branches are most efficient? Transfer best practices.
```

#### F-ANALYTICS-COMPLIANCE: Compliance Analytics

```
User flow:
    Admin opens /admin/analytics -> Compliance tab
    -> Sees:
        - Template quality scores across the organization
        - % of templates with full validator coverage
        - % of templates with bilingual labels
        - Quality score distribution and templates needing attention
        - Approval workflow adherence: how many templates bypass review?
        - Audit log volume by action type
        - Customer data access patterns (privacy monitoring)
        - Data retention status: what's approaching retention limit?
    -> Compliance alerts:
        - Templates missing required validators (flagged)
        - Templates not updated after regulatory change (stale)
        - Users with unusual access patterns (investigation prompt)

Business value:
    - Regulatory readiness: prove compliance posture to auditors at any time
    - Proactive risk: catch issues before external audit finds them
    - Data privacy: monitor who accesses customer data and how often
    - Continuous compliance: not a point-in-time check but ongoing monitoring
```

#### F-ANALYTICS-ORG: Organizational Analytics

```
User flow:
    Admin opens /admin/analytics -> Organization tab
    -> Sees:
        - Total forms processed this month/quarter/year
        - Forms by department and branch (comparison charts)
        - Growth trend: processing volume over time
        - Storage utilization (media, PDFs, backups)
        - Active users this month
        - Feature adoption: which capabilities are actually used
    -> Export:
        - Any chart as PNG image
        - Any dataset as CSV / Excel
        - Scheduled reports: weekly PDF summary emailed to stakeholders
        - Custom report builder: select metrics + filters + date range

Business value:
    - Executive reporting: clear metrics for leadership reviews
    - Capacity planning: growth trends inform infrastructure decisions
    - ROI measurement: forms processed per month vs. before FormCraft adoption
    - Department accountability: which departments are underutilizing the platform?
    - Budget justification: hard numbers for license renewals and expansion
```

#### F-REPORT: Scheduled Reports

```
User flow:
    Admin configures scheduled report:
    -> Select report type: template usage / operator performance / compliance / custom
    -> Set frequency: daily / weekly / monthly
    -> Set recipients: email addresses
    -> Set format: PDF summary / Excel with raw data / both
    -> System generates and emails report on schedule

    Custom report builder:
    -> Select metrics (forms processed, error rate, fill time, etc.)
    -> Apply filters (date range, department, branch, template)
    -> Choose visualization (table, chart, both)
    -> Preview -> save as scheduled or download one-time

Business value:
    - Hands-off monitoring: stakeholders get insights without logging in
    - Consistency: same report format every week enables trend comparison
    - Delegation: admin configures once, reports run forever
    - Audit evidence: scheduled compliance reports serve as documentation
```

#### F-REPORT-OPS: Operational Reports (business-level reporting on filled form data)

```
User flow:
    Admin or Branch Manager opens /admin/reports
    -> Sees pre-built report categories:

    Transaction Register:
    -> All form submissions in a date range
    -> Filter by: template, operator, branch, department, customer, status, amount range
    -> Columns: reference number, template, operator, customer, date, key fields (amount,
       beneficiary), status
    -> Use case: "Show me all cheques issued last month over 50,000 EGP"

    Daily Reconciliation:
    -> Per-operator or per-branch totals for a single day
    -> Shows: total submissions, total amount (for financial forms), breakdown by template
    -> Auto-generated at configurable time (e.g., 5:00 PM)
    -> Emailed to branch manager automatically
    -> Use case: end-of-day teller count — "Did my total match the system?"

    Period Summary:
    -> Aggregate for week / month / quarter / year
    -> Group by: department, branch, template, operator, cost center
    -> Metrics: count, total amount, average, min/max
    -> Period-over-period comparison with trend arrows
    -> Use case: "Monthly management report for the board"

    Beneficiary / Payee Report:
    -> All transactions for a specific beneficiary across all templates
    -> Filter by: date, template type, amount range
    -> Use case: "How much did we pay Supplier X this quarter?"
    -> Use case: "All cheques issued to employee Y in 2026"

    Void & Reprint Register:
    -> All voided, cancelled, or reprinted submissions
    -> Shows: original reference, void reason, who voided, who reprinted, when
    -> Flagged if same form voided and reprinted > 3 times
    -> Use case: fraud monitoring, operational audit

    Signatory Usage Report (cross-references Reference Data):
    -> Which authorized signatories were used on which transactions
    -> Filter by: signatory, amount range, date, template
    -> Alerts: signatory approaching their authority limit
    -> Use case: internal audit — "Did any branch use an unauthorized signatory?"

    Custom Report Builder:
    -> Select dimensions: any template field, submission metadata, customer data, ref data
    -> Apply filters: date, branch, department, operator, template
    -> Choose aggregation: count, sum, average, distinct
    -> Group by any dimension
    -> Choose visualization: table, bar chart, line chart, pie chart
    -> Save as named report -> schedule for recurring delivery
    -> Export: Excel, CSV, or PDF
    -> Scheduled delivery: approved email recipients

    Access control:
    -> Admin: all reports, all data
    -> Branch Manager: own branch data only
    -> Operator: "My Activity" report only

Business value:
    - Transforms FormCraft from a form tool into the system of record for document operations
    - Daily reconciliation: the single most requested feature in bank teller operations
    - Beneficiary reports: required for anti-money-laundering (AML) compliance
    - Void/reprint register: fraud detection without external tools
    - Signatory reports: authorization audit trail required by banking regulations
    - Custom reports: replaces shadow Excel spreadsheets that operators build manually
    - Scheduled delivery: stakeholders get insights without logging into FormCraft
    - Period comparison: enables data-driven operational improvement
    - Without reports, filled data is trapped — operators will export to Excel and build
      parallel systems, defeating the purpose of centralized form processing
```

---

### Stage 5: GOVERN — Control & Secure

> **Business problem solved**: "We need to know who did what, when, and ensure that only authorized people can access sensitive forms and data."

#### F-PLATFORM: Platform Admin Console

```
User flow:
    Platform Admin opens /platform (visible only when is_platform_admin=true)
    -> Dashboard shows platform-wide metrics:
        Total organizations
        Total users
        Total submissions
        Organizations by tier
        Submission volume trend
        Organizations approaching tier limits
    -> Opens /platform/organizations:
        Search, filter, and sort organizations by name, tier, status, country
        View active users, templates count, submissions this month, storage usage
    -> Creates new organization:
        Name, default language, country, currency, subscription tier
        First org admin invitation generated automatically
    -> Opens organization detail:
        Profile and branding
        Subscription settings
        Users overview
        Usage statistics
    -> Suspends or reactivates an organization when required
    -> Every platform admin action is audit logged

Business value:
    - Replaces direct database access for platform operations
    - Makes customer onboarding repeatable and supportable
    - Gives SaaS operators visibility into tenant health, usage, and tier limits
    - Separates platform-level control from organization admin routes
    - Supports emergency suspension/reactivation with traceability
```

#### F-ORG: Organization & Tenant Management

```
User flow:
    Org Admin configures the organization:
    -> Basic info: name (AR+EN), logo, primary color
    -> Defaults: language, country, currency
    -> Structure: departments and branches (hierarchical)
    -> Policies: draft expiry, data retention, approval workflow stages
    -> Custom domain: org-branded URL (forms.mybank.eg)
    -> Custom validators: org-specific field validation rules
    -> Subscription: tier, limits, add-ons

    Multi-tenancy:
    -> Each organization is completely isolated
    -> Users only see their organization's data
    -> RLS enforces isolation at database level
    -> Templates, submissions, customers, audit logs — all scoped to org

Business value:
    - SaaS deployment: one platform serves unlimited organizations
    - Data isolation: bank A cannot see bank B's data (regulatory requirement)
    - Self-service configuration: orgs manage themselves without platform admin
    - White-labeling: org sees their brand, not FormCraft's
    - Compliance: org-specific policies enforce local regulations
```

#### F-USERS: User & Access Management

```
User flow:
    Admin manages users:
    -> Invite new user: email + role + department + branch
    -> User receives branded invitation email
    -> User clicks link -> sets password -> account activated
    -> Admin can: change role, move department, deactivate, force logout

    Roles and permissions:
    -> Admin: full access to everything within the org
    -> Designer: create/edit templates, view feedback, submit for review
    -> Reviewer capability: branch managers and admins approve/reject submitted templates
    -> Operator: fill forms, manage drafts, view history, manage customers
    -> Viewer: read-only access to published templates and own submissions

    Enterprise authentication:
    -> SSO via SAML 2.0 (Active Directory, Okta, Azure AD)
    -> OIDC (Google Workspace, Microsoft Entra ID)
    -> MFA: TOTP (authenticator app) or SMS OTP
    -> Session management: configurable timeout, concurrent session limit
    -> IP whitelisting: restrict to corporate network

Business value:
    - Zero shared passwords: invitation-based onboarding
    - Role clarity: each person sees only what they need
    - Enterprise SSO: single sign-on with existing corporate identity
    - MFA: security requirement for banking and government
    - IP restriction: prevent unauthorized access from outside the office
    - Deactivation: employee leaves = instant access revocation
```

#### F-AUDIT: Audit Trail & Compliance

```
User flow:
    Every action in FormCraft creates an immutable audit record:
    -> Who (user ID, name, role, IP address)
    -> What (action type: created, updated, deleted, printed, accessed, approved, etc.)
    -> When (timestamp with timezone)
    -> Where (resource type, resource ID, branch)
    -> Details (before/after values for updates, full metadata)

    Admin views audit logs:
    -> Filter by: user, action type, resource, date range, branch
    -> Expand row -> full before/after JSON comparison
    -> Export as CSV for external compliance systems
    -> Scheduled audit reports emailed to compliance officers

    Logged events (comprehensive):
    | Category | Events |
    |----------|--------|
    | Auth | login, logout, failed_login, password_reset, mfa_verified |
    | Templates | created, updated, submitted, approved, rejected, published, archived, cloned |
    | Forms | filled, printed, reprinted, archived, exported |
    | Customers | created, viewed, updated, merged, deleted |
    | Users | invited, activated, deactivated, role_changed, department_changed |
    | System | settings_changed, webhook_configured, api_key_created, batch_started |

    Data retention:
    -> Audit logs: minimum 7 years (configurable, immutable — cannot be deleted)
    -> Form submissions: configurable retention + auto-archive
    -> Customer data: configurable retention + right-to-delete support
    -> Legal hold: flag specific records as "do not purge"

Business value:
    - Regulatory compliance: complete audit trail for banking regulators
    - Internal investigation: trace any action back to specific user and time
    - Accountability: "who approved this form?" answered in seconds
    - Data governance: retention policies ensure compliance with data laws
    - Dispute resolution: prove exactly what data was on a form when it was printed
```

#### F-NOTIFY: Notification System

```
User flow:
    Events trigger notifications to relevant users:
    -> Template submitted for review -> reviewer notified
    -> Template approved/rejected -> designer notified
    -> New template version published -> operators notified
    -> Batch job completed/failed -> initiator notified
    -> Draft expiring soon -> owner notified
    -> Feedback received on template -> designer notified
    -> Feedback resolved -> operator notified
    -> System announcement -> targeted users notified by role, department, or all users

    Delivery channels:
    -> In-app: bell icon with unread count, notification panel
    -> Email: bilingual HTML emails with org branding, retry on delivery failure
    -> Each user controls their preferences per notification type per channel
    -> Email unsubscribe disables that notification type for that user

    Notification center (/notifications):
    -> Full history of all notifications
    -> Mark as read, mark all as read
    -> Filter by type, read status, and date range
    -> Deep link: clicking notification navigates to relevant page
    -> Admin can publish system announcements for all users, roles, or departments

Business value:
    - No missed actions: reviewers don't forget to review, operators know about new versions
    - Reduces delays: approval workflows move faster with instant notifications
    - User control: each person sees notifications relevant to their role
    - Email fallback: critical notifications reach users even when not logged in
```

#### F-USER-FEEDBACK: Product Feedback & Support Loop

```
User flow:
    Authenticated user opens the persistent feedback widget from any page
    -> Types feedback text (required)
    -> Optionally attaches media:
        Up to five images with thumbnail previews
        One recorded or uploaded audio message
        Or one recorded/uploaded video message
    -> Submission captures user identity, page URL, timestamp, text, media, and status
    -> User receives confirmation and can later open /my-feedback

    Admin feedback dashboard:
    -> Admin views all feedback submissions with submitter, source page, text, media previews
    -> Search by text and filter by status, submitter, date range, and labels
    -> Create/manage labels and assign up to five labels per submission
    -> Reply in a threaded conversation with the submitting user
    -> User replies from /my-feedback; admin sees unread indicators
    -> In-app notifications connect users back to the relevant thread

Business value:
    - Captures product issues where they happen, with page context
    - Rich media makes bug reports and UX issues easier to understand
    - Labels and filters turn raw feedback into triageable support work
    - Threading closes the loop with the person who reported the issue
    - Builds a continuous improvement channel for the platform itself
```

---

### Stage 6: INTEGRATE — Connect & Extend

> **Business problem solved**: "FormCraft is one system in our organization. It needs to work with our core banking, CRM, document management, and reporting systems."

#### F-API: REST API & Programmatic Access

```
User flow:
    Admin creates an integration credential for their organization:
    -> Names and scopes the credential
    -> Grants only explicit capabilities
    -> Rate limits: per-key throttling
    -> Rotation and revocation controls
    -> Expiry: optional expiration date

    External systems use the API to:
    -> Submit forms programmatically: POST /api/desk/fill/:id with field_data
    -> Generate PDFs in bulk: POST /api/pdf/batch
    -> Query submission data: GET /api/desk/history with filters
    -> Manage templates: full CRUD on templates
    -> Lookup customers: GET /api/desk/customers/search

    OpenAPI specification published for integration partners.

Business value:
    - Core banking integration: bank system triggers form generation automatically
    - CRM sync: customer data flows between FormCraft and CRM
    - Automation: no manual intervention for routine form processing
    - Partner ecosystem: third-party developers build on FormCraft API
    - Procurement requirement: APIs are mandatory for enterprise software deals
    - Immediate revocation limits blast radius when credentials are compromised
```

#### F-WEBHOOK: Event Webhooks

```
User flow:
    Admin configures webhook endpoints:
    -> Select event: on_form_submitted, on_form_printed, on_template_published, on_batch_completed
    -> Enter endpoint URL
    -> Set custom headers (for authentication)
    -> Test: send sample event to verify endpoint responds
    -> Activate

    When event occurs:
    -> FormCraft POSTs event payload to configured URL
    -> Includes: event type, timestamp, resource data, org context
    -> Retry logic: 3 attempts with exponential backoff (1s, 5s, 30s)
    -> Delivery log: admin sees success/failure history per webhook

Business value:
    - Real-time integration: external systems react immediately to FormCraft events
    - DMS archival: PDF auto-archived to document management system on print
    - Workflow triggers: form submission triggers downstream approval in BPM system
    - Reporting: submission events feed into data warehouse for cross-system analytics
    - No polling: push-based integration is more efficient and timely
```

#### F-PORTAL: External Form Portal

```
User flow:
    Admin enables public access on a published template:
    -> Generates public URL: https://forms.org.eg/kyc-application
    -> Configures: require OTP? allow PDF download? send email confirmation? CAPTCHA?

    External user (citizen/customer) experience:
    -> Opens public URL in browser (no login required)
    -> (Optional) Verifies identity via OTP to phone number
    -> Form rendered in responsive Flow Layout (mobile-friendly)
    -> Arabic-first UI with language toggle
    -> All validation rules enforced (same as internal Form Desk)
    -> Submits form -> confirmation page with reference number
    -> (Optional) Downloads PDF copy of submitted form
    -> (Optional) Receives email confirmation with reference number

    Internal handling:
    -> Submission appears in admin dashboard with source: "portal"
    -> Admin reviews, prints, or processes further
    -> Status updates visible to external user via reference number lookup

Business value:
    - Citizen self-service: government forms fillable from home (no branch visit)
    - Pre-fill before visit: customer completes form online, comes to branch for signature only
    - Reduced branch load: routine form collection moves online
    - 24/7 availability: forms accessible outside business hours
    - Mobile-first: citizens use their phones to complete forms
    - Appointment reduction: "Please fill this form before your appointment" links in SMS
```

#### F-EXPORT: Data Export & Portability

```
User flow:
    Admin exports submission data:
    -> Filter: template, date range, department, branch, operator, status
    -> Format: CSV, Excel (.xlsx), JSON
    -> Column selection: choose which fields to include
    -> Export preview shows matching record count and field warnings
    -> Schedule: one-time download or recurring daily/weekly export
    -> Delivery: browser download or approved email recipients
    -> Export history records requester, filters, format, status, delivery summary

    Template export/import:
    -> Export template as .formcraft package (everything: pages, elements, rules, validators)
    -> Package also preserves conditional rules and reference binding metadata
    -> Import package into another org or environment (dev -> staging -> prod)
    -> If lineage/name matches existing template: import as a new version
    -> If no match exists: import as a new draft template
    -> Missing references produce remapping or warning summary before use
    -> Invalid/corrupted/unsupported packages are rejected with no partial template created
    -> Use case: managed deployments across environments
    -> Use case: franchise organizations sharing form standards

Business value:
    - Reporting: feed form data into Excel, Power BI, or data warehouse
    - Regulatory filings: export specific submissions for regulatory reports
    - Backup: regular data exports as organizational safety net
    - Environment management: promote templates through dev/staging/prod lifecycle
    - Data ownership: organization owns their data, can extract it at any time
    - No vendor lock-in: complete data portability reduces procurement risk
```

#### F-MARKETPLACE: Template Marketplace

```
User flow:
    Publisher (org admin):
    -> Marks a published template as "Marketplace Available"
    -> Adds: description, preview images, compliance certifications, pricing (free/premium)
    -> Template listed in marketplace after FormCraft review

    Consumer (org admin):
    -> Browses marketplace by: country, category, compliance standard, price
    -> Previews: read-only canvas view + sample PDF output
    -> "Use Template" -> clones into own org as new draft
    -> Customizes cloned template for own needs
    -> Full independence: changes to original don't affect consumer's copy

Business value:
    - Best practices: proven templates shared across the industry
    - Compliance shortcuts: "CBE-compliant KYC form" ready to use
    - Revenue for publishers: monetize form design expertise
    - Faster adoption: new org starts with working templates, not blank canvas
    - Industry standardization: consistent form quality across organizations
    - Network effects: more templates attract more users attract more templates
```

---

## Complete User Journeys (End-to-End Closed Cycles)

### Journey 1: New Organization Onboarding

```
Day 1:
    -> Org Admin creates organization (name, logo, locale, structure)
    -> Admin invites Designer team (email invitations)
    -> Admin invites Operators (by department/branch)
    -> Users accept invitations, set passwords

Day 2-5:
    -> Designers upload existing paper forms (batch OCR import)
    -> OCR processes all forms -> review dashboard shows results
    -> Designers accept high-confidence detections, manually fix low-confidence ones
    -> Result: 80% of form library digitized automatically

Day 5-10:
    -> Designers refine templates: add conditional logic, validation, tafqeet
    -> AI suggests missing validators, quality scores improve
    -> Designers submit templates for review
    -> Reviewers approve -> Admin publishes

Day 10+:
    -> Operators begin daily operations on Form Desk
    -> Customer profiles build up automatically
    -> Feedback flows from operators to designers (continuous improvement)
    -> Analytics show adoption metrics to leadership

Result: Organization fully operational in 2 weeks.
```

### Journey 2: Regulatory Form Update

```
Trigger: Central Bank issues new regulation requiring additional field on KYC form

    -> Admin receives notification of regulatory change (external to FormCraft)
    -> Admin flags existing KYC template for update

    -> Designer clones current published version (v2.0) into new draft
    -> Designer adds required new field with appropriate validator
    -> AI confirms validator matches new regulation requirements
    -> Designer submits for review

    -> Reviewer verifies: new field present, validator correct, no existing fields broken
    -> Reviewer approves

    -> Admin publishes -> becomes v3.0
    -> v2.0 automatically marked as deprecated
    -> All operators see notification: "KYC Form updated to v3.0"
    -> Operators see new field on next form fill (no training needed — help text explains)
    -> In-progress drafts using v2.0 show migration prompt

    -> Admin runs version diff report for audit evidence
    -> Compliance team verifies: new version live before regulatory deadline

Time: 1-3 days from regulation to live form (vs. weeks with manual process)
```

### Journey 3: Daily Bank Teller Operations

```
Morning (8:00 AM):
    -> Operator logs in -> Form Desk dashboard
    -> Sees pinned forms: Cheque, Transfer, KYC (the forms used daily)
    -> Sees 1 saved draft from yesterday (customer coming back today)
    -> Loads pre-printed cheque stationery into printer tray

Throughout the day:
    -> Customer arrives for cheque issuance
    -> Operator clicks "Cheque" from pinned forms
    -> Types customer name -> profile auto-fills (name, ID, account number)
    -> Selects beneficiary from Reference Data list -> name, bank, IBAN auto-fill
    -> Operator enters: amount, date
    -> Tafqeet auto-computes: "خمسة آلاف جنيه مصري لا غير"
    -> Selects authorized signatory from Reference Data list -> name, title, signature auto-fill
    -> Validation confirms: IBAN valid, amount within signatory's authority limit
    -> Operator clicks "Print & Next"
    -> System uses Overlay Print mode: only filled data prints onto pre-printed cheque
    -> Printer profile "Teller Window 3" applies +1.5mm X offset automatically
    -> Cheque comes out with data perfectly aligned on pre-printed security paper
    -> Form resets for next customer -> total time: 45 seconds

    Between customers:
    -> Notices template feedback was resolved: "Fixed in v3.0"
    -> Clicks notification -> sees the improvement

End of day (4:00 PM):
    -> Operator has processed 60 cheques
    -> Daily Reconciliation report auto-generates at 5:00 PM:
        - 60 cheques issued, total amount: 1,250,000 EGP
        - Breakdown by signatory: Branch Manager signed 12, Deputy signed 48
        - 0 voids, 1 reprint (reason: paper jam)
    -> Report emailed to branch manager automatically
    -> Branch manager also views real-time analytics: 60 forms, 0 errors, avg 48 seconds
    -> All submissions searchable in history with reference numbers

End of month:
    -> Admin generates Period Summary: total cheques by branch, by beneficiary
    -> Signatory Usage Report: each signatory's total authorized amount vs. limit
    -> Beneficiary Report: top 20 payees by total amount (AML compliance check)
    -> All reports exported as Excel for compliance team and central bank audit
```

### Journey 4: Batch Certificate Issuance

```
Trigger: Monthly training certificate generation for 300 employees

    -> HR Admin opens /desk/queue -> "New Batch Job"
    -> Selects "Training Certificate" template
    -> Uploads Excel: employee name, ID, training program, completion date, score
    -> Column mapper auto-maps all columns (headers match field labels)
    -> Validation preview: 298 valid, 2 invalid (missing completion date)
    -> Admin fixes 2 rows inline, re-validates -> all 300 valid
    -> Clicks "Generate All"
    -> Progress: "Generated 300/300 PDFs — 2 minutes"
    -> Downloads ZIP with 300 individual certificates
    -> Sends ZIP to printing department

    Each certificate:
    -> Personalized with employee data
    -> Tafqeet renders score in words
    -> QR code contains verification URL
    -> Organization logo in header
    -> Bilingual (Arabic primary, English secondary)

Alternative: Scheduled batch
    -> Admin configures: run monthly on 1st, pull data from HR API
    -> System auto-generates and emails ZIP to HR admin
    -> No manual intervention after initial setup
```

### Journey 5: External Citizen Form Submission

```
Government agency publishes "Building Permit Application" form on portal:

    Citizen experience:
    -> Receives SMS: "Apply for building permit online: forms.gov.eg/building-permit"
    -> Opens link on mobile phone
    -> Enters phone number -> receives OTP -> verifies identity
    -> Form loads in mobile-friendly Flow Layout
    -> Fills: property details, owner info, dimensions, purpose
    -> Attaches: property deed photo (camera capture)
    -> Validation catches: "National ID must be 14 digits" -> fixes
    -> Submits -> confirmation page: "Ref: GOV-2026-0847"
    -> Downloads PDF copy for records
    -> Receives SMS confirmation

    Government side:
    -> Submission appears in admin dashboard (source: portal)
    -> Reviewer opens submission, verifies attached documents
    -> Processes application through internal workflow
    -> Status updates visible to citizen via reference number lookup:
        "GOV-2026-0847: Under review" -> "Approved" -> "Certificate ready for pickup"

Business value for government:
    - 24/7 availability: citizens apply from home at any time
    - Reduced queues: fewer branch visits for routine applications
    - Data quality: validation ensures correct format on submission (no back-and-forth)
    - Accessibility: mobile-first design reaches all citizens
    - Paper reduction: government digitization mandate fulfilled
```

---

## Closed Cycle Summary

Every function feeds back into the system, creating a self-improving loop:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│  ONBOARD ──────> DESIGN ──────> OPERATE ──────> ANALYZE ──────> IMPROVE         │
│     │               │               │               │               │           │
│     │               │               │               │               │           │
│     │               │               │               v               │           │
│     │               │               │         "KYC form has          │           │
│     │               │               │          30% error rate        │           │
│     │               │               │          on IBAN field"        │           │
│     │               │               │               │               │           │
│     │               │               │               v               │           │
│     │               │               │      FEEDBACK from operators:  │           │
│     │               │               │      "IBAN field too small,    │           │
│     │               │               │       can't see full number"   │           │
│     │               │               │               │               │           │
│     │               v               │               v               │           │
│     │          Designer fixes:      │         Analytics confirm:     │           │
│     │          wider IBAN field,    <─────── error rate drops to 5%  │           │
│     │          bigger font,         │         after v3.0 published   │           │
│     │          publishes v3.0       │                                │           │
│     │               │               │                                │           │
│     │               v               │                                │           │
│     │         Operators auto-see    │                                │           │
│     │         new version next      │                                │           │
│     │         form fill             │                                │           │
│     │                               │                                │           │
│     │                               │                                │           │
│     v                               v                                v           │
│  New forms scanned ─> new templates created ─> more data ─> better insights     │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**No dead ends. Every output becomes an input. The platform gets better with use.**

| From | To | How |
|------|-----|-----|
| Analytics | Design | Error rate data tells designers which fields to fix |
| Operator Feedback | Design | Real-world issues surface design problems |
| Form Desk | Analytics | Every submission feeds usage metrics |
| Form Desk | Operational Reports | Every submission feeds transaction registers and reconciliation |
| Form Desk | Customer Profiles | New customers auto-created from submissions |
| Customer Profiles | Form Desk | Profiles speed up future form filling |
| Reference Data | Form Desk | Signatories, beneficiaries, cost centers auto-fill from governed lists |
| Reference Data | Operational Reports | Signatory usage report cross-references list selections |
| Operational Reports | Governance | Daily reconciliation and AML reports satisfy compliance |
| Template Governance | Design | Review comments, compliance scores, and stale flags drive template remediation |
| Platform Admin Console | Organization Management | Tenant usage, tier limits, and status controls feed SaaS operations |
| Product Feedback | Support Loop | User reports, media, labels, and replies feed platform improvement |
| Template Versioning | Form Desk | New versions automatically available to operators |
| OCR Import | Design Studio | Scanned forms become editable templates |
| Overlay Print | Form Desk | Pre-printed stationery + data-only output = complete cheque |
| Printer Calibration | Overlay Print | Per-printer offsets ensure mm-accurate alignment |
| Batch Queue | Analytics | Volume data informs capacity planning |
| External Portal | Admin Console | Portal submissions appear in admin dashboard |
| Webhooks | External Systems | FormCraft events trigger downstream processes |
| External Systems | API | External data feeds form generation |
| Marketplace | Design Studio | Shared templates reduce design effort for new orgs |
| Audit Trail | Compliance | Complete history satisfies regulatory audits |

---

## Business Value Summary by Stakeholder

### For the Operator (daily user)

| Value | Before FormCraft | After FormCraft |
|-------|-----------------|-----------------|
| Find a form | Search filing cabinets | 2 clicks from pinned favorites |
| Fill a form | Handwrite or slow desktop app | Keyboard-optimized with auto-populate |
| Validate data | Hope it's correct; errors caught later | Real-time validation prevents errors at source |
| Customer handling | Re-enter data every visit | Auto-populate from customer profile |
| Select signatory/beneficiary | Type manually (error-prone) | Pick from governed Reference Data list (instant auto-fill) |
| Handle errors | Form rejected, start over | Instant feedback, fix in place |
| Tafqeet | Manual lookup or calculation | Automatic, instant, always correct |
| Print cheque | Print full form on plain paper (or misalign on cheque book) | Overlay Print: data-only on pre-printed stationery, calibrated per printer |
| Reprint | Call central office, wait 2 days | Self-service, 10 seconds |
| Track submissions | Paper logbook | Searchable digital history |
| End-of-day reconciliation | Manual count from paper logbook | Auto-generated daily report emailed at 5 PM |

### For the Designer (template author)

| Value | Before FormCraft | After FormCraft |
|-------|-----------------|-----------------|
| Create a form | Adobe InDesign + developer | Self-service canvas editor |
| Arabic support | Manual font embedding, testing | Automatic: reshaping, bidi, font embedding |
| Validation rules | Written in spec document, never enforced | Configured once, enforced everywhere |
| Regulatory update | Weeks of redesign + testing | Clone, modify, review, publish in days |
| Know if forms work | No visibility | Analytics + operator feedback |
| AI assistance | None | Suggestions for types, validation, quality scoring |
| Import existing forms | Manual recreation | OCR scan -> auto-detect -> refine |

### For the Admin (governance)

| Value | Before FormCraft | After FormCraft |
|-------|-----------------|-----------------|
| Audit trail | Incomplete, manual records | Every action logged immutably |
| Compliance proof | Scramble before audit | Real-time compliance dashboard |
| Template governance | Manual review lists and ad hoc comments | Central governance dashboard with canvas-pinned review comments |
| User management | Spreadsheet of who has access | Role-based, department-scoped, SSO |
| Performance visibility | None | Per-operator, per-branch, per-template analytics |
| Form version control | Which version is "the latest"? | Clear versioning with deprecation |
| Data security | Trust-based | RLS + encryption + access logging |
| Multi-branch oversight | Call each branch | Centralized dashboard, branch comparison |

### For the Platform Admin (SaaS operator)

| Value | Before FormCraft | After FormCraft |
|-------|-----------------|-----------------|
| Tenant onboarding | Direct database/API work | Create organization from `/platform` with first admin invite |
| Tenant monitoring | Scattered support checks | Platform dashboard with org, user, submission, and tier-limit metrics |
| Emergency control | Manual intervention | Suspend/reactivate organization with audit trail |
| Support context | Ask customer for screenshots | Organization detail view with profile, users, subscription, and stats |

### For the Organization (strategic)

| Value | Metric |
|-------|--------|
| Onboarding speed | 2 weeks vs. 6 months to digitize form library |
| Operator efficiency | 10x faster form processing vs. manual |
| Error reduction | 90% reduction in form errors with validation |
| Regulatory response | Days vs. weeks for form updates |
| Customer satisfaction | Faster service, fewer re-visits |
| Cost reduction | Eliminate per-form printing costs; reduce manual data entry staffing |
| Stationery savings | Overlay Print = accurate first print, no wasted pre-printed forms |
| Revenue enablement | Process more customers per day per branch |
| Compliance | Always audit-ready with operational reports + signatory trail |
| AML / Fraud monitoring | Beneficiary reports, void/reprint register, signatory usage — built in |
| Digital transformation | Measurable progress toward paperless operations |
| Management visibility | Daily reconciliation and period reports replace manual spreadsheets |
