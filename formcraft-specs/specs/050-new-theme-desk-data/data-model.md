# Data Model: New Theme Desk Live Data Integration

**Date**: 2026-05-31 | **Feature**: 050-new-theme-desk-data

## Overview

No new database entities or backend models are introduced. This feature reuses existing data models exposed by the classic desk services. This document maps the existing models to their usage in the new theme components.

## Existing Entities (Reused As-Is)

### DashboardData (from DeskService)

Aggregated response from `GET /desk/dashboard`.

| Field | Type | Description |
|-------|------|-------------|
| templates | TemplatesPage | Paginated list of published templates |
| recent | RecentTemplate[] | Recently used templates by operator |
| pinned | PinnedTemplate[] | Operator's pinned templates (max 6 displayed) |
| drafts | DraftResponse[] | Operator's in-progress drafts |
| notifications | NotificationItem[] | Template version update notifications |

### PinnedTemplate

| Field | Type | Description |
|-------|------|-------------|
| template_id | string | Template UUID |
| template_name | string | Display name |
| category | string | null | Template category |
| version | number | Current template version |
| is_published | boolean | Whether template is still published |
| pinned_at | string | ISO timestamp of when pinned |

### RecentTemplate

| Field | Type | Description |
|-------|------|-------------|
| template_id | string | Template UUID |
| template_name | string | Display name |
| category | string | null | Template category |
| version | number | Template version at time of use |
| last_used_at | string | ISO timestamp of last usage |

### DraftResponse (from DraftService)

| Field | Type | Description |
|-------|------|-------------|
| id | string | Draft UUID |
| template_id | string | Associated template UUID |
| template_version | number | Template version at draft creation |
| operator_id | string | Creating operator's UUID |
| org_id | string | Organization UUID |
| field_values | Record<string, any> | Saved form field values |
| completion_percent | number | Progress percentage (0-100) |
| name | string | null | Optional draft label |
| expires_at | string | ISO expiry timestamp |
| created_at | string | ISO creation timestamp |
| updated_at | string | ISO last-modified timestamp |

### SubmissionListItem (from HistoryService)

Used for the dashboard's recent activity section.

| Field | Type | Description |
|-------|------|-------------|
| id | string | Submission UUID |
| reference_number | string | Human-readable reference (e.g., "REF-20260531-001") |
| template_id | string | Template UUID |
| template_name | string | Template display name |
| template_version | number | Template version at submission |
| status | string | Submission status (approved, pending, rejected) |
| created_at | string | ISO submission timestamp |
| key_summary | string[] | Key field values for quick display |

### FillTemplate (from FormFillerService)

Used by the form filler to render dynamic form structure.

| Field | Type | Description |
|-------|------|-------------|
| id | string | Template UUID |
| name | string | Template name |
| version | number | Template version |
| language | string | Template language (ar/en) |
| country | string | Target country |
| is_deprecated | boolean | Deprecation flag |
| pages | TemplatePage[] | Ordered pages containing elements |

### TemplatePage

| Field | Type | Description |
|-------|------|-------------|
| id | string | Page UUID |
| sort_order | number | Page ordering |
| width_mm | number | Page width in mm |
| height_mm | number | Page height in mm |
| elements | TemplateElement[] | Ordered form fields on this page |

### TemplateElement

| Field | Type | Description |
|-------|------|-------------|
| id | string | Element UUID |
| key | string | Unique field key (used as form control name) |
| type | string | Field type (text, number, date, select, etc.) |
| label_ar | string | Arabic label |
| label_en | string | English label |
| required | boolean | Whether field is required |
| direction | string | Text direction (rtl/ltr/auto) |
| sort_order | number | Field ordering within page |
| validation | any | Validation rules (pattern, min, max, etc.) |
| formatting | any | Display formatting rules |

### Customer (from CustomerService)

| Field | Type | Description |
|-------|------|-------------|
| id | string | Customer UUID |
| name | string | Full name |
| name_en | string | English name |
| national_id | string | National ID number |
| phone | string | Phone number |
| email | string | Email address |
| is_active | boolean | Active status |
| created_at | string | Creation timestamp |
| updated_at | string | Last modification timestamp |

## State Transitions

### Draft Lifecycle

```
[New Form] → DRAFT (auto-saved on navigation away)
DRAFT → DRAFT (field values updated, completion_percent recalculated)
DRAFT → SUBMITTED (operator clicks Submit, passes validation)
DRAFT → DELETED (operator explicitly deletes draft)
DRAFT → EXPIRED (expires_at reached, backend cleanup)
```

### Submission Status

```
SUBMITTED → PENDING (default on creation)
PENDING → APPROVED (reviewer approves)
PENDING → REJECTED (reviewer rejects)
```

## Relationships

```
Operator (1) ──→ (N) PinnedTemplate
Operator (1) ──→ (N) DraftResponse
Operator (1) ──→ (N) SubmissionListItem
DraftResponse (N) ──→ (1) FillTemplate
SubmissionListItem (N) ──→ (1) FillTemplate
Customer (1) ──→ (N) SubmissionListItem
```

## No New Entities

This feature introduces no new database tables, columns, or API contracts. All data flows through existing services and models documented above.
