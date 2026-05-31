# Feature Specification: New Theme Desk Live Data Integration

**Feature Branch**: `050-new-theme-desk-data`  
**Created**: 2026-05-31  
**Status**: Draft  
**Input**: Replace all hardcoded mock data in the new-theme desk (/ui/desk) with real API data using existing services

## Clarifications

### Session 2026-05-31

- Q: Does "real-time KPIs" mean auto-refreshing or fetch-on-load? → A: Fetch-on-load — fresh data on each page navigation, no background polling.
- Q: How many pinned/frequent templates should the dashboard display? → A: Maximum 6 templates displayed.
- Q: Should the form filler auto-save on navigation away? → A: Yes — auto-save current state as draft when the operator navigates away, preventing data loss.
- Q: Should hardcoded mock data be deleted or kept as fallback? → A: Delete all mock data entirely from components — no fallback arrays, no feature flags.
- Q: How many recent activity items should the dashboard show? → A: Show the 10 most recent items with a "View All" link to the full history page.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Dashboard Shows Real KPIs (Priority: P1)

As an operator opening the new-theme desk dashboard, I see real-time key performance indicators reflecting my actual work — today's submission count, pending drafts count, and active templates count — so I can gauge my workload at a glance.

**Why this priority**: KPIs are the first thing operators see on the dashboard. Displaying fake numbers erodes trust in the entire interface and defeats the purpose of a dashboard.

**Independent Test**: Log in as an operator, navigate to /ui/desk. Verify KPI cards show numbers matching the actual counts returned by the backend. Submit a new form and confirm the KPI updates on next dashboard visit.

**Acceptance Scenarios**:

1. **Given** an operator with 5 submissions today, 3 pending drafts, and 12 active templates, **When** they open the dashboard, **Then** KPI cards display "5", "3", and "12" respectively.
2. **Given** an operator with zero submissions today, **When** they open the dashboard, **Then** the submissions KPI displays "0" (not a placeholder or mock value).
3. **Given** the backend is temporarily unreachable, **When** the dashboard loads, **Then** KPI cards show a loading indicator followed by a user-friendly error state, not hardcoded fallback numbers.

---

### User Story 2 - Recent Activity From Real Submissions (Priority: P1)

As an operator, I see my recent submission activity (form name, customer, status, reference number, timestamp) on the dashboard, drawn from actual submission history, so I can track what I have processed recently.

**Why this priority**: The activity feed is the primary operational view. Without real data, operators cannot use the new theme for daily work.

**Independent Test**: Submit several forms via the classic desk, then navigate to /ui/desk and verify the activity table shows those submissions with correct details.

**Acceptance Scenarios**:

1. **Given** an operator who submitted 3 forms in the last hour, **When** they view the dashboard, **Then** the recent activity table lists those 3 submissions with correct form names, customer names, statuses, reference numbers, and timestamps.
2. **Given** an operator with no submissions, **When** they view the dashboard, **Then** the activity section shows an empty state message (e.g., "No recent activity").
3. **Given** submissions exist in multiple statuses (approved, pending, rejected), **When** the dashboard loads, **Then** each submission displays its correct status with appropriate visual indicator.

---

### User Story 3 - Drafts Panel From Real Drafts (Priority: P1)

As an operator, I see my actual in-progress drafts on the dashboard, so I can resume incomplete form submissions without losing work.

**Why this priority**: Drafts represent uncommitted work. Showing mock drafts prevents operators from finding and resuming their real in-progress forms.

**Independent Test**: Start filling a form, save as draft, then navigate to /ui/desk. Verify the draft appears in the drafts panel with correct form name and timestamp.

**Acceptance Scenarios**:

1. **Given** an operator with 2 saved drafts, **When** they open the dashboard, **Then** the drafts panel lists both drafts with form name, customer name, and last-modified time.
2. **Given** an operator clicks on a draft in the panel, **When** the draft opens, **Then** it navigates to the form filler pre-loaded with the saved draft data.
3. **Given** an operator with no drafts, **When** they view the dashboard, **Then** the drafts panel shows an empty state message.

