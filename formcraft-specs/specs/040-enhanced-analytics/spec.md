# Feature Specification: Enhanced Analytics Dashboard

**Feature Branch**: `040-enhanced-analytics`  
**Created**: 2026-05-25  
**Status**: Draft  
**Vision Reference**: AC-05 (extends F27)

## User Scenarios & Testing

### User Story 1 - Field-Level Analytics (Priority: P1)

As an org admin, I need field-level analytics showing error rates per field, most common validation errors, fields most often left empty, and average time spent per field, so I can identify problematic form designs and coach operators on common mistakes.

**Why this priority**: Actionable design intelligence — field-level data directly improves template quality by showing designers which fields cause operator friction.

**Independent Test**: Navigate to `/admin/analytics/fields`, select a template, see per-field error rates and empty-field statistics.

**Acceptance Scenarios**:

1. **Given** admin navigates to field analytics for a specific template, **When** data loads, **Then** a table shows each field with: error rate (%), most common error type, empty rate (% of times left blank among non-required fields), and average fill time (if telemetry enabled).
2. **Given** a field has a high error rate (>20%), **When** displayed, **Then** it is highlighted with a warning indicator and the top 3 error messages are listed.
3. **Given** admin selects a date range, **When** analytics refresh, **Then** field-level metrics are scoped to submissions within that range.

---

### User Story 2 - Operator Performance Analytics (Priority: P2)

As an org admin, I need operator-level analytics showing forms filled per period, average fill time, error rate, and busiest hours, so I can identify coaching opportunities and optimize staffing.

**Why this priority**: Operational efficiency — operator analytics drive training decisions and staffing optimization.

**Independent Test**: Navigate to `/admin/analytics/operators`, see per-operator metrics, compare operators, identify outliers.

**Acceptance Scenarios**:

1. **Given** admin navigates to operator analytics, **When** data loads, **Then** a table shows each operator with: forms filled (day/week/month), average fill time, error rate (validation failures per form), and busiest hours.
2. **Given** an operator has a significantly higher error rate than average, **When** displayed, **Then** that operator is flagged with a coaching indicator.
3. **Given** admin views "Busiest Hours" chart, **When** data loads, **Then** a heatmap shows submission volume by hour and day of week for staffing optimization.

---

### User Story 3 - Compliance Analytics (Priority: P3)

As an org admin, I need compliance analytics showing percentage of templates with full validator coverage, bilingual label coverage, audit log volume by action type, and customer data access frequency, so I can monitor organizational compliance posture.

**Why this priority**: Regulatory readiness — banking and government clients need compliance dashboards for internal and external audits.

**Independent Test**: Navigate to `/admin/analytics/compliance`, see compliance scorecards, drill into non-compliant templates.

**Acceptance Scenarios**:

1. **Given** admin navigates to compliance analytics, **When** data loads, **Then** scorecards show: % templates with full validator coverage, % with bilingual labels, % with quality score > 80%.
2. **Given** a template lacks validator coverage on required fields, **When** admin clicks the non-compliant count, **Then** a list shows the specific templates and which fields lack validators.
3. **Given** admin views customer data access frequency, **When** a spike is detected, **Then** an alert highlights unusual access patterns (privacy monitoring).

---

### User Story 4 - Enhanced Template Usage Analytics (Priority: P4)

As an org admin, I need deeper template usage analytics beyond basic counts: fill completion rate (started vs submitted vs printed), average fill time per template, version adoption rate, and template usage by department/branch, so I can understand how templates are actually used.

**Why this priority**: Extends existing F27 analytics with deeper operational insights.

**Independent Test**: Navigate to `/admin/analytics/templates`, see completion funnel, fill time distribution, version adoption chart.

**Acceptance Scenarios**:

1. **Given** admin views template usage analytics, **When** selecting a template, **Then** a funnel chart shows: forms started → saved as draft → submitted → printed, with conversion rates between stages.
2. **Given** a template has multiple published versions, **When** admin views version adoption, **Then** a chart shows what percentage of operators are using each version over time.
3. **Given** admin selects "By Department" grouping, **When** data loads, **Then** usage metrics are broken down by department with department comparison.

---

### Edge Cases

- What happens when telemetry for field-level timing is disabled? Analytics show "N/A" for time fields.
- How does the system handle operators with zero submissions in a period?
- What happens when compliance analytics reference deleted templates?
- How does the system handle analytics across template version changes (field names changed)?

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide field-level analytics: error rate, common errors, empty rate, and fill time per field.
- **FR-002**: System MUST provide operator-level analytics: forms filled per period, average fill time, error rate, busiest hours.
- **FR-003**: System MUST provide compliance analytics: validator coverage %, bilingual label %, quality score distribution, customer data access frequency.
- **FR-004**: System MUST provide enhanced template usage analytics: completion funnel, fill time, version adoption, department/branch breakdown.
- **FR-005**: All analytics MUST support date range filtering.
- **FR-006**: All analytics MUST respect RLS — branch managers see branch-scoped data only.
- **FR-007**: Analytics data MUST be exportable as CSV and PNG (charts).
- **FR-008**: System MUST highlight anomalies and outliers with visual indicators.
- **FR-009**: Field-level timing analytics MUST be optional (configurable telemetry toggle).

### Key Entities

- **Field Analytics**: Template reference, field key, error_count, error_types (JSON), empty_count, total_submissions, avg_fill_time_ms.
- **Operator Analytics**: Operator ID, period (day/week/month), forms_filled, avg_fill_time, error_rate, busiest_hours (JSON).
- **Compliance Scorecard**: Org-level computed metrics: validator_coverage_pct, bilingual_label_pct, quality_score_avg, templates_needing_attention.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Field-level analytics for a template with 50 fields and 10,000 submissions loads within 5 seconds.
- **SC-002**: Operator analytics for 100 operators loads within 3 seconds.
- **SC-003**: Compliance scorecards compute across 500+ templates within 10 seconds.
- **SC-004**: After implementing field analytics recommendations, template error rates decrease by 25% within 3 months.
- **SC-005**: Staffing decisions informed by busiest-hours analytics improve operator utilization by 15%.
