# FormCraft — Critical Analysis & Strategic Vision

> Complete system analysis, business value assessment, and full-platform vision.
> Date: 2026-05-15 | Last updated: 2026-06-19

---

## Table of Contents

1. [What FormCraft Is](#what-formcraft-is)
2. [Documentation Quality Assessment](#what-the-documentation-does-well)
3. [Critical Issues](#critical-issues)
4. [The Value Proposition](#the-value-proposition-formcraft-should-own)
5. [Architectural Reframe: Four Product Modes](#architectural-reframe-two-product-modes)
6. [Full Feature Inventory](#full-feature-inventory)
7. [Complete Data Model](#complete-data-model)
8. [Complete API Surface](#complete-api-surface)
9. [Cross-Cutting Platform Capabilities](#cross-cutting-platform-capabilities)
10. [Revenue Model](#revenue-model)
11. [Phased Roadmap](#phased-roadmap)
12. [Implementation Status vs. Vision](#implementation-status-vs-vision-as-of-2026-05-24)
13. [Final Architecture Diagram](#final-architecture-diagram)

---

## What FormCraft Is

FormCraft is an **enterprise Arabic-first form designer and print studio** targeting banks and government entities in Egypt, Saudi Arabia, and the UAE. It lets organizations design pixel-perfect printable forms (cheques, applications, certificates) via a browser-based canvas editor (Konva.js), export them as PDF with exact mm positioning, and includes AI-powered field recognition, country-specific validators, and a feedback loop for end-users.

**Architecture**: Angular 19 frontend + FastAPI backend + Supabase (PostgreSQL, Auth, Storage) + AWS Bedrock (AI) + Azure Document Intelligence (OCR) + WeasyPrint (PDF). Hosted on Bunny Magic Containers.

**Current scope**: 58 feature spec directories (001–058) spanning the full platform lifecycle. Of the original 26 features (001–026), 22 are fully working, 1 partial (F09 — performance caching), and 2 awaiting external credentials (F05 — AWS Bedrock AI, F26 — Azure OCR). Specs 027–058 cover: analytics-reporting, approval-workflow, notification-center, customer-profiles, template-governance, data-export-integration, operational-reports, external-form-portal, template-marketplace, batch-operations, desk-search-quickfill, template-creation-wizard, platform-admin-console, enhanced-analytics, UI-redesign-prototype (041), enterprise-SSO-MFA (042), granular-template-permissions (043), data-retention-archival (044), batch-OCR-onboarding (045), digital-signatures (046), mobile-offline-desk (047), custom-locale-validators (048), connector-framework (049), new-theme-desk-data (050), responsive-themes-mobile (051), cross-theme form filler (052–053), analytics-real-data (054), spark3-missing-pages (055), spark-add-customer (056), overlay-control-font-insets (057), and paygateway-billing (058). Specs 041/050/052–053 have frontend code in production (new theme routes live); 058 is in draft/spec phase.

---

## What the Documentation Does Well

The documentation is unusually thorough for a project at this stage:

- 26 feature specs with Mermaid wireflows, sequence diagrams, and state diagrams
- Clear dependency graph (`F01 Auth` as root, branching into design, operations, and feedback subtrees)
- Role-access matrix covering all 26 features across 5 role levels
- API surface summary with auth and role gates (40+ verified endpoints)
- Simplified ERD showing full data model relationships across 28 migrations
- Cross-cutting concerns (RTL, error handling, session lifecycle) documented separately
- Per-feature edge cases and constraints tables
- Speckit-driven feature specs with plan.md, tasks.md, data-model.md, contracts/, and research.md per feature

The separation between `feature-map.md` (system view), `user-flows.md` (cross-cutting), and individual feature docs in `formcraft-specs/specs/NNN-feature-name/` is clean and navigable.

---

## Critical Issues

### 1. ~~Identity Crisis: Form Designer vs. Feedback Platform~~ ✅ RESOLVED

**Severity: Strategic** → **Status: RESOLVED (F20 Template Feedback)**

Features F11-F14 (Feedback Widget, Labels, Rich Media, Threading) have been reframed as **Template Feedback** (F20). Feedback is now tied to specific template versions so designers iterate based on operator input. The `/api/admin/template-feedback` endpoint provides cross-template feedback oversight. The generic feedback subsystem remains as infrastructure but the product positioning is now coherent — feedback serves the core design-to-desk loop.

**Original risks (now mitigated)**:

| Dimension | Original Impact | Current Status |
|-----------|--------|--------|
| Focus dilution | ~30% of spec effort on non-core | Feedback now serves template quality iteration |
| Value proposition | Confused enterprise buyers | Template Feedback is a natural fit for enterprise form governance |
| Admin surface | Parallel admin dashboard | Unified under `/admin/template-feedback` |

### 2. ~~One-Way Template Lifecycle is a Business Limiter~~ ✅ RESOLVED

**Severity: High** → **Status: RESOLVED (F19 Template Versioning)**

Templates now support full versioning and cloning via F19. Key capabilities implemented:
- **Clone any template** (`POST /templates/:id/clone` — 201 verified) into a new draft
- **Version tracking** (`POST /templates/:id/version` — 200 verified) with `lineage_id` tracing template lineage
- **lineage_id** is NOT NULL on all templates (migration 020), ensuring every template traces its origin
- Templates can be cloned, versioned, and iterated without starting from scratch

**Remaining gap**: The full approval workflow (submit → review → approve → publish) is specified in the vision (DS-08, AC-03) but not yet implemented as a separate feature. Currently templates go draft → published directly.

### 3. ~~No Data Collection / Form Filling Runtime~~ ✅ RESOLVED

**Severity: Critical** → **Status: RESOLVED (F15-F18)**

The design-to-desk gap has been closed with four features:
- **F15 Mode Switching**: Top-level nav between Design Studio, Form Desk, and Admin (`/users/me` returns role, language, org context — 200 verified)
- **F16 Operator Dashboard** (`/desk/dashboard` — 200 verified): Template list with pins, quick actions, recently used forms
- **F17 Form Filler** (`/desk/fill/:id` — 200 verified): Published template structure returned for filling with field data
- **F18 Submission History** (`/submissions` — 200 verified): Operators can view past submissions

The core business loop now works: designer creates template → publishes → operator fills in Form Desk → validates → prints/submits → finds in history.

**Remaining gaps**: Batch processing (FD-06), customer profiles (FD-08), and external form portal (EXT-01) are not yet implemented — these are Phase 2/3 vision items.

### 4. ~~Single-Tenant, No Organization Boundary~~ ✅ RESOLVED

**Severity: High** → **Status: RESOLVED (F25 Multi-Tenancy)**

Full multi-tenancy is implemented via F25 (migration 027):
- **Organizations** table with settings, branding, custom domain (`/organizations` — 403 for non-platform-admins, by design)
- **Departments** (`/departments` — 200 verified) and **Branches** (`/branches` — 200 verified) hierarchy
- **User management** (`/users` — 200 verified) with org/department/branch assignment
- **Invitations** (`/invitations` — 200 verified) for onboarding new users
- **Org settings** (`/org-settings` — 200 verified) for per-org configuration
- **RLS policies** on all tables enforce org-level isolation via `current_setting('app.current_org_id', true)::UUID` — 10 policies fixed across migrations 025-027
- **Auth branding** (`/auth/branding/:domain`) supports custom domain login pages

Bank A's admins cannot see Bank B's data. Department and branch scoping is in place.

### 5. ~~OCR Import is Powerful but Under-Leveraged~~ ✅ PARTIALLY RESOLVED

**Severity: Opportunity cost** → **Status: PARTIALLY RESOLVED (F26 Form Import & OCR Detection)**

F26 significantly elevates OCR from a toolbar button to a first-class feature:
- **Backend**: OCR client, BoundingBoxConverter (DPI + page-aware), FieldClassifier (Arabic/Hijri support), forms API routes (import, list, accept, delete), audit logging, 30s timeout, IoU deduplication, boundary clipping
- **Frontend**: Import panel in Design Studio, detection review panel (accept/reject/clear/history), debug grid overlay (Ctrl+G), replace confirmation dialog, full i18n (EN+AR)
- **Tests**: 76/76 passing (21 converter, 45 classifier incl. 19 Arabic-specific, 10 route integration)
- **API routes**: `/forms/import/:id`, `/forms/:id/detections`, `/forms/:id/detections/:did/accept`, `/forms/detections/:did` (DELETE)

**Awaiting**: Azure Document Intelligence credentials for live OCR testing.

**Still missing (Phase 3 vision items)**:
- Batch onboarding wizard for importing a library of forms
- Comparing OCR results against previous imports
- Progressive refinement workflow

### 6. Missing Operational Features for Enterprise (Updated Status)

| Capability | Status | Notes |
|------------|:------:|-------|
| ~~Conditional fields / logic~~ | ✅ DONE | F22: `visible_when`, `required_when`, `computed_value` columns on elements |
| ~~Template versioning & cloning~~ | ✅ DONE | F19: Clone + version endpoints working |
| ~~Multi-tenancy / org boundaries~~ | ✅ DONE | F25: Orgs, departments, branches, RLS isolation |
| ~~Template feedback loop~~ | ✅ DONE | F20: Template-specific feedback with admin dashboard |
| ~~Signature & table elements~~ | ✅ DONE | F21: Signature and table element types added |
| ~~Overlay print mode~~ | ✅ DONE | F23: Full/overlay/both toggle, printer profiles, calibration |
| ~~Reference data / lookups~~ | ✅ DONE | F24: Reference lists with schema, entries, org-scoped |
| ~~Notifications~~ | ✅ DONE | F14: Notification endpoint working (`/notifications` — 200) |
| ~~White-labeling~~ | ✅ PARTIAL | F25: Custom domain + branding endpoint exists |
| **Platform Admin Dashboard** | ✅ DONE | PC-01: backend (5 endpoints, `require_platform_admin()`) + frontend now built — `features/platform` module, `PlatformAdminGuard`, org list/create/detail + tabs, routed at `admin/platform`. **Remaining gap: tiers are display/alert-only, not enforced** (see Revenue Model) |
| Approval workflows | ❌ TODO | Template review/approve/reject not yet implemented |
| Template permissions | ⚠️ SPECIFIED | Spec 043: per-role/dept/branch grants + explicit deny, access diagnostics |
| Digital signatures | ⚠️ SPECIFIED | Spec 046: ordered/parallel multi-signer, OTP for external, SHA-256 evidence |
| Print queue / batch print | ⚠️ SPECIFIED | Spec 036-batch-operations |
| Template import/export | ❌ TODO | .formcraft package format not yet implemented |
| Customer data management | ⚠️ SPECIFIED | Spec 030-customer-profiles |
| Data export | ⚠️ SPECIFIED | Spec 032-data-export-integration |
| Mobile support | ⚠️ SPECIFIED | Spec 047: 360px phone + tablet, IndexedDB offline, sync queue, WebCrypto |
| SSO / enterprise auth | ⚠️ SPECIFIED | Spec 042: SAML/OIDC, TOTP, SMS OTP, domain routing, 8h session default |
| Data retention policies | ⚠️ SPECIFIED | Spec 044: configurable periods, legal holds, SHA-256 purge, privacy requests |
| Custom locale validators | ⚠️ SPECIFIED | Spec 048: org-scoped regex, bilingual errors, 500/org, 10/field limits |
| Connector framework | ⚠️ SPECIFIED | Spec 049: DMS/CRM/email/banking connectors, delivery logs, retry backoff |
| Dual-theme UI shell | ✅ PARTIAL | Specs 041/050/052–053: new-theme routes live, real API data, cross-theme filler |

---

## The Value Proposition FormCraft Should Own

> **"The only Arabic-first form platform that lets you scan existing paper forms, digitize them with AI, design pixel-perfect templates, fill them on screen with live validation, and print — from design to desk in one platform."**

Right now, FormCraft delivers the middle of that sentence (design + PDF export) but not the beginning (OCR onboarding as hero flow) or the end (fill and print as daily operation).

Closing both ends transforms FormCraft from a **design tool** into an **operational platform** — which is where recurring revenue and enterprise stickiness live.

---

## Architectural Reframe: Four Product Modes

### The Core Insight

FormCraft should not treat form filling as a feature bolted onto the design studio. It should be structured as **four parallel product modes** — each with its own UX, dashboard, persona, and usage pattern. Three modes (Studio, Desk, Admin) are used by different people every day. The fourth (Platform) is used rarely by super-admins for cross-org management.

### Why Modes, Not Features

| Dimension | "Feature" Framing (weaker) | "Product Mode" Framing (stronger) |
|---|---|---|
| UX architecture | One app with an extra screen | Two purpose-built workspaces with shared data |
| Navigation | Sidebar link to /forms | Top-level mode switcher or separate entry points |
| Dashboard | Template list with a "fill" button | Dedicated operator dashboard: queue, drafts, recent, search |
| Persona clarity | "Users can also fill forms" | "Designers design. Operators operate. Different tools for each." |
| Revenue model | License the whole app | License Studio for design teams + license Desk per operator seat |
| Usage ratio | Design is primary, fill is secondary | Design is occasional, Desk is daily — Desk drives volume |

### Mode 1: Design Studio (exists today)

The creative workspace for template authors.

```
Who:        Designers, Admins
When:       Occasional — when creating or updating form templates
Entry:      /studio or /designer/:pageId
Core loop:  Create template -> design on canvas -> AI assist -> preview PDF -> submit for approval -> publish
```

### Mode 2: Form Desk (new)

The operational workspace for daily form processing.

```
Who:        Operators, Viewers, Branch staff, Service agents
When:       All day, every day — the primary daily-use mode
Entry:      /desk
Core loop:  Select form -> fill fields -> validate -> preview -> print -> archive
```

### Mode 3: Admin Console (enhanced from current)

The governance and oversight workspace.

```
Who:        Admins, Org owners, Compliance officers
When:       Periodic — governance, reporting, configuration
Entry:      /admin
Core loop:  Manage users -> review templates -> approve workflows -> monitor operations -> audit -> report
```

### Mode 4: Platform Console (new — backend exists, no frontend)

The super-admin workspace for multi-org platform management.

```
Who:        Platform Admins (is_platform_admin=true on profile — NOT a role, a flag)
When:       Rare — when onboarding new orgs, managing subscriptions, platform-wide oversight
Entry:      /platform
Core loop:  Create org -> configure tier -> monitor orgs -> manage platform users -> system health
```

**Key distinction**: Platform Admin is a flag (`is_platform_admin`) on the `profiles` table, independent of the `role` column. A user can be both `role: 'admin'` for their org AND `is_platform_admin: true` for cross-org management. The backend endpoints exist (`POST /api/organizations`, `GET /api/organizations`, etc.) protected by `require_platform_admin()`, but no frontend UI has been built.

### Mode Switching UX

```
┌──────────────────────────────────────────────────────────────────────────────┐
│  FormCraft   [Design Studio]  [Form Desk]  [Admin]  [Platform]   🔔 🌐 👤   │
│              ─────────────    ──────────   ─────   ──────────              │
│                                (active)                                     │
├──────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Current mode content here                                                   │
│                                                                              │
└──────────────────────────────────────────────────────────────────────────────┘
```

Note: [Platform] tab is ONLY visible when `is_platform_admin=true`. Most users never see it.

- Top-level tabs in the main nav bar
- Mode persists across sessions (stored in user profile preference)
- Default mode based on role:
    - Platform Admin -> default to Platform Console
    - Admin -> default to Admin Console
    - Designer -> default to Design Studio
    - Operator, Viewer -> default to Form Desk
    - Users can switch freely if their role permits
- Role gates enforce access: Operators cannot reach Design Studio routes
- Platform Console requires `is_platform_admin=true` (not a role — a profile flag)
- URL structure: `/studio/*` for design, `/desk/*` for operations, `/admin/*` for governance, `/platform/*` for platform management

---

## Full Feature Inventory

Below is every feature the platform needs for full business value, organized by product mode and phase.

### Design Studio Features

#### DS-01: Template Library (`/studio/templates`) — ✅ EXISTS (F03)

```
Designer opens template library
    -> Grid/list view of all templates accessible to this user
    -> Filter by: status (draft/published/archived), category, language, country, version
    -> Search by: name, description, tags
    -> Sort by: name, created date, last modified, version number
    -> Actions per template: Edit (draft), Clone, View History, Archive, Delete (draft only)
    -> "New Template" button -> creation wizard
    -> "Import from Scan" button -> OCR onboarding pipeline (see DS-09)
```

#### DS-02: Template Creation Wizard (enhanced)

```
Designer clicks "New Template"
    -> Step 1: Basic info — name, description, category, tags
    -> Step 2: Locale — language (AR/EN/Both), country (EG/SA/AE), currency
    -> Step 3: Page setup — size (A4/A3/Letter/Legal/Custom mm), orientation, margins
    -> Step 4: Starting point:
        Option A: Blank canvas
        Option B: Clone from existing template
        Option C: Import from scanned form (OCR)
        Option D: Import from template package (.formcraft export)
    -> System creates template in "draft" status
    -> Designer redirected to Design Studio canvas
```

#### DS-03: Canvas Editor (`/studio/designer/:pageId`) — ✅ EXISTS (F04, enhanced with F21, F22)

```
Full canvas editor with Konva.js — all existing functionality plus:

Element palette (expanded):
    Text, Number, Date, Currency, Checkbox, Radio, Dropdown, Image,
    QR, Barcode, Tafqeet, Signature (NEW), Table (NEW),
    Section Header (NEW), Divider Line (NEW), Stamp (NEW)

Properties panel (enhanced):
    All existing properties plus:
    - Conditional visibility rules (visible_when)
    - Conditional requirement rules (required_when)
    - Computed value formulas (computed_value)
    - Field grouping / section assignment
    - Tab order (for Form Desk keyboard navigation)
    - Tooltip / help text (shown to operators during filling)
    - Default value (pre-filled when operator opens form)
    - Read-only toggle (visible but not editable in Form Desk)
    - Placeholder text (shown when field is empty)

Canvas enhancements:
    - Alignment guides (snap to other elements, not just grid)
    - Smart distribute (equal spacing between selected elements)
    - Group/ungroup elements
    - Copy formatting (paint roller)
    - Element search (find element by key or label)
    - Zoom to fit page
    - Ruler with mm markings along top and left edges
```

#### DS-04: AI Smart Suggestion — ✅ EXISTS (F05, awaiting AWS Bedrock credentials)

```
All existing AI suggestion functionality plus:

Batch field analysis:
    -> Designer clicks "Analyze All Fields"
    -> AI reviews all elements on the page simultaneously
    -> Returns cross-field suggestions:
        - "These 3 fields look like an address group — add a section header?"
        - "This currency field has no linked tafqeet — add one?"
        - "National ID field detected but no IBAN — typical KYC forms include both"
    -> Designer accepts/dismisses each suggestion

Template quality score:
    -> AI evaluates template completeness:
        - % of fields with validators
        - % of fields with bilingual labels
        - % of required fields with help text
        - Accessibility score (tab order defined, field groupings logical)
    -> Score shown as badge on template card in library
    -> Suggestions for improvement shown inline
```

#### DS-05: Tafqeet — ✅ EXISTS (F10)

All existing tafqeet functionality. No changes needed.

#### DS-06: PDF Engine — ✅ EXISTS (F06)

```
All existing PDF rendering functionality plus:

Watermark support:
    -> Draft templates render with "DRAFT" watermark
    -> Configurable watermark text, position, opacity per template

Header/footer engine:
    -> Page number: "Page X of Y"
    -> Date printed
    -> Template name and version
    -> Organization logo (from org settings)
    -> Custom text

Conditional element rendering:
    -> Elements with visible_when rules evaluated against provided data
    -> Hidden elements do not occupy space in PDF output

Batch rendering:
    -> POST /api/pdf/batch with { template_id, records: [{field_data}, ...] }
    -> Returns ZIP of individual PDFs or single merged PDF
    -> Background job with progress tracking
```

#### DS-07: Validation Library — ✅ EXISTS (F07, enhanced with F22)

All existing Arabic validators plus:

New validators:
| Country | Field type | Format rule |
|---------|-----------|-------------|
| EG | Tax Registration | 9 digits |
| EG | Commercial Register | variable, alphanumeric |
| SA | Commercial Register (CR) | 10 digits |
| SA | SADAD Bill Number | variable length numeric |
| AE | Emirates ID | 784-YYYY-NNNNNNN-C |
| AE | Trade License | alphanumeric, emirate-prefixed |
| All | Email | RFC 5322 |
| All | URL | valid URL format |
| All | Arabic text only | Unicode Arabic block |
| All | English text only | ASCII letters |

```
Custom validator support:
    -> Admin defines regex + error message per org
    -> Saved as reusable validators in org settings
    -> Available in element properties dropdown alongside built-in validators
```

#### DS-08: Template Versioning & Lifecycle — ✅ PARTIAL (F19, clone + version working; full approval workflow not yet)

```
Template lifecycle (expanded):

    draft -> submitted_for_review -> approved -> published (v1.0)
                  |                                  |
                  v                                  v
             rejected (back to draft)         new_draft (clone from v1.0)
                                                     |
                                                     v
                                              submitted_for_review -> approved -> published (v2.0)
                                                                                      |
                                                                                      v
                                                                                   archived

State machine:
    - draft: editable by designer
    - submitted_for_review: read-only, pending reviewer action
    - rejected: returned to designer with comments, becomes editable again
    - approved: pending admin publish action
    - published: immutable, usable in Form Desk
    - archived: hidden from Form Desk, visible in template library with filter
    - deprecated: still visible but shows warning "newer version available"

Version tracking:
    - Each publish increments version: v1.0, v2.0, v3.0
    - Minor versions for metadata-only changes: v1.1
    - All versions retained and accessible
    - Form Desk defaults to latest published version
    - Submissions reference the exact version used
    - Version comparison: diff view showing what changed between versions

Cloning:
    - Clone any template (any status) into a new draft
    - Clone preserves: all pages, elements, properties, validation rules
    - Clone creates: new template_id, resets version to 0 (draft), resets status
    - Cross-org cloning (marketplace): strips org-specific data, preserves structure
```

#### DS-09: OCR Onboarding Pipeline — ✅ PARTIAL (F26, single-form import done; batch wizard is Phase 3)

```
Two entry points:
    1. Single form: Design Studio toolbar -> "Import from Scan"
    2. Batch onboarding: /studio/import -> "Digitize Form Library"

Single form import (enhanced from current):
    Designer uploads scanned form image or PDF
    -> POST /api/ai/detect — Azure Document Intelligence
    -> Detection results returned as bounding boxes with field classification
    -> AI suggests: field type, label, validation rules per detection
    -> Canvas overlays detection boxes with Accept/Reject/Modify controls
    -> Accepted detections become FormCraft elements with suggested properties
    -> Rejected detections dismissed
    -> Modified detections: adjust bounding box + properties before accepting

Batch onboarding wizard (/studio/import):
    Step 1: Upload — drag-drop or select multiple PDF/image files (up to 200)
    Step 2: Processing — background OCR job with progress bar
    Step 3: Review dashboard — each form shown as card:
        - Thumbnail preview
        - AI-suggested template name and category
        - Detection count and confidence score
        - Status: pending review / approved / needs work
    Step 4: Per-form review — same Accept/Reject/Modify as single import
    Step 5: Bulk actions — "Approve All High Confidence (>90%)" button
    Step 6: Result — N new draft templates created in library, ready for refinement

Business value: "Your bank has 300 paper forms. We digitize them all in a week."
```

#### DS-10: Template Feedback — ✅ EXISTS (F20, reframed from F11-F14)

```
Feedback tied to specific template versions:

Operator fills a form in Form Desk -> encounters issue
    -> Clicks feedback icon on the form filler toolbar
    -> Feedback widget opens, pre-populated with:
        - Template name and version
        - Current page
        - Field being filled (if any)
    -> Operator types feedback, optionally attaches screenshot
    -> POST /api/templates/:id/feedback

Designer opens template in Design Studio
    -> Feedback panel (side drawer) shows all feedback for this template
    -> Filter by: version, status (new/acknowledged/resolved), field
    -> Each feedback item shows: operator name, date, message, affected field
    -> Designer can:
        - Acknowledge feedback
        - Mark as resolved (with comment)
        - Link feedback to a specific element on canvas (highlight)
    -> Resolved feedback contributes to template quality score

Admin dashboard: /admin/template-feedback
    -> Cross-template feedback overview
    -> Most-reported templates, most-reported fields
    -> Feedback resolution rate and time-to-resolve metrics
```

#### DS-11: Reference Data Manager — ✅ EXISTS (F24)

```
/studio/reference-data — organizational lookup lists that feed into Form Desk

List schema definition (by Admin / Designer):
    -> Admin creates a reference data list:
        Name: "Authorized Signatories"
        Schema: [
            { key: "name_ar", type: "text", required: true },
            { key: "name_en", type: "text", required: true },
            { key: "title_ar", type: "text" },
            { key: "title_en", type: "text" },
            { key: "signature_image", type: "file", accept: "image/*" },
            { key: "authority_level", type: "dropdown", options: ["branch", "regional", "executive"] },
            { key: "max_amount", type: "currency", description: "Maximum cheque amount this signatory can authorize" }
        ]
        Scope: org-wide / department-specific / branch-specific
    -> Other common lists:
        "Beneficiaries" — name, ID, bank, account, IBAN
        "Cost Centers" — code, name_ar, name_en, department, GL account
        "Currencies" — code, name_ar, name_en, symbol, tafqeet_config
        "Department Heads" — name, title, department, approval_limit

List data management:
    -> Admin populates list entries (CRUD)
    -> Bulk import from CSV/Excel
    -> Active/inactive toggle per entry (deactivate signatory on leave, don't delete)
    -> Audit trail: who added/modified/deactivated each entry and when
    -> Effective dates: entry valid from/to (auto-deactivate expired entries)

Designer binds list to form fields:
    -> In Canvas Editor, designer selects a field (e.g., "Signatory Name")
    -> Properties panel: Data Source = "Reference List"
    -> Selects list: "Authorized Signatories"
    -> Maps list columns to form fields:
        signatory_name_field <- list.name_ar
        signatory_title_field <- list.title_ar
        signature_image_field <- list.signature_image
    -> One selection auto-populates all mapped fields

Form Desk behavior:
    -> Operator reaches a reference-list-bound field
    -> Searchable dropdown appears with active entries from the list
    -> Operator types to filter (search across all visible columns)
    -> Selects entry -> all mapped fields auto-fill
    -> Fields are editable after auto-fill (override allowed if template permits)
    -> Audit log records which list entry was selected (traceability)

Cascading lists:
    -> Department -> Cost Centers filtered by department -> Approver filtered by cost center
    -> Country -> City -> Branch (hierarchical filtering)
```

### Form Desk Features

#### FD-01: Operator Dashboard (`/desk`) — ✅ EXISTS (F16)

```
Operator logs in -> lands on /desk (role-based default)

Dashboard sections:
    -> "Quick Actions" bar: search field + "New Form" dropdown of favorites
    -> "Recently Used" section: last 10 forms filled, one-click to refill same template
    -> "Pinned Forms" section: operator's starred favorites (drag to reorder)
    -> "Saved Drafts" section: partially filled forms with resume button + age indicator
    -> "All Forms" section: searchable grid of all published templates
        -> Filter by: category, language, country
        -> Search by: template name, description, tags
        -> Sort by: name, most used, recently updated
    -> Each form card shows: name, category, version, last used date, quality score badge
    -> Click card -> navigate to /desk/fill/:templateId

Notifications panel:
    -> Template feedback responses from designers
    -> New template versions published ("KYC Form updated to v3.0")
    -> Batch job completions
    -> System announcements from admin
```

#### FD-02: Form Filler (`/desk/fill/:templateId`) — ✅ EXISTS (F17)

```
Form filler loads the latest published version of the template

Rendering modes (toggle in toolbar):
    "Print Layout" view:
        -> Fields positioned at exact mm coordinates matching PDF output
        -> WYSIWYG — what you see is exactly what will print
        -> Background image visible (if template has one)
        -> Best for: verifying layout accuracy, training new operators
    "Flow Layout" view:
        -> Fields stacked vertically by section, responsive width
        -> Tab order follows logical grouping (defined by designer)
        -> Keyboard-optimized: Tab to next field, Enter to submit section
        -> Best for: high-speed data entry, daily operational use
    "Split View":
        -> Left: Flow Layout form fields
        -> Right: live PDF preview updating as fields are filled
        -> Best for: complex forms where operators need visual confirmation

Field rendering (Angular form controls):
    text       -> mat-input (dir="auto" for mixed Arabic/English)
    number     -> mat-input type=number with locale-aware formatting
    date       -> mat-datepicker with Hijri/Gregorian toggle (configurable per org)
    currency   -> mat-input with currency mask + auto-tafqeet trigger
    checkbox   -> mat-checkbox
    radio      -> mat-radio-group
    dropdown   -> mat-select with searchable options (for long lists)
    image      -> file upload button or camera capture (mobile)
    QR         -> auto-generated QR code preview from field value
    barcode    -> auto-generated barcode preview from field value
    tafqeet    -> read-only, auto-computed from linked source field, updates live
    signature  -> signature pad (touch/stylus) or upload image
    table      -> editable grid with add/remove rows, column totals

Live validation:
    -> Required fields: red outline on blur if empty
    -> Arabic validators (F07): national ID, IBAN, phone, VAT — validated on each keystroke
    -> Pattern rules from element.validation JSONB: min/max, regex, custom
    -> Cross-field validation: "end_date must be after start_date"
    -> Validation errors shown inline below each field (bilingual: Arabic + English)
    -> Form-level validation summary: "3 errors remaining" banner at top
    -> Submit button disabled until all required fields valid

Conditional logic (at fill time):
    -> visible_when rules evaluated as operator fills fields
    -> Fields appear/disappear smoothly (no page jump)
    -> required_when rules activate/deactivate dynamically
    -> computed_value formulas recalculate on dependency change
    -> Example: operator selects "Corporate" account type -> corporate-only fields appear

Auto-populate:
    -> Fields with default_value pre-filled on form open
    -> Fields with auto_populate rules can pull from:
        - Customer profile (if customer selected — see FD-08)
        - Previous submission (if "Clone as New" used)
        - System values (current date, operator name, branch name)

Toolbar: [Save Draft] [Preview PDF] [Print] [Print & Next] [Clear All] [Cancel]
    -> Keyboard shortcuts: Ctrl+S (save draft), Ctrl+P (print), Ctrl+Enter (print & next)

Tafqeet auto-compute:
    Operator types "1500.25" in amount field
    -> Linked tafqeet field instantly shows "ألف وخمسمائة جنيه مصري وخمسة وعشرون قرشاً"
    -> Both Arabic and English if template configured for "Both"

Offline resilience:
    -> Form state auto-saved to localStorage every 30 seconds
    -> If network drops during print: form data preserved, retry on reconnection
    -> Toast: "Connection lost — your work is saved locally"
```

#### FD-03: Save & Resume Drafts

```
Save:
    Operator partially fills a form -> clicks "Save Draft" or Ctrl+S
    -> POST /api/desk/drafts with { template_id, template_version, field_data, operator_id }
    -> Draft saved with timestamp and auto-generated name ("KYC Form - Draft - 15 May 10:22")
    -> Operator can rename the draft for identification
    -> Operator can close browser and come back later

Resume:
    /desk/drafts shows all saved drafts for this operator
    -> Sorted by last modified (most recent first)
    -> Each draft shows: template name, draft name, last modified, completion % (filled/total fields)
    -> Click draft -> form filler loads with all previously entered data
    -> Continue filling -> submit/print or save again
    -> Version check: if template was updated since draft was saved, show warning:
        "This form was updated to v3.0 since you saved this draft (v2.0).
         [Continue with v2.0] [Migrate to v3.0]"
    -> Migration: attempt to map old field data to new version by field key

Auto-save:
    -> Drafts auto-save every 60 seconds while form is open
    -> Auto-saved drafts marked differently from manual saves
    -> Drafts auto-expire after configurable period (org setting, default: 7 days)
    -> Warning at 24h before expiry: "This draft will expire tomorrow"
    -> Draft count badge shown on /desk dashboard
```

#### FD-04: PDF Preview & Print

```
Preview:
    Operator clicks "Preview PDF"
    -> POST /api/pdf/render/:templateId with { data: {filled_field_values} }
    -> PDF opens in overlay dialog with embedded viewer
    -> Operator verifies output matches expectations
    -> Close overlay to continue editing

Print:
    Operator clicks "Print"
    -> Validation check: all required fields must be filled
    -> If validation fails: scroll to first error, highlight it, block print
    -> If validation passes:
        -> PDF generated with filled data
        -> Browser print dialog opens (or sent to configured network printer)
        -> On successful print confirmation:
            -> form_submissions row created:
                { template_id, template_version, operator_id, org_id, field_data (JSONB),
                  printed_at, printer_name, status: "printed", ip_address, branch_id }
            -> Audit log: FORM_PRINTED event
            -> Draft deleted (if form was resumed from a draft)
            -> Submission reference number generated and shown to operator
            -> Form filler resets to blank

Print & Next:
    -> Same as Print, but form filler immediately resets for the next entry
    -> No intermediate "success" screen — optimized for high-throughput (bank teller window)
    -> Subtle success toast: "Printed. Ref: FC-2026-05-0042"

Save without printing:
    -> Operator clicks "Submit" (without print)
    -> Form data saved as submission with status: "submitted" (not "printed")
    -> Use case: digital-only workflows where PDF is generated later or downstream
```

#### FD-05: Submission History & Reprint — ✅ EXISTS (F18)

```
/desk/history — all forms this operator has submitted

Table columns: ref number, date, template name, key field values (first 3), status, actions
    -> Search by: date range, template, reference number, field values (full-text)
    -> Filter by: template, status (submitted/printed/archived), date range
    -> Sort by: date (default: newest first)
    -> Pagination: 25/50/100 per page

Row actions:
    -> "View" -> read-only view of filled data (all fields)
    -> "Reprint" -> regenerates PDF from stored field_data
        -> Uses the same template version that was originally used
        -> Stamped with "REPRINT" watermark and reprint timestamp
    -> "Clone as New" -> opens form filler pre-filled with this submission's data
        -> Creates a new submission (new reference number)
        -> Useful for: "same form, different customer" workflows
    -> "Export" -> download filled data as JSON or CSV
    -> "Archive" -> marks submission as archived (hidden from default view, still accessible)

Submission detail view:
    -> All field values displayed in form layout
    -> Audit trail: who created, when printed, any reprints
    -> Attached files (signatures, uploaded images)
    -> PDF download button
    -> Template version and quality score at time of filling
```

#### FD-06: Batch Operations & Print Queue

```
Batch form generation:
    Admin or Operator navigates to /desk/queue
    -> "New Batch Job" button
    -> Step 1: Select template (from published templates)
    -> Step 2: Upload data source:
        Option A: CSV file upload with column mapping UI
        Option B: Excel (.xlsx) file upload
        Option C: Paste from clipboard (tab-separated)
        Option D: API endpoint (pull data from external system)
    -> Step 3: Column mapping:
        -> Drag-drop mapper: CSV columns -> template field keys
        -> Auto-map by matching column headers to field labels
        -> Preview: first 5 rows rendered inline
    -> Step 4: Validation preview:
        -> All rows validated against template rules
        -> Valid rows: green checkmarks
        -> Invalid rows: red with specific error per field
        -> "Fix errors" option: inline edit invalid rows
        -> "Skip invalid rows" option: proceed with valid rows only
    -> Step 5: Generate
        -> Background job creates N PDFs
        -> Progress bar: "Generated 127/500 PDFs"
        -> Each PDF logged as individual form_submission with batch_job_id
    -> Step 6: Download
        -> Individual PDFs as ZIP
        -> Merged single PDF (all records concatenated)
        -> Send to network printer queue

Queue dashboard (/desk/queue):
    -> Active jobs: progress bar, estimated time, cancel button
    -> Completed jobs: download link, row count, success/fail count, timestamp
    -> Failed jobs: error summary, download error report CSV
    -> Scheduled jobs: recurring batches (e.g., daily statement run)

Scheduled batches:
    -> Admin configures recurring batch job:
        Template + data source (API endpoint) + schedule (cron expression)
    -> System runs job automatically on schedule
    -> Results available in queue dashboard
    -> Email notification on completion or failure
```

#### FD-07: Form Desk Search & Quick Fill

```
Global search bar at top of /desk:
    -> Type template name -> instant filtered results
    -> Type reference number -> jump directly to submission
    -> Type customer name (if customer profiles enabled) -> show customer's recent forms

Quick Fill mode:
    -> Operator selects template + optional customer profile
    -> Customer's known data auto-populated into matching fields
    -> Operator only fills remaining empty fields
    -> Reduces fill time from minutes to seconds for repeat customers
```

#### FD-08: Customer Profiles (new)

```
/desk/customers — address book of known customers/entities

Customer profile:
    id, name_ar, name_en, identifier (national ID / commercial register),
    identifier_type, contact_phone, contact_email, address,
    custom_fields (JSONB — org-configurable), org_id, created_at

Usage in Form Desk:
    -> Operator starts filling a form
    -> Clicks "Select Customer" button (or field auto-suggest as they type a name)
    -> Customer profile selected
    -> All matching fields auto-populated:
        National ID field <- customer.identifier
        Name field <- customer.name_ar or name_en (based on form language)
        Phone field <- customer.contact_phone
        Address field <- customer.address
    -> Operator fills remaining fields manually

Customer profile CRUD:
    -> Created automatically when operator submits a form with new customer data
        (configurable: "Auto-create customer profiles from submissions" toggle)
    -> Created manually from /desk/customers
    -> Edited by operators (own org only)
    -> Merged by admin (deduplicate two profiles into one)
    -> Deleted by admin (with audit log)

Customer form history:
    -> Click customer -> see all forms ever filled for this customer
    -> Cross-template view: KYC form (3 submissions), Cheque (12 submissions), etc.
    -> Useful for: customer service, compliance review, relationship overview

Privacy:
    -> Customer data encrypted at rest (Supabase column encryption)
    -> Access limited to same-org users
    -> Audit log records every access to customer profiles
    -> Data retention policy: auto-archive after configurable period
```

#### FD-09: Overlay Print Mode — ✅ EXISTS (F23)

```
Print mode toggle per template — Full Print vs. Overlay Print

Full Print (default):
    -> PDF includes: background image, borders, labels, static text, AND filled data
    -> Used when printing on plain paper — the PDF IS the complete form
    -> Existing behavior enhanced

Overlay Print (new):
    -> PDF includes ONLY: filled data values at exact mm coordinates
    -> Transparent background — no borders, no labels, no static text
    -> Used when printing onto pre-printed stationery:
        - Bank cheque books (pre-printed security paper)
        - Government certificates (pre-printed with watermarks and seals)
        - Official letterhead (pre-printed header/footer)
        - Insurance claim forms (pre-printed multi-part carbonless)

Designer configuration (/studio/designer):
    -> Template settings panel: Print Mode = "Full" | "Overlay" | "Both"
    -> "Both" mode: operator chooses at print time
    -> Stationery registration:
        -> Upload scan of blank pre-printed form (high-res image)
        -> Scan displayed as canvas background for positioning reference
        -> Scan excluded from overlay PDF output (design-time only)
    -> Per-element toggle: "Include in overlay" (default: only data fields)
        -> Allows exceptions: org logo or stamp that should print even in overlay mode

Calibration system:
    -> /desk/settings/printers — printer profile management
    -> "Print Calibration Page" button:
        -> Generates A4 page with crosshair grid at known mm positions
        -> Operator prints on pre-printed stationery
        -> Compares printed positions to expected positions
        -> Enters offset adjustments:
            X offset: +/- mm (horizontal shift)
            Y offset: +/- mm (vertical shift)
    -> Printer profile saved:
        { name: "Teller Window 3 — HP LaserJet", x_offset_mm: 1.5, y_offset_mm: -0.8 }
    -> Offsets applied automatically when printing to that printer
    -> Multiple printer profiles per branch

Form Desk print flow (overlay mode):
    -> Operator fills form in Form Filler
    -> Clicks "Print" -> system detects template has overlay mode
    -> Dialog: "Select printer profile" (dropdown of saved profiles)
    -> PDF preview shows:
        -> "Overlay Preview": filled data on transparent background
        -> "Composite Preview": filled data overlaid on stationery scan (for verification)
    -> Operator loads pre-printed stationery into printer tray
    -> Clicks "Print Overlay" -> PDF with only data values sent to printer
    -> Result: filled data printed at exact positions on pre-printed paper
```

### Platform Console Features

#### PC-01: Platform Admin Dashboard — ✅ DONE (backend + frontend; tier enforcement still missing)

```
/platform — cross-org management for platform super-admins (is_platform_admin=true)

Backend API exists (all protected by require_platform_admin()):
    POST   /api/organizations                    — create org
    GET    /api/organizations                    — list all orgs
    GET    /api/organizations/:id                — get org details
    PATCH  /api/organizations/:id                — update org
    POST   /api/organizations/:id/logo           — upload org logo

Frontend needed:
    /platform/organizations         — list all organizations with search, filter, create button
    /platform/organizations/new     — create organization form
    /platform/organizations/:id     — org detail: settings, stats, subscription, users overview

Organization list view:
    -> Table: org name (AR/EN), subscription tier, active users count, templates count,
       submissions this month, status (active/suspended), created date
    -> Search by: org name, custom domain
    -> Filter by: subscription tier, status, country
    -> Sort by: name, created date, user count, submission volume
    -> Actions per row: View Details, Suspend, Reactivate

Create organization:
    -> Form: name_ar*, name_en, default_language, default_country, default_currency
    -> Subscription tier: starter / professional / enterprise / platform
    -> Creates org -> auto-generates first admin invitation
    -> POST /api/organizations -> returns org_id
    -> Next step: invite the org's first admin user

Organization detail view:
    -> Profile tab: name, logo, domain, branding, settings (read/write)
    -> Subscription tab: current tier, limits, usage stats, upgrade/downgrade
    -> Users tab: all users in this org (read-only overview with counts by role)
    -> Stats tab: templates count, submissions this month/total, storage usage
    -> Actions: Suspend org (disables all logins), Delete org (destructive, requires confirmation)

Platform-wide overview (dashboard):
    /platform — landing page with:
    -> Total organizations, total users, total submissions (platform-wide)
    -> Orgs by tier (pie chart)
    -> Submission volume trend (line chart)
    -> Recently created orgs
    -> Orgs approaching tier limits (alerts)
```

**Key implementation notes:**
- Platform Admin is NOT a role — it's `is_platform_admin=true` flag on `profiles` table
- A user can be both `role: 'admin'` within their org AND `is_platform_admin: true`
- Platform Console routes require a new `PlatformAdminGuard` checking `is_platform_admin`
- The `/platform` tab in the nav bar is only visible when `is_platform_admin=true`
- This is completely separate from the Org Admin's `/admin/settings` page

---

### Admin Console Features

#### AC-01: Organization Settings — ✅ EXISTS (F25)

```
/admin/settings — org-level settings for the CURRENT organization (Org Admin, NOT Platform Admin)

Note: This is the Org Admin editing THEIR OWN org's settings.
For creating/managing MULTIPLE organizations, see PC-01 (Platform Console).

Organization profile:
    -> Name (Arabic + English)
    -> Logo (shown in nav bar, PDF headers, login page)
    -> Primary color / theme (white-label UI tinting)
    -> Default language (AR/EN)
    -> Default country (EG/SA/AE)
    -> Default currency
    -> Custom domain (CNAME mapping for white-label URL)
    -> Subscription tier and limits

Org-level settings:
    -> Template approval workflow: enabled/disabled, number of review stages
    -> Draft expiry period: 7/14/30/90 days
    -> Data retention policy: auto-archive submissions after N months
    -> Customer profile auto-creation: on/off
    -> Allowed file types for media upload
    -> Max batch job size (rows per job)
    -> Custom validators library (org-specific regex rules)
    -> Hijri date support: on/off
    -> Notification preferences: email on/off, in-app on/off
```

#### AC-02: User Management — ✅ PARTIAL (F01 + F25, invitation workflow exists; bulk import, custom roles not yet)

```
/admin/users — enhanced from current implementation

User CRUD (enhanced):
    -> All existing functionality plus:
    -> Assign user to department/branch (for multi-branch orgs)
    -> Assign user to teams (for permission scoping)
    -> Bulk user import: upload CSV of users with roles
    -> User activity log: last login, forms filled this month, templates created
    -> Account actions: activate, deactivate, reset password, force logout

Role management (enhanced):
    Built-in roles: Admin, Designer, Reviewer (NEW), Operator, Viewer
    -> Reviewer role: can approve/reject template submissions but cannot publish
    -> Custom roles (Phase 3): admin defines custom role with granular permission matrix

Department / Branch structure:
    -> Org has departments (e.g., "Retail Banking", "Corporate Banking")
    -> Departments have branches (e.g., "Cairo Branch", "Riyadh Branch")
    -> Users assigned to department + branch
    -> Template access can be scoped by department
    -> Submission reporting can be filtered by branch
    -> RLS enforces: department-level isolation where configured

Invitation workflow:
    -> Admin enters email + role + department
    -> System sends invitation email with one-time setup link
    -> New user clicks link -> sets password -> profile created
    -> No shared passwords or manual credential distribution
```

#### AC-03: Template Governance (new)

```
/admin/templates — administrative view of all templates

Template oversight:
    -> List all templates across all statuses with admin actions
    -> Filter by: designer, status, department, category, version
    -> Bulk actions: archive selected, reassign designer, change category

Approval workflow (when enabled):
    -> Queue of templates in "submitted_for_review" status
    -> Reviewer opens template in read-only canvas preview
    -> Side panel shows: version diff (if updating existing), designer notes, previous feedback
    -> Reviewer actions:
        Approve -> template moves to "approved" (pending admin publish)
        Reject -> template returns to "draft" with reviewer comments
        Request Changes -> specific element-level comments (like code review)
    -> Admin sees approved templates -> one-click publish
    -> Full audit trail of review decisions

Template compliance dashboard:
    -> Quality scores across all templates
    -> Templates missing validators on required fields
    -> Templates without bilingual labels
    -> Templates not updated in > 6 months (staleness alert)
    -> Regulatory change tracker: when a validator rule changes, flag affected templates
```

#### AC-04: Audit & Compliance — ✅ EXISTS (F08)

/admin/audit-logs — enhanced from current implementation

All existing audit log functionality plus:

New logged events:
| Action | Trigger |
|--------|---------|
| FORM_SUBMITTED | Operator submits a filled form |
| FORM_PRINTED | Operator prints a form |
| FORM_REPRINTED | Operator reprints a past submission |
| FORM_ARCHIVED | Submission archived |
| BATCH_STARTED | Batch print job initiated |
| BATCH_COMPLETED | Batch print job finished |
| CUSTOMER_CREATED | Customer profile created |
| CUSTOMER_ACCESSED | Customer profile viewed |
| CUSTOMER_UPDATED | Customer profile modified |
| TEMPLATE_SUBMITTED | Template submitted for review |
| TEMPLATE_APPROVED | Template approved by reviewer |
| TEMPLATE_REJECTED | Template rejected by reviewer |
| TEMPLATE_ARCHIVED | Template archived |
| TEMPLATE_CLONED | Template cloned |
| USER_INVITED | User invitation sent |
| USER_DEACTIVATED | User account deactivated |
| ORG_SETTINGS_CHANGED | Organization settings modified |
| DATA_EXPORTED | Submission data exported |

```
Compliance reporting:
    -> Scheduled audit reports: daily/weekly/monthly summary email to admin
    -> Export audit logs as CSV for external compliance systems
    -> Retention: audit logs retained for configurable period (minimum 7 years for banking)
    -> Immutable: audit records cannot be edited or deleted (append-only table)

Data retention engine:
    -> Configurable per org: auto-archive submissions after N months
    -> Configurable per org: purge archived submissions after N years
    -> Pre-purge report: admin reviews what will be deleted before execution
    -> Legal hold: flag specific submissions as "do not purge" (litigation, investigation)
    -> Retention policy change requires admin + confirmation (destructive action)
```

#### AC-05: Analytics & Reporting Dashboard (new)

```
/admin/analytics — operational intelligence

Template analytics:
    -> Most-used templates (by fill count, by department, by branch)
    -> Template usage over time (line chart)
    -> Fill completion rate: started vs. submitted vs. printed
    -> Average fill time per template
    -> Template version adoption: how quickly operators move to new versions

Field analytics:
    -> Error rates per field (which fields cause the most validation failures)
    -> Most common validation errors (by type, by field)
    -> Fields most often left empty (among non-required fields)
    -> Average time spent per field (if telemetry enabled)

Operator analytics:
    -> Forms filled per operator per day/week/month
    -> Average fill time per operator
    -> Error rate per operator (coaching opportunity)
    -> Busiest hours / days (staffing optimization)

Compliance analytics:
    -> % of templates with full validator coverage
    -> % of templates with bilingual labels
    -> Audit log volume by action type
    -> Customer data access frequency (privacy monitoring)

Organizational analytics:
    -> Total forms processed this month/quarter/year
    -> Forms by department / branch
    -> Storage usage (media attachments, PDFs)
    -> Active users this month

Export:
    -> All charts exportable as PNG
    -> All data exportable as CSV / Excel
    -> Scheduled reports: daily/weekly/monthly email with PDF summary
    -> Custom report builder: select metrics + filters + date range -> generate
```

#### AC-06: Notification Center (new)

System-wide notification engine serving all three modes:

Notification types:
| Event | Recipients | Channel |
|-------|-----------|---------|
| Template submitted for review | Assigned reviewers | In-app + email |
| Template approved | Designer who submitted | In-app + email |
| Template rejected | Designer who submitted | In-app + email |
| Template published (new version) | All operators using this template | In-app |
| Template feedback received | Template designer | In-app |
| Batch job completed | Job initiator | In-app + email |
| Batch job failed | Job initiator + admin | In-app + email |
| Draft expiring soon (24h) | Draft owner | In-app |
| Customer profile merged/deleted | Relevant operators | In-app |
| System maintenance scheduled | All users | In-app + email |
| User invited | New user | Email |
| Password reset | User | Email |
| Scheduled report ready | Report subscriber | Email |

```
Notification UI:
    -> Bell icon in nav bar with unread count badge
    -> Dropdown panel: recent notifications with mark-as-read
    -> /notifications: full notification history with filters
    -> Notification preferences: per-user toggle for each notification type and channel

Email engine:
    -> Bilingual email templates (Arabic + English based on recipient's language preference)
    -> HTML emails with org branding (logo, colors)
    -> Unsubscribe link per notification type
    -> Email delivery tracked (sent, delivered, opened — if supported by provider)
```

#### AC-07: Data Export & Integration (new)

```
/admin/export — data export capabilities

Submission data export:
    -> Filter: template, date range, department, branch, operator, status
    -> Format: CSV, Excel (.xlsx), JSON
    -> Scope: field_data flattened (one column per field key) or nested JSON
    -> Schedule: one-time download or recurring (daily/weekly CSV to email or SFTP)

Template export/import:
    -> Export template as .formcraft package (JSON bundle: template + pages + elements + validators)
    -> Import .formcraft package into another org or environment
    -> Use case: dev -> staging -> production promotion
    -> Use case: template sharing between departments

API keys & webhooks (admin manages):
    -> Generate API keys scoped to org
    -> Configure webhook endpoints:
        on_form_submitted: POST to external URL with submission data
        on_form_printed: POST to external URL
        on_template_published: POST to external URL
        on_batch_completed: POST to external URL
    -> Webhook retry logic: 3 attempts with exponential backoff
    -> Webhook logs: delivery status, response codes, payload preview

Integration connectors (Phase 3):
    -> Pre-built connectors for common enterprise systems:
        - Core banking system (field mapping configuration)
        - CRM (customer profile sync)
        - DMS / ECM (auto-archive PDFs to document management system)
        - Email system (send filled PDF as email attachment)
    -> Custom connector builder: HTTP endpoint + field mapping + auth config
```

#### AC-08: Operational Report Engine (new)

```
/admin/reports — business-level reporting on filled form data (not platform analytics)

Pre-built operational reports:
    Transaction Register:
        -> All form submissions in a date range
        -> Filter by: template, operator, branch, department, status, customer
        -> Columns: reference number, template name, operator, customer, date,
                    key field values (amount, beneficiary, etc.), status
        -> Sortable, paginated, searchable
        -> Export: Excel, CSV, PDF

    Daily Reconciliation:
        -> Per-operator, per-branch summary for a single day
        -> Total submissions, total amount (for financial templates),
           breakdown by template type
        -> Designed for end-of-day teller reconciliation
        -> Auto-generated at configurable time (e.g., 5:00 PM daily)
        -> Emailed to branch manager

    Period Summary:
        -> Aggregate totals for a date range (week / month / quarter / year)
        -> By: department, branch, template, operator, cost center
        -> Metrics: submission count, total amount, average amount, min/max
        -> Comparison: this period vs. previous period (trend arrows)
        -> Use case: monthly management report, quarterly board report

    Beneficiary/Payee Report:
        -> All transactions for a specific beneficiary across all templates
        -> Filter by date range, template type, amount range
        -> Use case: "How much did we pay Supplier X this quarter?"
        -> Use case: "All cheques issued to beneficiary Y in 2026"

    Void & Reprint Register:
        -> All voided, cancelled, or reprinted submissions
        -> Shows: original submission, void reason, who voided, who reprinted
        -> Use case: fraud monitoring, operational audit
        -> Flagged if same form voided and reprinted > 3 times

    Signatory Usage Report (uses Reference Data):
        -> Which signatories authorized which transactions
        -> Filter by: signatory, amount range, date, template
        -> Use case: audit trail for financial authorization
        -> Alerts: signatory approaching their authority limit

Custom Report Builder:
    -> Select data dimensions: template fields, submission metadata, customer data
    -> Apply filters: date range, branch, department, operator, template
    -> Choose aggregation: count, sum, average, min, max, distinct
    -> Group by: any dimension (branch, operator, day, week, month)
    -> Choose output: table, bar chart, line chart, pie chart
    -> Preview in browser
    -> Save as named report (reusable)
    -> Schedule: frequency + recipients + format (Excel / PDF / both)

Report access control:
    -> Admin: all reports, all data
    -> Branch Manager: reports scoped to their branch
    -> Operator: "My Activity" report only (own submissions)
    -> Reports respect RLS: never show cross-org data

Report storage:
    -> Generated reports cached for 24 hours
    -> Historical report archives: keep last 12 months of scheduled reports
    -> Export to SFTP or cloud storage (for enterprise data warehouse integration)
```

### External / Public Features

#### EXT-01: External Form Portal (new)

```
Published template -> admin enables "Public Access"
    -> System generates public URL: https://forms.formcraft.io/{org}/{template-slug}
    -> Or custom domain: https://forms.bank.eg/{template-slug}

Public form experience:
    -> No login required (anonymous submission)
    -> Or OTP verification: enter phone number -> receive SMS code -> verify -> fill form
    -> Or simple registration: email + name -> fill form
    -> Form rendered in Flow Layout (responsive, mobile-friendly)
    -> Arabic-first UI with language toggle
    -> All validation rules enforced
    -> Tafqeet computed live
    -> On submit:
        -> Confirmation page with reference number
        -> Optional: PDF download of submitted form
        -> Optional: email confirmation to submitter
        -> Submission stored in form_submissions with source: "public_portal"

Admin oversight:
    -> /admin/portal — manage public form settings
    -> Enable/disable per template
    -> Configure: require OTP? allow PDF download? send email confirmation?
    -> Rate limiting: max submissions per IP per hour
    -> CAPTCHA integration (hCaptcha or reCAPTCHA)
    -> Submission dashboard: filter by portal submissions
```

#### EXT-02: Template Marketplace (new)

```
/marketplace — cross-org template sharing

Publisher flow:
    -> Admin marks a published template as "Marketplace Available"
    -> Adds: description, tags, preview images, compliance certifications
    -> Sets: free or premium (price in USD/SAR/EGP)
    -> Template listed in marketplace with org attribution

Consumer flow:
    -> Any org admin browses marketplace
    -> Filter by: country, category, language, compliance standard, price
    -> Preview: read-only canvas view + sample PDF
    -> "Use Template" -> clones into consumer's org as new draft
    -> Premium templates: payment processed -> then clone
    -> Consumer can modify the cloned template for their needs

Quality assurance:
    -> FormCraft team reviews marketplace submissions (curated marketplace)
    -> Quality score and compliance badges displayed
    -> User ratings and reviews
    -> Download count and usage stats visible to publisher

Revenue model:
    -> Free tier: publish up to 5 templates
    -> Premium: 70/30 revenue share (publisher/FormCraft)
    -> Enterprise: unlimited publishing, featured placement
```

---

## Complete Data Model

### Existing Tables (enhanced)

```
profiles (enhanced)
    id                  UUID PK
    email               TEXT UNIQUE NOT NULL
    role                ENUM (admin, designer, reviewer, operator, viewer)
    language            ENUM (ar, en)
    display_name        TEXT
    is_active           BOOLEAN DEFAULT true
    org_id              UUID FK -> organizations          -- NEW
    department_id       UUID FK -> departments            -- NEW
    branch_id           UUID FK -> branches               -- NEW
    default_mode        ENUM (studio, desk, admin)        -- NEW
    notification_prefs  JSONB                             -- NEW
    last_login_at       TIMESTAMPTZ                       -- NEW
    created_at          TIMESTAMPTZ
    updated_at          TIMESTAMPTZ

templates (enhanced)
    id                  UUID PK
    name                TEXT NOT NULL
    description         TEXT
    category            TEXT
    status              ENUM (draft, submitted, rejected, approved, published, archived, deprecated)  -- ENHANCED
    version             INTEGER DEFAULT 0                 -- NEW
    version_label       TEXT                              -- NEW (e.g., "v2.1")
    parent_version_id   UUID FK -> templates              -- NEW (lineage tracking)
    language            ENUM (ar, en, both)               -- ENHANCED (added "both")
    country             ENUM (EG, SA, AE)
    tags                TEXT[]                             -- NEW
    quality_score       FLOAT                             -- NEW
    public_access       BOOLEAN DEFAULT false             -- NEW
    public_slug         TEXT UNIQUE                       -- NEW
    org_id              UUID FK -> organizations          -- NEW
    department_id       UUID FK -> departments            -- NEW
    created_by          UUID FK -> profiles
    published_by        UUID FK -> profiles               -- NEW
    published_at        TIMESTAMPTZ                       -- NEW
    created_at          TIMESTAMPTZ
    updated_at          TIMESTAMPTZ

template_elements (enhanced)
    id                  UUID PK
    page_id             UUID FK -> template_pages
    type                ENUM (text, number, date, currency, checkbox, radio, dropdown,
                               image, qr, barcode, tafqeet, signature, table,
                               section_header, divider, stamp)        -- ENHANCED
    key                 TEXT NOT NULL
    label_ar            TEXT
    label_en            TEXT
    x                   FLOAT (mm)
    y                   FLOAT (mm)
    width               FLOAT (mm)
    height              FLOAT (mm)
    validation          JSONB
    formatting          JSONB
    direction           ENUM (auto, rtl, ltr)
    required            BOOLEAN DEFAULT false
    sort_order          INTEGER
    source_element_key  TEXT                              -- for tafqeet
    visible_when        JSONB                             -- NEW (conditional visibility)
    required_when       JSONB                             -- NEW (conditional requirement)
    computed_value      JSONB                             -- NEW (formula)
    default_value       TEXT                              -- NEW
    placeholder_text    TEXT                              -- NEW
    help_text           TEXT                              -- NEW (tooltip for operators)
    tab_order           INTEGER                           -- NEW (Form Desk keyboard nav)
    read_only           BOOLEAN DEFAULT false             -- NEW
    section_group       TEXT                              -- NEW (logical grouping)
    dropdown_options    JSONB                             -- NEW (for dropdown type)
    table_columns       JSONB                             -- NEW (for table type)
    created_at          TIMESTAMPTZ
    updated_at          TIMESTAMPTZ
```

### New Tables

```
organizations
    id                  UUID PK
    name_ar             TEXT NOT NULL
    name_en             TEXT NOT NULL
    logo_url            TEXT
    primary_color       TEXT                              -- hex color for white-label
    default_language    ENUM (ar, en)
    default_country     ENUM (EG, SA, AE)
    default_currency    TEXT
    custom_domain       TEXT UNIQUE
    settings            JSONB                             -- org-level configuration
    subscription_tier   ENUM (starter, professional, enterprise)
    created_at          TIMESTAMPTZ
    updated_at          TIMESTAMPTZ

departments
    id                  UUID PK
    org_id              UUID FK -> organizations
    name_ar             TEXT NOT NULL
    name_en             TEXT NOT NULL
    created_at          TIMESTAMPTZ

branches
    id                  UUID PK
    department_id       UUID FK -> departments
    org_id              UUID FK -> organizations
    name_ar             TEXT NOT NULL
    name_en             TEXT NOT NULL
    location            TEXT
    created_at          TIMESTAMPTZ

template_reviews
    id                  UUID PK
    template_id         UUID FK -> templates
    reviewer_id         UUID FK -> profiles
    status              ENUM (approved, rejected, changes_requested)
    comments            TEXT
    element_comments    JSONB                             -- per-element review comments
    created_at          TIMESTAMPTZ

template_feedback
    id                  UUID PK
    template_id         UUID FK -> templates
    template_version    INTEGER
    element_key         TEXT                              -- optional: specific field
    submitted_by        UUID FK -> profiles
    text_content        TEXT NOT NULL
    screenshot_url      TEXT
    status              ENUM (new, acknowledged, resolved)
    resolution_comment  TEXT
    org_id              UUID FK -> organizations
    created_at          TIMESTAMPTZ
    resolved_at         TIMESTAMPTZ

form_submissions
    id                  UUID PK
    reference_number    TEXT UNIQUE NOT NULL               -- e.g., "FC-2026-05-0042"
    template_id         UUID FK -> templates
    template_version    INTEGER NOT NULL
    operator_id         UUID FK -> profiles
    org_id              UUID FK -> organizations
    branch_id           UUID FK -> branches
    customer_id         UUID FK -> customers               -- optional
    field_data          JSONB NOT NULL
    status              ENUM (draft, submitted, printed, reprinted, archived)
    source              ENUM (desk, portal, api, batch)
    printed_at          TIMESTAMPTZ
    printer_name        TEXT
    batch_job_id        UUID FK -> form_print_jobs         -- null if not from batch
    ip_address          INET
    created_at          TIMESTAMPTZ
    updated_at          TIMESTAMPTZ

form_drafts
    id                  UUID PK
    template_id         UUID FK -> templates
    template_version    INTEGER NOT NULL
    operator_id         UUID FK -> profiles
    org_id              UUID FK -> organizations
    draft_name          TEXT
    field_data          JSONB NOT NULL
    completion_pct      FLOAT                             -- filled / total fields
    expires_at          TIMESTAMPTZ
    auto_saved          BOOLEAN DEFAULT false
    created_at          TIMESTAMPTZ
    updated_at          TIMESTAMPTZ

form_print_jobs
    id                  UUID PK
    template_id         UUID FK -> templates
    operator_id         UUID FK -> profiles
    org_id              UUID FK -> organizations
    source_type         ENUM (csv_upload, xlsx_upload, api_call, scheduled)
    source_filename     TEXT
    total_rows          INTEGER NOT NULL
    completed_rows      INTEGER DEFAULT 0
    failed_rows         INTEGER DEFAULT 0
    status              ENUM (pending, validating, processing, completed, failed, cancelled)
    result_url          TEXT                              -- signed URL to ZIP download
    error_log           JSONB
    schedule_cron       TEXT                              -- for recurring jobs
    created_at          TIMESTAMPTZ
    started_at          TIMESTAMPTZ
    completed_at        TIMESTAMPTZ

customers
    id                  UUID PK
    org_id              UUID FK -> organizations
    name_ar             TEXT
    name_en             TEXT
    identifier          TEXT                              -- national ID, commercial register, etc.
    identifier_type     ENUM (national_id, iqama, commercial_register, passport, other)
    contact_phone       TEXT
    contact_email       TEXT
    address             TEXT
    custom_fields       JSONB                             -- org-configurable
    created_by          UUID FK -> profiles
    is_active           BOOLEAN DEFAULT true
    created_at          TIMESTAMPTZ
    updated_at          TIMESTAMPTZ

operator_favorites
    operator_id         UUID FK -> profiles
    template_id         UUID FK -> templates
    sort_order          INTEGER
    pinned_at           TIMESTAMPTZ
    PK (operator_id, template_id)

notifications
    id                  UUID PK
    recipient_id        UUID FK -> profiles
    org_id              UUID FK -> organizations
    type                TEXT NOT NULL                      -- e.g., "template_published", "batch_completed"
    title_ar            TEXT NOT NULL
    title_en            TEXT NOT NULL
    body_ar             TEXT
    body_en             TEXT
    action_url          TEXT                              -- deep link to relevant page
    read_at             TIMESTAMPTZ
    email_sent_at       TIMESTAMPTZ
    created_at          TIMESTAMPTZ

webhook_configs
    id                  UUID PK
    org_id              UUID FK -> organizations
    event_type          TEXT NOT NULL                      -- e.g., "on_form_submitted"
    endpoint_url        TEXT NOT NULL
    headers             JSONB                             -- custom headers (e.g., API key)
    is_active           BOOLEAN DEFAULT true
    created_at          TIMESTAMPTZ

webhook_deliveries
    id                  UUID PK
    webhook_config_id   UUID FK -> webhook_configs
    event_type          TEXT NOT NULL
    payload             JSONB NOT NULL
    response_status     INTEGER
    response_body       TEXT
    attempt_number      INTEGER DEFAULT 1
    delivered_at        TIMESTAMPTZ
    created_at          TIMESTAMPTZ

api_keys
    id                  UUID PK
    org_id              UUID FK -> organizations
    name                TEXT NOT NULL
    key_hash            TEXT NOT NULL                      -- bcrypt hash of the key
    key_prefix          TEXT NOT NULL                      -- first 8 chars for identification
    permissions         JSONB                             -- scoped permissions
    last_used_at        TIMESTAMPTZ
    expires_at          TIMESTAMPTZ
    is_active           BOOLEAN DEFAULT true
    created_by          UUID FK -> profiles
    created_at          TIMESTAMPTZ

custom_validators
    id                  UUID PK
    org_id              UUID FK -> organizations
    name                TEXT NOT NULL
    label_ar            TEXT
    label_en            TEXT
    pattern             TEXT NOT NULL                      -- regex
    error_message_ar    TEXT NOT NULL
    error_message_en    TEXT NOT NULL
    created_by          UUID FK -> profiles
    created_at          TIMESTAMPTZ

reference_lists
    id                  UUID PK
    org_id              UUID FK -> organizations
    name                TEXT NOT NULL                      -- e.g., "Authorized Signatories"
    name_ar             TEXT NOT NULL
    name_en             TEXT NOT NULL
    scope               ENUM (org, department, branch)
    scope_id            UUID                              -- null for org, dept/branch id otherwise
    schema              JSONB NOT NULL                    -- column definitions [{key, type, required, options}]
    is_active           BOOLEAN DEFAULT true
    created_by          UUID FK -> profiles
    created_at          TIMESTAMPTZ
    updated_at          TIMESTAMPTZ

reference_list_entries
    id                  UUID PK
    list_id             UUID FK -> reference_lists
    data                JSONB NOT NULL                    -- {name_ar: "...", name_en: "...", ...}
    sort_order          INTEGER DEFAULT 0
    is_active           BOOLEAN DEFAULT true
    effective_from      DATE                              -- null = always active
    effective_to        DATE                              -- null = no expiry
    created_by          UUID FK -> profiles
    deactivated_by      UUID FK -> profiles
    created_at          TIMESTAMPTZ
    updated_at          TIMESTAMPTZ

reference_list_bindings
    id                  UUID PK
    template_id         UUID FK -> templates
    element_key         TEXT NOT NULL                     -- the form field bound to this list
    list_id             UUID FK -> reference_lists
    field_mappings      JSONB NOT NULL                   -- [{list_column: "name_ar", target_element_key: "signatory_name"}]
    cascade_parent_id   UUID FK -> reference_list_bindings -- for cascading list filters
    cascade_filter_key  TEXT                              -- which list column to filter by parent selection
    created_at          TIMESTAMPTZ

printer_profiles
    id                  UUID PK
    org_id              UUID FK -> organizations
    branch_id           UUID FK -> branches
    name                TEXT NOT NULL                     -- e.g., "Teller Window 3 — HP LaserJet"
    x_offset_mm         DECIMAL(5,2) DEFAULT 0           -- horizontal calibration offset
    y_offset_mm         DECIMAL(5,2) DEFAULT 0           -- vertical calibration offset
    paper_source        TEXT                              -- tray identifier if applicable
    is_default          BOOLEAN DEFAULT false
    created_by          UUID FK -> profiles
    created_at          TIMESTAMPTZ
    updated_at          TIMESTAMPTZ

template_print_settings
    template_id         UUID FK -> templates (PK)
    print_mode          ENUM (full, overlay, both) DEFAULT 'full'
    stationery_scan_url TEXT                              -- uploaded scan of blank pre-printed form
    overlay_include_elements JSONB                       -- element keys to include even in overlay mode
    updated_at          TIMESTAMPTZ

saved_reports
    id                  UUID PK
    org_id              UUID FK -> organizations
    name                TEXT NOT NULL
    name_ar             TEXT
    name_en             TEXT
    report_type         ENUM (transaction_register, daily_reconciliation, period_summary,
                              beneficiary, void_reprint, signatory_usage, custom)
    config              JSONB NOT NULL                    -- filters, dimensions, aggregations, grouping
    visualization       ENUM (table, bar_chart, line_chart, pie_chart) DEFAULT 'table'
    created_by          UUID FK -> profiles
    is_shared           BOOLEAN DEFAULT false             -- visible to other admins in same org
    created_at          TIMESTAMPTZ
    updated_at          TIMESTAMPTZ

scheduled_reports
    id                  UUID PK
    saved_report_id     UUID FK -> saved_reports
    org_id              UUID FK -> organizations
    frequency           ENUM (daily, weekly, monthly, quarterly)
    day_of_week         INTEGER                           -- for weekly (0=Mon, 6=Sun)
    day_of_month        INTEGER                           -- for monthly/quarterly
    time_of_day         TIME NOT NULL                     -- e.g., 17:00
    format              ENUM (excel, pdf, both) DEFAULT 'both'
    recipients          JSONB NOT NULL                    -- [{email, name}]
    is_active           BOOLEAN DEFAULT true
    last_run_at         TIMESTAMPTZ
    next_run_at         TIMESTAMPTZ
    created_by          UUID FK -> profiles
    created_at          TIMESTAMPTZ

report_archives
    id                  UUID PK
    scheduled_report_id UUID FK -> scheduled_reports
    org_id              UUID FK -> organizations
    file_url            TEXT NOT NULL                     -- signed URL to generated report file
    file_format         ENUM (excel, pdf)
    row_count           INTEGER
    generated_at        TIMESTAMPTZ
    expires_at          TIMESTAMPTZ                      -- auto-purge after retention period
```

---

## Complete API Surface

### Authentication & Users

| Endpoint | Method | Role | Purpose |
|----------|--------|:----:|---------|
| `/api/auth/login` | POST | public | User login |
| `/api/auth/refresh` | POST | public | Token refresh |
| `/api/auth/logout` | POST | any | User logout |
| `/api/auth/register` | POST | admin | Create new user (invitation) |
| `/api/auth/accept-invite/:token` | POST | public | New user accepts invitation |
| `/api/auth/forgot-password` | POST | public | Request password reset |
| `/api/auth/reset-password` | POST | public | Reset password with token |
| `/api/users/me` | GET | any | Current user profile |
| `/api/users/me` | PATCH | any | Update own profile (language, display_name, notification_prefs) |
| `/api/admin/users` | GET | admin | List all users in org |
| `/api/admin/users/:id` | GET | admin | User detail |
| `/api/admin/users/:id` | PATCH | admin | Update user role/department/status |
| `/api/admin/users/:id/deactivate` | POST | admin | Deactivate user account |
| `/api/admin/users/bulk-import` | POST | admin | Import users from CSV |

### Platform Admin — Organization CRUD (PC-01) ⚠️ Backend exists, NO frontend

| Endpoint | Method | Auth | Purpose |
|----------|--------|:----:|---------|
| `/api/organizations` | POST | **platform_admin** | Create new organization |
| `/api/organizations` | GET | **platform_admin** | List all organizations |
| `/api/organizations/:id` | GET | **platform_admin** | Get organization details |
| `/api/organizations/:id` | PATCH | **platform_admin** | Update organization |
| `/api/organizations/:id/logo` | POST | **platform_admin** | Upload organization logo |

Note: All 5 endpoints protected by `require_platform_admin()` — checks `is_platform_admin=true` on profile. Returns 403 for non-platform-admins. **No frontend routes exist** — needs `/platform/*` module, guard, and components.

### Organizations & Structure (Org Admin — within current org)

| Endpoint | Method | Role | Purpose |
|----------|--------|:----:|---------|
| `/api/admin/org` | GET | admin | Get current organization settings |
| `/api/admin/org` | PATCH | admin | Update current organization settings |
| `/api/admin/departments` | GET | admin | List departments |
| `/api/admin/departments` | POST | admin | Create department |
| `/api/admin/departments/:id` | PATCH | admin | Update department |
| `/api/admin/departments/:id/branches` | GET | admin | List branches in department |
| `/api/admin/departments/:id/branches` | POST | admin | Create branch |
| `/api/admin/branches/:id` | PATCH | admin | Update branch |

### Design Studio — Templates

| Endpoint | Method | Role | Purpose |
|----------|--------|:----:|---------|
| `/api/templates` | GET | designer+ | List templates (filtered by role/dept) |
| `/api/templates` | POST | designer+ | Create new template |
| `/api/templates/:id` | GET | varies | Get template detail |
| `/api/templates/:id` | PATCH | designer | Update template metadata |
| `/api/templates/:id` | DELETE | designer | Delete draft template |
| `/api/templates/:id/clone` | POST | designer+ | Clone template to new draft |
| `/api/templates/:id/submit` | POST | designer | Submit for review |
| `/api/templates/:id/approve` | POST | reviewer | Approve template |
| `/api/templates/:id/reject` | POST | reviewer | Reject with comments |
| `/api/templates/:id/publish` | POST | admin | Publish approved template |
| `/api/templates/:id/archive` | POST | admin | Archive template |
| `/api/templates/:id/versions` | GET | designer+ | List all versions |
| `/api/templates/:id/versions/:v` | GET | designer+ | Get specific version |
| `/api/templates/:id/diff/:v1/:v2` | GET | designer+ | Diff between versions |
| `/api/templates/:id/export` | GET | admin | Export as .formcraft package |
| `/api/templates/import` | POST | admin | Import .formcraft package |
| `/api/templates/:id/pages/*` | CRUD | designer | Page management |
| `/api/templates/:id/pages/:p/elements/*` | CRUD | designer | Element management |

### Design Studio — AI & Tools

| Endpoint | Method | Role | Purpose |
|----------|--------|:----:|---------|
| `/api/ai/suggest` | POST | designer+ | Single field AI suggestion |
| `/api/ai/suggest-batch` | POST | designer+ | Batch field analysis |
| `/api/ai/detect` | POST | designer+ | OCR form detection (single) |
| `/api/ai/detect-batch` | POST | designer+ | OCR batch detection |
| `/api/ai/quality-score` | POST | designer+ | Template quality analysis |
| `/api/pdf/render/:id` | POST | operator+ | Render PDF (preview or export) |
| `/api/pdf/batch` | POST | operator+ | Batch PDF generation |

### Reference Data

| Endpoint | Method | Role | Purpose |
|----------|--------|:----:|---------|
| `/api/reference-lists` | GET | designer+ | List all reference lists in org |
| `/api/reference-lists` | POST | admin | Create reference list (schema + metadata) |
| `/api/reference-lists/:id` | GET | designer+ | Get list detail with schema |
| `/api/reference-lists/:id` | PATCH | admin | Update list schema or metadata |
| `/api/reference-lists/:id` | DELETE | admin | Delete list (soft — deactivate) |
| `/api/reference-lists/:id/entries` | GET | operator+ | List active entries (with search/filter) |
| `/api/reference-lists/:id/entries` | POST | admin | Create entry |
| `/api/reference-lists/:id/entries/bulk` | POST | admin | Bulk import entries (CSV/JSON) |
| `/api/reference-lists/:id/entries/:eid` | PATCH | admin | Update entry |
| `/api/reference-lists/:id/entries/:eid/deactivate` | POST | admin | Deactivate entry |
| `/api/templates/:id/list-bindings` | GET | designer+ | Get reference list bindings for template |
| `/api/templates/:id/list-bindings` | PUT | designer | Set reference list bindings |

### Printer Profiles & Overlay Print

| Endpoint | Method | Role | Purpose |
|----------|--------|:----:|---------|
| `/api/desk/printers` | GET | operator+ | List printer profiles for user's branch |
| `/api/desk/printers` | POST | operator+ | Create printer profile |
| `/api/desk/printers/:id` | PATCH | operator+ | Update printer profile (calibration offsets) |
| `/api/desk/printers/:id` | DELETE | admin | Delete printer profile |
| `/api/desk/printers/calibration-page` | GET | operator+ | Generate calibration test page PDF |
| `/api/templates/:id/print-settings` | GET | designer+ | Get template print mode settings |
| `/api/templates/:id/print-settings` | PUT | designer | Update print mode (full/overlay/both) |
| `/api/templates/:id/print-settings/stationery` | POST | designer | Upload stationery scan image |
| `/api/pdf/render/:id/overlay` | POST | operator+ | Render overlay-only PDF (data only, no background) |

### Form Desk

| Endpoint | Method | Role | Purpose |
|----------|--------|:----:|---------|
| `/api/desk/templates` | GET | operator+ | List published templates for filling |
| `/api/desk/fill/:id` | POST | operator+ | Submit a filled form |
| `/api/desk/fill/:id/validate` | POST | operator+ | Validate field data without submitting |
| `/api/desk/drafts` | GET | operator+ | List operator's saved drafts |
| `/api/desk/drafts` | POST | operator+ | Save a new draft |
| `/api/desk/drafts/:id` | GET | operator+ | Load a specific draft |
| `/api/desk/drafts/:id` | PUT | operator+ | Update a draft |
| `/api/desk/drafts/:id` | DELETE | operator+ | Discard a draft |
| `/api/desk/history` | GET | operator+ | Operator's submission history |
| `/api/desk/history/:id` | GET | operator+ | View a specific past submission |
| `/api/desk/history/:id/reprint` | POST | operator+ | Reprint a past submission |
| `/api/desk/history/:id/clone` | POST | operator+ | Clone submission as new form fill |
| `/api/desk/history/:id/export` | GET | operator+ | Export submission data (JSON/CSV) |
| `/api/desk/favorites` | GET | operator+ | List pinned templates |
| `/api/desk/favorites/:templateId` | PUT | operator+ | Pin a template |
| `/api/desk/favorites/:templateId` | DELETE | operator+ | Unpin a template |
| `/api/desk/queue` | GET | operator+ | List print jobs |
| `/api/desk/queue` | POST | admin/operator | Create batch print job |
| `/api/desk/queue/:id` | GET | operator+ | Job status and progress |
| `/api/desk/queue/:id/cancel` | POST | operator+ | Cancel running job |
| `/api/desk/queue/:id/download` | GET | operator+ | Download completed ZIP |

### Customers

| Endpoint | Method | Role | Purpose |
|----------|--------|:----:|---------|
| `/api/desk/customers` | GET | operator+ | List customers in org |
| `/api/desk/customers` | POST | operator+ | Create customer profile |
| `/api/desk/customers/:id` | GET | operator+ | Get customer detail |
| `/api/desk/customers/:id` | PATCH | operator+ | Update customer profile |
| `/api/desk/customers/:id/history` | GET | operator+ | Customer's form submission history |
| `/api/desk/customers/search` | GET | operator+ | Search by name, identifier |
| `/api/admin/customers/:id/merge` | POST | admin | Merge duplicate profiles |
| `/api/admin/customers/:id` | DELETE | admin | Delete customer profile |

### Template Feedback

| Endpoint | Method | Role | Purpose |
|----------|--------|:----:|---------|
| `/api/templates/:id/feedback` | GET | designer+ | List feedback for template |
| `/api/templates/:id/feedback` | POST | operator+ | Submit feedback on template |
| `/api/templates/:id/feedback/:fid` | PATCH | designer | Acknowledge/resolve feedback |
| `/api/admin/template-feedback` | GET | admin | Cross-template feedback overview |

### Admin — Governance & Reporting

| Endpoint | Method | Role | Purpose |
|----------|--------|:----:|---------|
| `/api/admin/submissions` | GET | admin | All submissions across all operators |
| `/api/admin/submissions/export` | POST | admin | Bulk export submission data |
| `/api/admin/audit-logs` | GET | admin | Audit log with filters |
| `/api/admin/audit-logs/:id` | GET | admin | Audit log detail (before/after) |
| `/api/admin/audit-logs/export` | POST | admin | Export audit logs |
| `/api/admin/analytics/templates` | GET | admin | Template usage analytics |
| `/api/admin/analytics/operators` | GET | admin | Operator performance analytics |
| `/api/admin/analytics/submissions` | GET | admin | Submission volume analytics |
| `/api/admin/analytics/compliance` | GET | admin | Compliance score analytics |
| `/api/admin/analytics/export` | POST | admin | Export analytics report |
| `/api/admin/validators` | GET | admin | List custom validators |
| `/api/admin/validators` | POST | admin | Create custom validator |
| `/api/admin/validators/:id` | PATCH | admin | Update custom validator |
| `/api/admin/validators/:id` | DELETE | admin | Delete custom validator |

### Operational Reports

| Endpoint | Method | Role | Purpose |
|----------|--------|:----:|---------|
| `/api/admin/reports/transaction-register` | GET | admin/manager | Transaction register with filters |
| `/api/admin/reports/daily-reconciliation` | GET | admin/manager | Daily per-operator/branch summary |
| `/api/admin/reports/period-summary` | GET | admin/manager | Aggregate totals for date range |
| `/api/admin/reports/beneficiary` | GET | admin/manager | All transactions for a beneficiary |
| `/api/admin/reports/void-reprint` | GET | admin/manager | Void and reprint register |
| `/api/admin/reports/signatory-usage` | GET | admin/manager | Signatory authorization usage |
| `/api/admin/reports/my-activity` | GET | operator+ | Operator's own submission report |
| `/api/admin/reports/saved` | GET | admin | List saved report configs |
| `/api/admin/reports/saved` | POST | admin | Create saved report |
| `/api/admin/reports/saved/:id` | GET | admin | Get saved report config |
| `/api/admin/reports/saved/:id` | PATCH | admin | Update saved report |
| `/api/admin/reports/saved/:id` | DELETE | admin | Delete saved report |
| `/api/admin/reports/saved/:id/run` | POST | admin | Run report now (generate on demand) |
| `/api/admin/reports/scheduled` | GET | admin | List scheduled reports |
| `/api/admin/reports/scheduled` | POST | admin | Schedule a saved report |
| `/api/admin/reports/scheduled/:id` | PATCH | admin | Update schedule |
| `/api/admin/reports/scheduled/:id` | DELETE | admin | Delete schedule |
| `/api/admin/reports/archives` | GET | admin | List generated report archives |
| `/api/admin/reports/archives/:id/download` | GET | admin | Download archived report |

### Notifications

| Endpoint | Method | Role | Purpose |
|----------|--------|:----:|---------|
| `/api/notifications` | GET | any | List user's notifications |
| `/api/notifications/unread-count` | GET | any | Unread notification count |
| `/api/notifications/:id/read` | POST | any | Mark notification as read |
| `/api/notifications/read-all` | POST | any | Mark all as read |
| `/api/notifications/preferences` | GET | any | Get notification preferences |
| `/api/notifications/preferences` | PATCH | any | Update notification preferences |

### Webhooks & API Keys

| Endpoint | Method | Role | Purpose |
|----------|--------|:----:|---------|
| `/api/admin/webhooks` | GET | admin | List webhook configurations |
| `/api/admin/webhooks` | POST | admin | Create webhook |
| `/api/admin/webhooks/:id` | PATCH | admin | Update webhook |
| `/api/admin/webhooks/:id` | DELETE | admin | Delete webhook |
| `/api/admin/webhooks/:id/test` | POST | admin | Send test event |
| `/api/admin/webhooks/:id/deliveries` | GET | admin | Delivery history |
| `/api/admin/api-keys` | GET | admin | List API keys |
| `/api/admin/api-keys` | POST | admin | Create API key |
| `/api/admin/api-keys/:id` | DELETE | admin | Revoke API key |

### External Portal

| Endpoint | Method | Role | Purpose |
|----------|--------|:----:|---------|
| `/api/portal/:slug` | GET | public | Get public form metadata |
| `/api/portal/:slug/submit` | POST | public | Submit public form |
| `/api/portal/:slug/verify-otp` | POST | public | OTP verification |
| `/api/portal/submission/:ref` | GET | public | Check submission status |

### Health & System

| Endpoint | Method | Role | Purpose |
|----------|--------|:----:|---------|
| `/api/health` | GET | public | System health check |
| `/api/health/detailed` | GET | admin | Detailed health (DB, storage, AI, queues) |

---

## Cross-Cutting Platform Capabilities

### Enterprise Authentication (enhanced)

```
Current: email + password via Supabase Auth

Phase 2 additions:
    -> SAML 2.0 SSO: integrate with corporate identity providers (AD FS, Okta, Azure AD)
    -> OIDC support: Google Workspace, Microsoft Entra ID
    -> MFA: TOTP (authenticator app) or SMS OTP as second factor
    -> Session management: configurable session timeout, concurrent session limit
    -> IP whitelisting: restrict access to corporate network ranges
    -> Password policy: min length, complexity, rotation period (configurable per org)
```

### Internationalization (enhanced)

```
Current: Arabic (RTL) + English (LTR) with ngx-translate

Additions:
    -> Bilingual templates: single template with both AR and EN labels, rendered based on user preference
    -> Hijri date support: date fields can display/accept Hijri calendar dates (configurable per org)
    -> Additional locale support: French (for North Africa), Urdu (for UAE labor market)
    -> Number formatting: locale-aware thousand separators and decimal points
    -> Currency formatting: EGP, SAR, AED, USD with proper symbol placement
    -> Email templates: bilingual (sent in recipient's preferred language)
    -> PDF output: language selection per export (AR, EN, or Both on same page)
```

### Security & Compliance (enhanced)

```
Current: JWT + Supabase RLS + audit logging

Additions:
    -> Data encryption at rest: customer data, field_data in submissions (Supabase column encryption)
    -> Data encryption in transit: TLS 1.3 enforced
    -> PII masking in audit logs: sensitive field values hashed, not stored in plaintext
    -> GDPR-style data subject rights: export all data for a customer, delete all data for a customer
    -> Penetration testing schedule: quarterly (documented in compliance artifacts)
    -> SOC 2 readiness: audit log immutability, access controls, data retention policies
    -> Rate limiting: configurable per endpoint, per org, per user
    -> CORS: strict origin whitelist per org
    -> CSP headers: prevent XSS via Content Security Policy
    -> File upload scanning: validate MIME types server-side, strip metadata from images
```

### Mobile & Responsive Support

```
Form Desk — mobile-optimized:
    -> /desk and /desk/fill routes fully responsive
    -> Flow Layout form filler works on tablets and phones
    -> Touch-friendly: larger tap targets, swipe between form sections
    -> Camera integration: photograph documents directly into image fields
    -> Signature pad: finger/stylus signing on touch devices
    -> Offline mode: fill form offline, auto-submit when connection restored

Design Studio — desktop only:
    -> Canvas editing requires mouse precision (not mobile-optimized)
    -> Minimum viewport: 1024px wide
    -> Tablet: read-only canvas preview, no editing

Admin Console — responsive:
    -> Dashboard and reports work on tablet
    -> User management and configuration work on tablet
    -> Not optimized for phone (admin tasks are not mobile-first)
```

### Performance Targets (expanded)

| Metric | Target |
|--------|--------|
| AI suggestion (cache hit) | < 50 ms |
| AI suggestion (LLM call) | < 5 s (hard timeout) |
| PDF render (A4, < 20 elements) | < 3 s |
| PDF batch (100 records) | < 60 s |
| Template list page load | < 500 ms |
| Form Desk dashboard load | < 300 ms |
| Form filler load (published template) | < 1 s |
| Form submission (with validation) | < 500 ms |
| Form draft save | < 300 ms |
| Notification delivery (in-app) | < 5 s |
| Search (templates/submissions/customers) | < 500 ms |
| Audit log query (filtered) | < 2 s |
| OCR single form detection | < 15 s |
| OCR batch (10 forms) | < 3 min |

---

## Revenue Model

The two-mode architecture enables a **tiered pricing model**:

| Tier | Includes | Target Buyer | Pricing Model |
|------|----------|--------------|---------------|
| **Starter** | Design Studio (1 designer) + Form Desk (3 operators) + 100 submissions/month | Small businesses, single-branch operations | Monthly subscription |
| **Professional** | Design Studio (5 designers) + Form Desk (25 operators) + unlimited submissions + batch processing + analytics | Multi-branch businesses, mid-size banks | Annual subscription |
| **Enterprise** | Unlimited designers + operators + SSO + custom domain + API access + dedicated support + SLA | Large banks, government ministries | Custom pricing, annual contract |
| **Platform** | Enterprise + External Form Portal + Template Marketplace + custom integrations | Digital transformation initiatives | Custom pricing |

Add-on pricing:
| Add-on | Price model |
|--------|------------|
| Additional operators beyond tier limit | Per seat / month |
| OCR batch onboarding (one-time) | Per form scanned |
| Template Marketplace premium publishing | Revenue share (70/30) |
| Custom integration connector | One-time setup + monthly |
| Priority support + SLA | % of subscription |

The Studio is the **land** (sold once to the design team). The Desk is the **expand** (sold per-seat to every branch, every teller, every agent). One Studio license generates 50-200 Desk licenses in a large bank.

### Implementation status (as of 2026-06-19) — monetization is the current revenue blocker

Org onboarding is no longer the blocker: the Platform Console frontend (PC-01) is built, so platform admins can create and tier orgs through the UI. The gap has moved one layer deeper — a tier is a stored label that is neither **sellable** nor **enforced**:

- `tier_limits` lookup table exists (`migrations/039_platform_admin_console.sql`) with values: starter 10 users / 50 templates / 5 GB, professional 50 / 200 / 25, enterprise 200 / 1000 / 100, platform 1000 / 5000 / 500.
- `get_tier_limit_alerts()` fires at **≥90% of the user limit only** — it is monitoring, not a gate. Nothing blocks an org from exceeding any limit; the subscription tab is a read-only label with no upgrade/downgrade action.
- **Two mismatches to reconcile before billing:** (1) the DB Starter limit (10 users) does not match the documented Starter tier (1 designer + 3 operators = 4 users + 100 submissions/mo); (2) the **submission-volume cap** central to the Starter tier is counted for display but is not part of `tier_limits` and is not enforced anywhere.

The blocker splits into two independent halves:

- **(a) Sellable — now specified.** Feature **058-paygateway-billing** (drafted 2026-06-19, design doc [`payment-gateway-integration.md`](payment-gateway-integration.md)) adds card payment via the existing PayGateway/Stripe service so an org admin can **pay to change tier** and buy add-ons (seats, OCR batch, marketplace template). Successful payment sets `subscription_tier` server-side and makes the read-only Subscription tab actionable. Clarified scope: upgrades only (downgrades happen via platform-admin refund/reversal), full refunds only, charge in the org's default currency, zero-amount purchases skip payment. This is the "turn the label into something you can buy" half.
- **(b) Enforced — still TODO.** Blocking invites/submissions/storage when an org exceeds its `tier_limits`, and aligning the DB limit values with the documented tiers. Feature 058 deliberately leaves this out of scope; it records purchased allowances (seats, OCR credits) but does not gate on them.

**Next revenue step:** implement 058 (sellable) and, in parallel, the enforcement gates at invite + submission time (enforced) — together they turn `subscription_tier` from a label into real, monetizable, governed access.

---

## Phased Roadmap

### Phase 1 — Complete the Core Loop (3-4 months)

**Goal**: Close the design-to-desk gap. Two working product modes.

| # | Initiative | Impact | Effort | Depends On |
|---|-----------|:------:|:------:|:----------:|
| 1.1 | Mode switching UX (nav bar, role-based routing) | High | Low | — |
| 1.2 | Form Desk: Operator Dashboard (FD-01) | Critical | Medium | 1.1 |
| 1.3 | Form Desk: Form Filler with Flow Layout (FD-02) | Critical | High | 1.1 |
| 1.4 | Form Desk: PDF Preview & Print (FD-04) | Critical | Medium | 1.3 |
| 1.5 | Form Desk: Save & Resume Drafts (FD-03) | High | Medium | 1.3 |
| 1.6 | Form Desk: Submission History & Reprint (FD-05) | High | Medium | 1.4 |
| 1.7 | Template Versioning & Cloning (DS-08) | High | Medium | — |
| 1.8 | Reframe feedback as Template Feedback (DS-10) | Low | Low | — |
| 1.9 | Design Studio: new element types (signature, table) | Medium | Medium | — |
| 1.10 | Form Desk: form validation at fill time | High | Medium | 1.3 |
| 1.11 | Overlay Print Mode — full/overlay toggle, stationery scan, calibration (FD-09) | Critical | Medium | 1.4 |
| 1.12 | Reference Data Manager — list schema, entries, field binding (DS-11) | High | Medium | 1.3 |
| 1.13 | Printer profile management & calibration page | High | Low | 1.11 |

**Phase 1 deliverable**: A designer can create a template, publish it, bind reference data lists, and an operator can fill it (with lookup auto-fill), validate it, print it (full or overlay on pre-printed stationery), and find it in history. The core business loop — including the bank cheque use case — works end to end.

### Phase 2 — Enterprise Operations (4-6 months)

**Goal**: Multi-tenant, governed, scalable for large organizations.

| # | Initiative | Impact | Effort | Depends On |
|---|-----------|:------:|:------:|:----------:|
| 2.1 | Multi-tenancy: organizations, departments, branches (AC-01) | High | High | — |
| 2.1b | **Platform Admin Dashboard: org CRUD frontend (PC-01)** | High | Medium | 2.1 |
| 2.2 | Enhanced user management: invitation, bulk import, departments (AC-02) | High | Medium | 2.1 |
| 2.3 | Template approval workflow: submit -> review -> publish (AC-03) | High | Medium | 2.1 |
| 2.4 | Reviewer role and permissions | Medium | Low | 2.3 |
| 2.5 | Conditional fields & logic engine (visible_when, required_when, computed_value) | High | High | — |
| 2.6 | Customer profiles & auto-populate (FD-08) | High | Medium | 2.1 |
| 2.7 | Batch operations & print queue (FD-06) | Medium | High | 1.4 |
| 2.8 | Notification center (AC-06) | Medium | Medium | 2.1 |
| 2.9 | Analytics & reporting dashboard (AC-05) | Medium | Medium | 2.1 |
| 2.10 | Enhanced audit logging (AC-04) | Medium | Medium | 2.1 |
| 2.11 | Digital signature element type | Medium | Medium | 1.9 |
| 2.12 | Data export & import (AC-07) | Medium | Medium | 2.1 |
| 2.13 | Custom validators per org | Low | Low | 2.1 |
| 2.14 | SSO / SAML / OIDC integration | High | Medium | 2.1 |
| 2.15 | MFA (TOTP + SMS) | Medium | Medium | 2.14 |
| 2.16 | White-labeling: org logo, colors, custom domain | Medium | Medium | 2.1 |
| 2.17 | Mobile-responsive Form Desk | Medium | Medium | 1.3 |
| 2.18 | Hijri date support | Low | Low | — |
| 2.19 | Data retention policies & auto-archival | Medium | Medium | 2.10 |
| 2.20 | Operational Report Engine — pre-built reports (AC-08) | High | Medium | 2.1, 1.3 |
| 2.21 | Daily reconciliation report + auto-email | High | Low | 2.20 |
| 2.22 | Custom report builder (AC-08) | Medium | Medium | 2.20 |
| 2.23 | Scheduled reports + report archives | Medium | Medium | 2.22 |
| 2.24 | Cascading reference lists (DS-11 enhancement) | Medium | Low | 1.12, 2.5 |
| 2.25 | Signatory usage report (cross-reference: reports + reference data) | Medium | Low | 2.20, 1.12 |

**Phase 2 deliverable**: A bank with 50 branches can deploy FormCraft with SSO, department-level template isolation, approval workflows, customer profiles, batch processing, analytics, operational reports (daily reconciliation, transaction registers, beneficiary reports), and overlay printing on pre-printed cheque books. Enterprise-ready.

### Phase 3 — Platform & Ecosystem (6-12 months)

**Goal**: Network effects, external-facing capabilities, integration ecosystem.

| # | Initiative | Impact | Effort | Depends On |
|---|-----------|:------:|:------:|:----------:|
| 3.1 | OCR onboarding pipeline: batch import wizard (DS-09) | High | Medium | — |
| 3.2 | External form portal: public URLs for forms (EXT-01) | High | High | 2.1 |
| 3.3 | Webhook engine (AC-07) | High | Medium | 2.1 |
| 3.4 | API keys & external API access (AC-07) | High | Medium | 2.1 |
| 3.5 | Template marketplace (EXT-02) | Medium | High | 2.1 |
| 3.6 | AI batch field analysis & quality scoring (DS-04) | Medium | Medium | — |
| 3.7 | Scheduled batch jobs (cron-based recurring PDF generation) | Medium | Medium | 2.7 |
| 3.8 | Integration connectors (core banking, CRM, DMS) | High | High | 3.3, 3.4 |
| 3.9 | Report SFTP/cloud export + data warehouse integration | Medium | Medium | 2.23 |
| 3.10 | Print Layout view in Form Desk (WYSIWYG fill) | Medium | High | 1.3 |
| 3.11 | Split View in Form Desk (form + live PDF preview) | Medium | Medium | 3.10 |
| 3.12 | Offline form filling with sync | Medium | High | 1.3 |
| 3.13 | Additional language support (French, Urdu) | Low | Medium | — |
| 3.14 | SOC 2 compliance artifacts | Medium | Medium | 2.10, 2.19 |
| 3.15 | Template version diff view | Low | Medium | 1.7 |

**Phase 3 deliverable**: FormCraft is a platform — external citizens fill forms online, banks auto-generate batches on schedule, templates are shared across organizations in a marketplace, and FormCraft integrates with core banking systems via API. Full ecosystem.

---

## Implementation Status vs. Vision (as of 2026-05-24)

### Phase 1 Progress: Core Loop

| # | Initiative | Vision Status | Implemented As | Verified |
|---|-----------|:------------:|----------------|:--------:|
| 1.1 | Mode switching UX | ✅ DONE | F15 — `/users/me` returns role + mode prefs | 200 |
| 1.2 | Operator Dashboard (FD-01) | ✅ DONE | F16 — `/desk/dashboard` with pins | 200 |
| 1.3 | Form Filler (FD-02) | ✅ DONE | F17 — `/desk/fill/:id` returns published template | 200 |
| 1.4 | PDF Preview & Print (FD-04) | ✅ DONE | F06 — `/pdf/preview/:id` + `/pdf/render/:id` | 200 |
| 1.5 | Save & Resume Drafts (FD-03) | ✅ DONE | Migration 018 — drafts table created | — |
| 1.6 | Submission History (FD-05) | ✅ DONE | F18 — `/submissions` | 200 |
| 1.7 | Template Versioning & Cloning (DS-08) | ✅ DONE | F19 — clone 201, version 200 | 201/200 |
| 1.8 | Template Feedback (DS-10) | ✅ DONE | F20 — `/admin/template-feedback` | 200 |
| 1.9 | New element types (DS-03) | ✅ DONE | F21 — signature + table types | 201 |
| 1.10 | Form validation at fill time | ✅ DONE | F22 — `visible_when`, `required_when`, `computed_value` | — |
| 1.11 | Overlay Print Mode (FD-09) | ✅ DONE | F23 — print settings + printer profiles | 200 |
| 1.12 | Reference Data Manager (DS-11) | ✅ DONE | F24 — `/reference-lists` | 200 |
| 1.13 | Printer profile management | ✅ DONE | F23 — `/printer-profiles` | 200 |

**Phase 1: 13/13 initiatives implemented.** The core design-to-desk loop is complete.

### Phase 2 Progress: Enterprise Operations

| # | Initiative | Vision Status | Notes |
|---|-----------|:------------:|-------|
| 2.1 | Multi-tenancy (AC-01) | ✅ DONE | F25 — orgs, depts, branches, RLS |
| 2.1b | **Platform Admin Dashboard (PC-01)** | ✅ DONE | Backend (`/api/organizations` 5 endpoints, `require_platform_admin()`) + frontend (`features/platform`: layout, dashboard, org list/create/detail, profile/subscription/stats/users tabs, `PlatformAdminGuard`, routed `admin/platform`). **New gap surfaced: subscription tier is read-only display + 90% user-count alert only — no enforcement, no upgrade/downgrade, submission cap untracked, and `tier_limits` values (starter=10 users) don't match the documented Starter tier (4 users / 100 submissions)** |
| 2.2 | User management (AC-02) | ✅ PARTIAL | Invitations done; bulk import not yet |
| 2.5 | Conditional fields & logic | ✅ DONE | F22 — 3 conditional columns on elements |
| 2.3-2.4 | Approval workflow + Reviewer role | ⚠️ SPECIFIED | Spec 028-approval-workflow |
| 2.6 | Customer profiles (FD-08) | ⚠️ SPECIFIED | Spec 030-customer-profiles |
| 2.7 | Batch operations (FD-06) | ⚠️ SPECIFIED | Spec 036-batch-operations |
| 2.8 | Notification center (AC-06) | ⚠️ SPECIFIED | Spec 029-notification-center |
| 2.9 | Analytics (AC-05) | ⚠️ SPECIFIED | Spec 027-analytics-reporting |
| 2.12 | Data export & import (AC-07) | ⚠️ SPECIFIED | Spec 032-data-export-integration |
| 2.13 | Custom validators | ⚠️ SPECIFIED | Spec 048-custom-locale-validators |
| 2.14-2.15 | SSO + MFA | ⚠️ SPECIFIED | Spec 042-enterprise-sso-mfa |
| 2.17 | Mobile-responsive Form Desk | ⚠️ SPECIFIED | Spec 047-mobile-offline-desk |
| 2.19 | Data retention policies | ⚠️ SPECIFIED | Spec 044-data-retention-archival |
| 2.20-2.25 | Operational Report Engine | ⚠️ SPECIFIED | Spec 033-operational-reports |
| 2.11 | Digital signatures | ⚠️ SPECIFIED | Spec 046-digital-signatures |
| **Extra** | Granular template permissions | ⚠️ SPECIFIED | Spec 043-granular-template-permissions |
| **Extra** | Connector framework | ⚠️ SPECIFIED | Spec 049-connector-framework |
| **Extra** | External form portal | ⚠️ SPECIFIED | Spec 034-external-form-portal |
| **Extra** | Platform admin console | ⚠️ SPECIFIED | Spec 039-platform-admin-console |
| **Extra** | Batch OCR onboarding | ⚠️ SPECIFIED | Spec 045-batch-ocr-onboarding |
| **Extra** | Dual-theme UI shell | ✅ PARTIAL | Specs 041/050/052–053: new-theme routes live, real data, cross-theme filler |

### Phase 3 Progress: Platform & Ecosystem

| # | Initiative | Vision Status | Notes |
|---|-----------|:------------:|-------|
| 3.1 | OCR onboarding pipeline (DS-09) | ✅ PARTIAL | F26 single-form done; batch wizard not yet |
| 3.2-3.15 | External portal, marketplace, webhooks, API keys, etc. | ❌ TODO | |

### Summary Metrics

| Metric | Count |
|--------|-------|
| Total spec directories | 58 (001–058) |
| Fully implemented (001–026) | 22 |
| Partially implemented (001–026) | 1 (F09 — performance caching) |
| Awaiting external credentials | 2 (F05 — AWS Bedrock, F26 — Azure OCR) |
| Specified, pending implementation | ~23 (specs 027–049, not all verified in code) |
| Partially live (new theme + filler) | 4 (specs 041, 050, 052–053: frontend routes running) |
| Database migrations applied | 28 (001–028, as of last full validation) |
| RLS policies fixed | 10 (across migrations 025–027) |
| Bugs fixed during validation | 9 |
| Backend API routes | 25 route files |
| Verified API endpoints | 40+ |

---

## Final Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────────────────────────┐
│                                    FormCraft Platform                                       │
├─────────────────────┬─────────────────────┬───────────────────────┬────────────────────────┤
│   DESIGN STUDIO     │     FORM DESK       │   ADMIN CONSOLE       │  PLATFORM CONSOLE ★★  │
│                     │                     │                       │  (is_platform_admin)   │
│  Template Library   │  Operator Dashboard │  Org Settings         │                        │
│  Canvas Editor      │  Form Filler        │  User Management      │  Org List & Create     │
│  AI Suggestions     │  Drafts             │  Template Governance  │  Org Detail & Config   │
│  OCR Import         │  Print & Submit     │  Approval Workflows   │  Subscription Mgmt     │
│  Tafqeet Config     │  Overlay Print ★    │  Audit & Compliance   │  Platform Overview     │
│  PDF Preview        │  Printer Calibrate ★│  Analytics            │  Cross-Org User View   │
│  Version Control    │  History & Reprint  │  Operational Reports ★│                        │
│  Template Feedback  │  Batch Queue        │  Report Builder ★     │  Backend: ✅ EXISTS    │
│  Ref Data Manager ★ │  Customer Profiles  │  Notification Center  │  Frontend: ✅ BUILT    │
│                     │  Quick Fill         │  Data Export & Import │                        │
│  By: Designers      │  Ref Data Lookup ★  │  Webhooks & API Keys  │  By: Platform Admins   │
│  When: Occasionally │                     │  Custom Validators    │  When: Rare            │
│                     │  By: Operators      │                       │                        │
│                     │  When: All day      │  By: Admins           │  Route: /platform/*    │
│                     │                     │  When: Periodic       │  Guard: PlatformAdmin  │
├─────────────────────┴─────────────────────┴───────────────────────┴────────────────────────┤
│                        EXTERNAL / PUBLIC                                                    │
│  Public Form Portal (anonymous or OTP-verified submissions)                                │
│  Template Marketplace (cross-org sharing and purchasing)                                    │
│  REST API + Webhooks (integration with core banking, CRM, DMS)                             │
├────────────────────────────────────────────────────────────────────────────────────────────┤
│                                   SHARED SERVICES                                          │
│  Auth (JWT + SSO + MFA) | i18n (AR/EN + Hijri) | PDF Engine (WeasyPrint)                  │
│  Validation (Arabic + Custom) | AI (AWS Bedrock) | Tafqeet | Notifications                │
│  Audit Logging | RLS + Encryption | Performance + Caching | File Storage                  │
├────────────────────────────────────────────────────────────────────────────────────────────┤
│                                   INFRASTRUCTURE                                           │
│  Angular 19 | FastAPI | Supabase (PostgreSQL + Auth + Storage + Realtime)                  │
│  AWS Bedrock | Azure Document Intelligence | WeasyPrint | Bunny Containers                │
└────────────────────────────────────────────────────────────────────────────────────────────┘
```

```
Target state flow:

    [Scan & Digitize] -> [Design & Iterate] -> [Approve & Publish] -> [Fill & Validate] -> [Print & Archive] -> [Report & Analyze]
         ^                      ^                      ^                      ^                    |                    |
         |                      |                      |                      |                    v                    v
    (OCR pipeline)       (AI assist +            (review workflow       (Form Desk +          (full print OR      (transaction register,
                          versioning +            + governance)          ref data lookup +      overlay on           daily reconciliation,
                          ref data mgr ★)                                customer data)         pre-printed          beneficiary reports,
                                                                                               stationery ★)        signatory usage ★)
                                                                              |
                                                                              v
                                                                     [External Portal]
                                                                     [API Integration]
                                                                     [Marketplace]
```