---

### User Story 4 - Pinned/Frequently Used Templates (Priority: P2)

As an operator, I see my most frequently used or pinned form templates on the dashboard, so I can quickly start filling the forms I use every day.

**Why this priority**: Quick access to common forms improves daily efficiency, but operators can still access all templates through the full template list.

**Independent Test**: As an operator who has submitted forms using certain templates multiple times, verify those templates appear in the pinned/frequent section on the dashboard.

**Acceptance Scenarios**:

1. **Given** an operator who frequently uses 3 templates, **When** they view the dashboard, **Then** those 3 templates appear in the pinned forms section with correct names and template codes.
2. **Given** an operator clicks a pinned template, **When** the action completes, **Then** they are navigated to the form filler for that template.
3. **Given** a newly created operator with no submission history, **When** they view the dashboard, **Then** the pinned section shows published templates as suggestions or an empty state.

---

### User Story 5 - Form Filler With Real Template Structure (Priority: P1)

As an operator filling a form via the new theme, I see the actual template structure (sections, fields, field types, validations) loaded from the system, and I can fill and submit the form with full validation, conditional logic, and auto-fill support.

**Why this priority**: The form filler is the core operational tool. Without real template rendering, the new theme cannot be used for actual work.

**Independent Test**: Navigate to /ui/desk/fill/{templateId}. Verify the form displays real sections and fields matching the template definition. Fill in fields and verify validation rules, conditional visibility, and tafqeet (number-to-words) work correctly. Submit and verify the submission is saved.

**Acceptance Scenarios**:

1. **Given** a published template with 3 sections and 10 fields, **When** an operator opens it in the new-theme filler, **Then** all 3 sections and 10 fields render with correct labels, types, and ordering.
2. **Given** a template with required fields, **When** the operator tries to submit with empty required fields, **Then** validation errors display for each missing field.
3. **Given** a template with conditional fields (e.g., show field B only when field A equals "yes"), **When** the operator changes field A, **Then** field B appears or hides accordingly.
4. **Given** a numeric field with tafqeet enabled, **When** the operator enters a number, **Then** the Arabic number-to-words representation appears.
5. **Given** an operator selects a customer, **When** the customer has profile data matching form fields, **Then** those fields auto-fill with the customer's data.

---

### User Story 6 - Customers Page With Real Data (Priority: P2)

As an operator, I can browse and search real customer profiles from the customers page, so I can look up customer information and initiate forms for specific customers.

**Why this priority**: Customer data supports form filling but operators can still fill forms without the customer lookup page.

**Independent Test**: Navigate to /ui/desk/customers. Verify the list shows real customer records from the system. Search for a customer by name and verify results update.

**Acceptance Scenarios**:

1. **Given** 50 customer profiles exist, **When** an operator opens the customers page, **Then** the list displays real customer names, IDs, and key details with pagination.
2. **Given** an operator searches for "محمد", **When** results load, **Then** only customers whose names match the search appear.
3. **Given** an operator clicks on a customer, **When** the detail view opens, **Then** it shows the customer's real profile data and submission history.

---

### Edge Cases

