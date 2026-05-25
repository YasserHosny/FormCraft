# Research: Template Marketplace

## Payment Scope

**Decision**: Implement premium purchases through a pluggable payment-provider adapter and persist internal transaction states (`pending`, `completed`, `failed`, `refunded`, `reversed`) without integrating a live gateway in MVP.

**Rationale**: The specification requires payment processing and 70/30 revenue-share records, but the project has no existing payment provider. An adapter keeps the service testable and allows later gateway integration without changing marketplace contracts.

**Alternatives considered**: Direct Stripe-style integration was rejected because no provider is specified. Free-only MVP was rejected because premium listings and revenue share are core requirements.

## Imported Template Updates

**Decision**: Treat each import as an immutable snapshot. Publisher updates create a new listing version and consumers may re-import as a separate draft.

**Rationale**: Existing templates are normalized drafts with user-owned edits. Auto-mutating consumer drafts would risk data loss and cross-org surprises.

**Alternatives considered**: Automatic update propagation was rejected due to edit conflicts and governance risk. Diff/merge UI was rejected as outside scope.

## Cross-Org Cloning

**Decision**: Clone template, pages, elements, print settings, supported validators, and layout coordinates. Strip publisher org identifiers, record remapping requirements for reference data, and disable unsupported custom validators/fields with warnings until mapped.

**Rationale**: This preserves print fidelity while preventing publisher-specific data leakage. It also gives admins a clear activation path for org-local dependencies.

**Alternatives considered**: Blocking imports with any org-specific dependency was rejected because it would make curated templates brittle. Blind cloning was rejected for security and correctness.

## Refunds

**Decision**: Record refunds as admin-triggered transaction reversal states. Imported drafts remain available unless an admin explicitly revokes access.

**Rationale**: This keeps financial records auditable and avoids deleting templates unexpectedly after they may have been edited locally.

**Alternatives considered**: Automatic draft deletion was rejected due to data loss risk. Full self-service refund workflows were deferred.

## Publisher Eligibility

**Decision**: If a publisher org is no longer marketplace-eligible, its active listings are suspended from discovery and purchase/import. Existing consumer imports continue working.

**Rationale**: This protects marketplace quality without breaking consumer operations.

**Alternatives considered**: Hard deleting listings was rejected for auditability. Allowing new purchases from lapsed publishers was rejected for policy risk.

## Search And Sorting

**Decision**: Use Supabase/PostgreSQL filtering with indexed listing status, category, country, language, price type, compliance badges, average rating, download count, and text search over name/description/tags.

**Rationale**: The catalog target is 1,000+ templates, which PostgreSQL can serve within the 2 second requirement with indexes and bounded pagination.

**Alternatives considered**: External search service was rejected as unnecessary for MVP.

## Review Verification

**Decision**: Allow one active review per listing per consumer org only after a completed import. Updating a review recalculates listing aggregate rating and review count.

**Rationale**: Verified-import reviews reduce spam and support consistent sorting.

**Alternatives considered**: User-level reviews were rejected because marketplace usage is org-centered. Anonymous reviews were rejected for trust and auditability.
