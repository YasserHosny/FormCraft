# Feature Specification: Template Marketplace

**Feature Branch**: `035-template-marketplace`  
**Created**: 2026-05-25  
**Status**: Draft  
**Vision Reference**: EXT-02

## User Scenarios & Testing

### User Story 1 - Browse & Import Templates (Priority: P1)

As an org admin, I need to browse a curated marketplace of form templates, preview them in read-only canvas view and sample PDF, and import selected templates into my organization as new drafts, so I can accelerate form creation by starting from proven designs.

**Why this priority**: Consumer-side value must exist first — without a good browsing/import experience, the marketplace has no demand.

**Independent Test**: Navigate to `/marketplace`, filter by country and category, preview a template, click "Use Template", verify it appears as a new draft in the org's template library.

**Acceptance Scenarios**:

1. **Given** admin navigates to `/marketplace`, **When** the page loads, **Then** a searchable grid shows available templates with: name, publisher org, category, country, language, compliance badges, quality score, download count, rating, and price (free/premium).
2. **Given** admin clicks a template card, **When** the preview opens, **Then** a read-only canvas view and sample PDF are shown.
3. **Given** admin clicks "Use Template" on a free template, **When** confirmed, **Then** the template is cloned into the admin's org as a new draft with all elements, validators, and bindings intact.
4. **Given** the imported template references org-specific reference data, **When** import completes, **Then** a mapping wizard helps remap bindings to the consumer org's reference lists.

---

### User Story 2 - Publish to Marketplace (Priority: P2)

As an org admin, I need to publish a finalized template to the marketplace with description, tags, preview images, compliance certifications, and pricing, so other organizations can discover and use my templates.

**Why this priority**: Supply-side — marketplace needs content to be valuable.

**Independent Test**: Select a published template, click "Publish to Marketplace", fill metadata, submit for review, verify it appears in marketplace after approval.

**Acceptance Scenarios**:

1. **Given** admin selects a published template, **When** they click "Publish to Marketplace", **Then** a form shows: description, tags, preview images upload, compliance standard checkboxes, pricing (free/premium with amount).
2. **Given** admin submits the listing, **When** the FormCraft review team approves it, **Then** the template appears in the marketplace with the org's attribution.
3. **Given** admin publishes a premium template at $50, **When** another org purchases it, **Then** a 70/30 revenue share is recorded (70% publisher, 30% platform).

---

### User Story 3 - Ratings & Reviews (Priority: P3)

As a marketplace user, I need to rate and review templates I've imported so I can help other users make informed decisions and provide feedback to publishers.

**Why this priority**: Social proof drives marketplace adoption — ratings are essential for trust.

**Independent Test**: Import a template, return to marketplace, leave a 4-star rating with review text, verify it appears on the listing.

**Acceptance Scenarios**:

1. **Given** an org has imported a marketplace template, **When** admin navigates to that listing, **Then** a "Rate & Review" option is available.
2. **Given** admin submits a rating (1-5 stars) with review text, **When** saved, **Then** the listing's average rating and review count update.
3. **Given** multiple orgs review the same template, **When** browsing the marketplace, **Then** templates can be sorted by average rating and download count.

---

### Edge Cases

- What happens when a publisher updates a marketplace template that others have already imported?
- How does the system handle premium template refunds?
- What happens when a publisher's org subscription lapses but their templates are in the marketplace?
- How does cross-org cloning handle org-specific validators or custom fields?

## Requirements

### Functional Requirements

- **FR-001**: System MUST provide a searchable, filterable marketplace UI at `/marketplace`.
- **FR-002**: Marketplace MUST support filtering by country, category, language, compliance standard, and price.
- **FR-003**: Template previews MUST show read-only canvas view and sample PDF.
- **FR-004**: "Use Template" MUST clone the template into the consumer org as a new draft with org-specific data stripped.
- **FR-005**: System MUST support a publisher flow with description, tags, images, compliance certifications, and pricing.
- **FR-006**: Marketplace listings MUST be reviewed and approved by the FormCraft team before going live.
- **FR-007**: System MUST support ratings (1-5 stars) and text reviews from verified importers.
- **FR-008**: System MUST track download counts and display them on listings.
- **FR-009**: Premium templates MUST support payment processing with 70/30 revenue share.
- **FR-010**: All marketplace transactions MUST be recorded in the audit log.

### Key Entities

- **Marketplace Listing**: Template reference, publisher org, description, tags, images, compliance badges, price, approval status, download count, average rating.
- **Marketplace Review**: Reviewer org, rating (1-5), review text, date, verified import flag.
- **Marketplace Transaction**: Listing, consumer org, price, revenue share, payment status, import timestamp.

## Success Criteria

### Measurable Outcomes

- **SC-001**: Marketplace search returns results within 2 seconds for a catalog of 1,000+ templates.
- **SC-002**: Template import preserves 100% of elements, validators, and layout on cross-org clone.
- **SC-003**: 80% of marketplace listings receive at least one rating within 30 days of first import.
- **SC-004**: Publisher approval turnaround averages under 48 hours.
- **SC-005**: Premium template payment processing completes within 30 seconds.