- What happens when a template is unpublished after an operator pinned it? The pinned forms section should exclude unpublished templates and not show broken entries.
- What happens when a draft references a template that has been updated to a new version? The system should notify the operator and offer to reload with the latest template version.
- What happens when the operator's session expires while filling a form? Since auto-save is always active, the most recent state will already be persisted as a draft. The system redirects to login, and the operator can resume from the auto-saved draft after re-authentication.
- What happens when the backend returns an empty dataset for all sections? Each dashboard section should display an appropriate empty state, not a blank area.
- What happens when the operator has a role that restricts access to certain templates? The dashboard and form filler should only show templates the operator is authorized to access.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Dashboard MUST display KPI counts (today's submissions, pending drafts, active templates) fetched fresh from the backend on each page load (no background polling or auto-refresh).
- **FR-002**: Dashboard MUST display the 10 most recent submission activities, including form name, customer name, status, reference number, and timestamp, ordered by most recent first, with a "View All" link to the full history page.
- **FR-003**: Dashboard MUST display the operator's current drafts with form name, customer name, progress indicator, and last-modified timestamp.
- **FR-004**: Dashboard MUST display up to 6 of the operator's pinned templates (via the existing pin/unpin API), filtered to published-only, allowing one-click navigation to start filling that form.
- **FR-005**: Form filler MUST load the real template structure (sections, fields, field types, labels, ordering) from the published template definition.
- **FR-006**: Form filler MUST apply all field validations (required, pattern, min/max, custom validators) and display inline validation errors.
- **FR-007**: Form filler MUST evaluate conditional logic rules to show/hide fields and sections dynamically based on field values.
- **FR-008**: Form filler MUST support auto-fill from selected customer profile data.
- **FR-009**: Form filler MUST support tafqeet (Arabic number-to-words conversion) for enabled numeric fields.
- **FR-010**: Form filler MUST allow saving in-progress forms as drafts and resuming them later. The form MUST auto-save the current state as a draft when the operator navigates away, preventing accidental data loss.
- **FR-011**: Form filler MUST submit completed forms and create a submission record.
- **FR-012**: Customers page MUST display real customer profiles with search and pagination.
- **FR-013**: All dashboard sections MUST show a loading indicator while data is being fetched.
- **FR-014**: All dashboard sections MUST show an appropriate empty state when no data is available.
- **FR-015**: All components MUST support both RTL (Arabic) and LTR (English) layouts without visual regressions.
- **FR-016**: All components MUST respect the user's role-based permissions, showing only authorized templates and data.
- **FR-017**: All hardcoded mock data arrays and placeholder values MUST be removed entirely from components — no fallback mock data, no feature flags for mock mode.

### Key Entities

- **Dashboard KPI**: Aggregated counts (submissions today, pending drafts, active templates) representing the operator's current workload snapshot.
- **Pinned Template**: A template frequently used by the operator, displayed for quick access. Linked to the operator's usage history or explicit pinning preference.
- **Activity Entry**: A recent submission record showing form name, customer, status, reference, and timestamp.
- **Draft**: An in-progress form submission that has been saved but not yet submitted, with its associated template and partial field data.
- **Customer Profile**: A record containing customer identity and details, used for auto-filling form fields and associating submissions.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All dashboard sections (KPIs, activity, drafts, pinned forms) display data from real backend sources with zero hardcoded mock values.
- **SC-002**: Operators can complete a full form submission workflow (select template, fill fields, validate, submit) entirely within the new theme without falling back to the classic theme.
- **SC-003**: Dashboard data loads and renders within 3 seconds on a standard connection.
- **SC-004**: Form validation errors appear inline within 500 milliseconds of the user moving to the next field.
- **SC-005**: Auto-fill from customer profile populates matching fields within 1 second of customer selection.
- **SC-006**: 100% of conditional field visibility rules behave identically to the classic theme form filler.
- **SC-007**: Dashboard correctly handles empty states for all sections (zero submissions, zero drafts, zero pinned templates) without displaying broken UI.
- **SC-008**: All content displays correctly in both Arabic (RTL) and English (LTR) with no layout breakage.

## Form Filler Feature Specification (Cross-Theme)

### Overview

The Form Filler is the primary operational tool for filling and submitting forms. It is implemented in two variations:

1. **Classic Desk**: `formcraft-frontend/src/app/features/desk/fill/fill.component.ts` — Full-featured implementation with offline support, auto-save intervals, and extended features
2. **New Theme**: `formcraft-frontend/src/app/features/ui-redesign/desk/form-filler.component.ts` — Streamlined standalone component implementation

Both implementations share the same underlying data models and services, ensuring feature parity and consistent user experience.

### Data Sources & Real Data Binding

All Form Filler data is fetched from backend APIs at runtime. There is **zero hardcoded mock data** in either implementation:

#### Template Loading (Real Data)
- **API**: `FormFillerService.getTemplate(templateId: string): Observable<FillTemplate>`
- **Data Structure**: `FillTemplate` contains:
  - Template metadata: `id`, `name`, `version`, `is_published`, `country`, `is_deprecated`
  - Pages: Array of `TemplatePage` objects
  - Elements: Array of `TemplateElement` objects with full field definitions
- **Example Flow**: 
  1. User clicks "Open Template" or navigates to `/desk/fill/{templateId}`
  2. Component calls `FormFillerService.getTemplate(templateId)`
  3. Backend returns complete template structure from database
  4. Component dynamically builds form from template structure
  5. No mock data used at any point

#### Draft Loading (Real Data)
- **API**: `DraftService.getDraft(draftId: string): Observable<Draft>`
- **Data Structure**: `Draft` contains:
  - `id`, `template_id`, `template_version`
  - `field_values`: Object mapping field keys to saved values
  - `created_at`, `updated_at`
  - Metadata: customer info, operator info, progress percentage
- **Example Flow**:
  1. User navigates to `/desk/fill/{templateId}?draftId={draftId}` or resumes from drafts panel
  2. Component calls `DraftService.getDraft(draftId)`
  3. Backend returns saved field values from database
  4. Component populates reactive form with actual saved data
  5. If draft template version differs from published version, warning displayed

#### Customer Profile Auto-Fill (Real Data)
- **API**: `CustomerService.getAutoPopulateData(customerId: string, templateId: string): Observable<AutoFillMapping>`
- **Data Structure**: `AutoFillMapping` contains field-to-customer mappings (e.g., `first_name` → customer first name)
- **Example Flow**:
  1. User selects customer from customer picker dialog
  2. Component calls `CustomerService.getAutoPopulateData(customerId, templateId)`
  3. Backend returns mappings for fields that exist in both template and customer profile
  4. Component calls `AutoFillService.executeAutoFill(mappings, formGroup)`
  5. Form fields auto-populate with actual customer data (not mock defaults)

#### Submission Creation (Real Data)
- **API**: `SubmissionService.submit(templateId: string, version: number, fieldValues: object): Observable<SubmissionResponse>`
- **Data Structure**: `SubmissionResponse` contains:
  - `id`: Unique submission identifier
  - `reference_number`: Human-readable reference
  - `status`: Submission status from backend
  - Links to view submission in history
- **Example Flow**:
  1. User completes form and clicks "Submit"
  2. Component validates all visible required fields
  3. Component calls `SubmissionService.submit(templateId, version, formValues)`
  4. Backend validates, creates submission record, returns confirmation
  5. Component navigates to dashboard, shows success confirmation

### Field Type System

The Form Filler supports dynamic rendering of all field types defined in the template:

#### Text Input Fields
- **Data Source**: `TemplateElement` with `type: "text"`
- **Binding**: `formGroup.get(element.key).valueChanges` → real user input
- **Validation**: Regex pattern from `element.validation.pattern`, required constraint from `element.required`
- **Rendering**: Dynamic label from `element.label_ar` or `element.label_en` (based on language service)
- **Example**: Customer name field displays Arabic label "اسم العميل", accepts text input, validates against name pattern

#### Number Input Fields
- **Data Source**: `TemplateElement` with `type: "number"`
- **Binding**: `formGroup.get(element.key).valueChanges` → numeric value
- **Validation**: `min`, `max` constraints from `element.validation`, required constraint
- **Tafqeet Support**: If `element.tafqeet_enabled === true`, component subscribes to valueChanges and calls `FillerTafqeetService.compute(value)` to display Arabic number-to-words representation
- **Example**: Amount field accepts "12345" and displays "اثنا عشر ألف وثلاثمائة وخمسة وأربعون" (Arabic tafqeet)

#### Date Input Fields
- **Data Source**: `TemplateElement` with `type: "date"`
- **Binding**: `formGroup.get(element.key).valueChanges` → ISO date string
- **Validation**: Date format, optional date range constraints
- **Rendering**: Browser date picker with locale-aware formatting
- **Example**: Birth date field accepts date input, validates against logical date constraints

#### Select/Dropdown Fields
- **Data Source**: `TemplateElement` with `type: "select"` and `options` array
- **Options Format**: Array of `{ value: string, label_ar: string, label_en: string }`
- **Binding**: `formGroup.get(element.key).valueChanges` → selected option value
- **Validation**: Value must be from available options list
- **Rendering**: Dynamic label from `element.label_ar` or `element.label_en`, options from `element.options`
- **Example**: Branch selection field displays "اختر الفرع" label, populated with actual branches from database

#### Checkbox Fields
- **Data Source**: `TemplateElement` with `type: "checkbox"`
- **Binding**: `formGroup.get(element.key).valueChanges` → boolean value
- **Validation**: If required, user must check the box
- **Rendering**: Checkbox with associated label text
- **Example**: "I agree to terms" checkbox requires explicit user action

#### Textarea Fields
- **Data Source**: `TemplateElement` with `type: "textarea"`
- **Binding**: `formGroup.get(element.key).valueChanges` → multi-line text
- **Validation**: Optional length constraints, pattern validation
- **Rendering**: Multi-line text input with appropriate styling
- **Example**: Comments field for customer remarks

#### Signature Fields
- **Data Source**: `TemplateElement` with `type: "signature"`
- **Binding**: `formGroup.get(element.key).valueChanges` → signature data (canvas data or image)
- **Validation**: If required, signature must be provided
- **Rendering**: Signature pad or image upload (depending on implementation)
- **Example**: Form signature field displays signature capture interface

### Validation System (Real Data)

All validation rules are loaded from the template definition and applied dynamically:

#### Validation Types
1. **Required Fields**: Enforced via Angular `Validators.required` when `element.required === true`
2. **Pattern Validation**: Applied from `element.validation.pattern` using regex matching
3. **Min/Max Constraints**: Applied from `element.validation.min` and `element.validation.max` for numbers and strings
4. **Custom Validators**: Loaded from `ValidationService` based on field type and country-specific rules
5. **Custom Rules**: Any field-specific validation logic stored in `element.validation.custom_rule`

#### Validation Flow
1. Component loads template via `FormFillerService.getTemplate()`
2. For each element, component extracts validation rules
3. Component calls `ValidationService.getValidatorFn(element)` to load custom validators
4. Component applies validators to form control: `this.fb.control(value, validators)`
5. As user types, reactive form validates in real-time
6. Invalid fields display inline error messages: "This field is required" or specific validation error

#### Error Display
- Errors only shown after user touches field (`.touched` state)
- Inline error message appears below field
- Error summary panel shows all current validation errors with field names
- Form submission blocked if any visible required field is invalid

### Conditional Logic (Real Data)

Field visibility and requirement are dynamically evaluated based on other field values:

#### Conditional Element Structure
- **Data Source**: `element.visible_when` and `element.required_when` contain condition expressions
- **Format**: Expression rules like `"field_a == 'yes' AND field_b > 100"`
- **Evaluation**: `ConditionEngineService` evaluates expressions at runtime

#### Visibility Conditions
1. Component initializes `ConditionEngineService` with all elements and form group
2. Service subscribes to form value changes
3. On each form change, service re-evaluates all `visible_when` expressions
4. Service emits `visibilityChanged$` observable with updated set of visible field keys
5. Component iterates template fields and only renders those in visible set
6. Hidden fields are excluded from form validation

#### Requirement Conditions
1. Service evaluates all `required_when` expressions
2. Service emits `requiredChanged$` observable with updated set of required field keys
3. Component updates form control validators dynamically
4. Example: "Phone number" field becomes required only when `contact_method == 'phone'`

#### Example Scenario
- Template has field "Account Type" (select: Individual/Corporate) and field "Company Name" (text)
- "Company Name" has `visible_when: "Account_Type == 'Corporate'"`
- User selects "Individual" → "Company Name" field hidden
- User changes to "Corporate" → "Company Name" field appears with required validation

### Tafqeet Integration (Real Data)

Arabic number-to-words conversion for numeric fields:

#### Tafqeet Configuration
- **Source**: `element.tafqeet_enabled` boolean flag in template element
- **Applies To**: Numeric fields where `element.type == "number"` and `tafqeet_enabled === true`

#### Tafqeet Flow
1. Component loads template and identifies fields with `tafqeet_enabled === true`
2. For each tafqeet field, component subscribes to its `valueChanges`
3. On value change, component calls `FillerTafqeetService.compute(value, rules)`
4. Service returns Arabic number-to-words string
5. Component displays tafqeet result below numeric field
6. Example: User enters "1234" → tafqeet displays "ألف ومائتان وأربعة وثلاثون"

### Auto-Fill from Customer (Real Data)

When a customer is selected, matching form fields auto-populate with customer profile data:

#### Auto-Fill Configuration
- **Source**: Template element field mapping to customer profile fields
- **Example Mapping**: Template field `first_name` maps to customer profile field `given_name`

#### Auto-Fill Flow
1. User opens customer picker dialog (displayed in form header)
2. User searches and selects a customer from list
3. Component calls `CustomerService.getAutoPopulateData(customerId, templateId)`
4. Backend returns mapping of template field keys → customer values
5. Component calls `AutoFillService.executeAutoFill(mappings, formGroup)`
6. Service populates matching form controls with customer data
7. Form fields update with real customer profile information
8. User can override any auto-filled values
9. Example: Selecting customer "فاطمة القحطاني" auto-fills first name, phone, email if they exist in template

### Draft Auto-Save & Resume (Real Data)

Forms are automatically saved as drafts when the user navigates away, allowing resumption later:

#### Auto-Save Mechanism
- **Trigger**: User navigates away from form (via router navigation or page close)
- **Data Saved**: Complete current form values object
- **Metadata Saved**: Template ID, version, timestamp, customer reference
- **Implementation**:
  - Classic desk: `setInterval()` every 10 seconds, or on `ngOnDestroy`
  - New theme: `ngOnDestroy` when user navigates away
  - Both call `DraftService.saveDraft()` or `DraftService.updateDraft()`

#### Draft Loading
1. User resumes from drafts panel or navigates to `/desk/fill/{templateId}?draftId={draftId}`
2. Component loads both template and draft in parallel
3. Component populates form with saved field values
4. If draft template version differs from published version:
   - Component shows warning snackbar
   - Offers to reload with latest template version
   - User can choose to continue with saved structure or reload

#### Draft Persistence
- **Storage**: Supabase `drafts` table
- **Fields**: `id`, `operator_id`, `template_id`, `template_version`, `field_values` (JSON), `customer_id`, `created_at`, `updated_at`
- **Retrieval**: `DraftService.getDraft(draftId)` returns saved draft data

### Form Submission (Real Data)

Completed forms create submission records in the backend:

#### Submission Process
1. User fills form completely and clicks "Submit" button
2. Component validates all visible required fields
3. If validation fails, user sees inline error messages
4. If validation passes, component calls `SubmissionService.submit(templateId, version, fieldValues)`
5. Backend creates submission record with:
   - Submission ID and reference number
   - Operator ID
   - Template ID and version
   - Field values (stored as JSON)
   - Customer reference (if auto-filled)
   - Submission status (initial state based on template workflows)
   - Timestamp
6. Component displays success message
7. Component navigates back to dashboard
8. Draft record is deleted or archived

### Theme-Specific Implementations

#### Classic Desk (`fill.component.ts`)

**Features**:
- Full template and draft support
- Auto-save with 10-second interval
- Offline sync support via `OfflineSyncService`
- Version warning dialog for template updates
- Feedback dialog for template ratings
- Print dialog for PDF generation
- Error summary component
- Clone submission feature (populate from previous submission)
- Deprecated template warning banner
- Extended toolbar with print, save, feedback actions

**Services Injected**:
- `FormFillerService` — Template loading
- `DraftService` — Draft save/load with auto-save intervals
- `SubmissionService` — Form submission
- `ValidationService` — Field validation rules
- `FillerTafqeetService` — Number-to-words conversion
- `ConditionEngineService` — Conditional visibility/required logic
- `AutoFillService` — Customer profile auto-fill
- `OfflineSyncService` — Offline submission queue
- `HistoryService` — Cloning from previous submissions
- `TranslateService` — i18n support

**Data Binding**: All data fetched from real APIs; no mock data

#### New Theme (`form-filler.component.ts`)

**Features**:
- Streamlined template and draft support
- Auto-save on navigation away (ngOnDestroy)
- No offline support (simplified for UI redesign phase)
- Customer picker dialog with search
- Completion progress bar
- Side panel with section navigation
- Inline validation with error messages
- Real-time visibility/required condition evaluation

**Services Injected**:
- `FormFillerService` — Template loading
- `DraftService` — Draft save/load
- `SubmissionService` — Form submission
- `ValidationService` — Field validation
- `ConditionEngineService` — Conditional logic
- `AutoFillService` — Customer auto-fill (deferred)
- `FillerTafqeetService` — Tafqeet (deferred)
- `LanguageService` — Language switching

**Data Binding**: All data fetched from real APIs; no mock data

### Field Type Support Matrix

| Field Type | Classic | New Theme | Validation | Tafqeet | Auto-Fill |
|------------|---------|-----------|-----------|---------|-----------|
| text       | ✓       | ✓         | ✓         | ✗       | ✓         |
| number     | ✓       | ✓         | ✓         | ✓       | ✓         |
| date       | ✓       | ✓         | ✓         | ✗       | ✓         |
| select     | ✓       | ✓         | ✓         | ✗       | ✓         |
| checkbox   | ✓       | ✓         | ✓         | ✗       | ✗         |
| textarea   | ✓       | ✓         | ✓         | ✗       | ✓         |
| signature  | ✓       | ✓         | ✓         | ✗       | ✗         |

### Data Flow Diagram

```
User Action
    ↓
Navigation to /desk/fill/{templateId}
    ↓
    ├─→ FormFillerService.getTemplate(templateId)
    │   ↓
    │   Backend Database
    │   ↓
    │   FillTemplate (real structure)
    │
    └─→ [Optional] DraftService.getDraft(draftId)
        ↓
        Backend Database
        ↓
        Draft (real saved values)
    ↓
Component.buildFormFromTemplate(template)
    ↓
Reactive FormGroup created with validators
    ↓
ConditionEngineService.initialize(elements, formGroup)
    ↓
Template renders with real sections, fields, values
    ↓
User Interaction
    ├─→ Fills fields (formGroup.valueChanges → real user input)
    ├─→ Validation applied (inline error messages)
    ├─→ Conditions evaluated (fields show/hide based on values)
    └─→ Tafqeet computed (if enabled for field)
    ↓
User Clicks Submit
    ↓
Validation Check
    ├─→ Invalid → Show errors, prevent submission
    └─→ Valid → Submit
        ↓
        SubmissionService.submit(templateId, version, fieldValues)
        ↓
        Backend Creates Submission Record
        ↓
        Success Response
        ↓
        Component shows success, navigates to dashboard
```

## Assumptions

- All required backend APIs already exist and are used by the classic desk. No new backend endpoints are needed.
- The new theme's visual design and layout will be preserved — this feature only replaces data sources, not the UI structure.
- "Pinned templates" use the existing `DeskService.pinTemplate()`/`unpinTemplate()` API and the `pinned` array returned by `getDashboard()`. No new backend work needed.
- The existing classic desk services can be directly imported into standalone components without modification.
- The form filler in the new theme will support the same field types and validation rules as the classic theme filler.
- Performance targets assume the same backend response times as the classic desk experiences.
- All form data (template structure, field definitions, validation rules, options lists) is loaded from the backend at runtime—no hardcoded fallbacks or mock data.
- Customer auto-fill mappings are determined by the backend API `CustomerService.getAutoPopulateData()` based on template configuration and customer profile data.
- Tafqeet computation uses the existing `FillerTafqeetService` which relies on backend rules for Arabic number formatting.
- Draft storage persists complete form state to allow resumption across sessions with template version awareness.
