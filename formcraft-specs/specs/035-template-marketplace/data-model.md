# Data Model: Template Marketplace

## Marketplace Listing

Represents a publisher-owned template offered in the marketplace.

- `id`: UUID primary key
- `template_id`: UUID references `templates.id`
- `publisher_org_id`: UUID references `organizations.id`
- `created_by`: UUID references `profiles.id`
- `name`: text, copied from template or overridden for marketplace display
- `description`: text
- `tags`: text array
- `preview_image_urls`: text array
- `sample_pdf_path`: text nullable
- `category`: text
- `country`: text
- `language`: text
- `compliance_badges`: text array
- `quality_score`: numeric default 0
- `price_type`: enum-like text `free` or `premium`
- `price_amount`: numeric nullable, required when `price_type = premium`
- `currency`: text default `USD`
- `status`: enum-like text `draft`, `submitted`, `approved`, `rejected`, `active`, `suspended`, `archived`
- `review_status`: enum-like text `pending`, `approved`, `rejected`
- `download_count`: integer default 0
- `average_rating`: numeric nullable
- `review_count`: integer default 0
- `published_version`: integer copied from template version
- `created_at`, `updated_at`, `approved_at`, `suspended_at`: timestamps

Validation:

- Only published templates can be submitted as marketplace listings.
- Premium listings require positive `price_amount` and `currency`.
- Only `active` listings appear in public marketplace browse/import responses.
- Suspended listings cannot be newly imported or purchased.

## Marketplace Import

Represents an immutable snapshot imported by a consumer organization.

- `id`: UUID primary key
- `listing_id`: UUID references `marketplace_listings.id`
- `consumer_org_id`: UUID references `organizations.id`
- `imported_template_id`: UUID references `templates.id`
- `imported_by`: UUID references `profiles.id`
- `listing_version`: integer
- `remapping_status`: enum-like text `not_required`, `pending`, `completed`
- `disabled_dependency_warnings`: jsonb array
- `source_snapshot`: jsonb with sanitized listing/template summary
- `created_at`, `updated_at`: timestamps

Validation:

- Import creates a new consumer-org draft template.
- Source publisher org identifiers are never copied into the consumer draft.
- Existing imports are not mutated when the listing changes.

## Marketplace Review

Represents verified feedback from a consumer organization.

- `id`: UUID primary key
- `listing_id`: UUID references `marketplace_listings.id`
- `consumer_org_id`: UUID references `organizations.id`
- `reviewer_id`: UUID references `profiles.id`
- `import_id`: UUID references `marketplace_imports.id`
- `rating`: integer 1 through 5
- `review_text`: text
- `verified_import`: boolean default true
- `status`: enum-like text `active`, `hidden`
- `created_at`, `updated_at`: timestamps

Validation:

- One active review per listing per consumer organization.
- Reviews require a completed import for the same listing and org.
- Listing aggregates update after create/update/hide.

## Marketplace Transaction

Represents purchase, refund, and revenue-share state for premium listings.

- `id`: UUID primary key
- `listing_id`: UUID references `marketplace_listings.id`
- `consumer_org_id`: UUID references `organizations.id`
- `publisher_org_id`: UUID references `organizations.id`
- `import_id`: UUID nullable references `marketplace_imports.id`
- `amount`: numeric
- `currency`: text
- `platform_share`: numeric
- `publisher_share`: numeric
- `payment_status`: enum-like text `pending`, `completed`, `failed`, `refunded`, `reversed`
- `provider`: text default `internal`
- `provider_reference`: text nullable
- `metadata`: jsonb
- `created_at`, `updated_at`, `completed_at`, `refunded_at`: timestamps

Validation:

- Revenue split is 70% publisher and 30% platform for completed purchases.
- Refunds create reversal metadata and never physically delete the original transaction.

## Relationships

- A `Marketplace Listing` has many `Marketplace Imports`, `Marketplace Reviews`, and `Marketplace Transactions`.
- A `Marketplace Import` belongs to one listing and one consumer draft template.
- A `Marketplace Review` belongs to one listing, one import, and one consumer organization.
- A `Marketplace Transaction` belongs to one listing and can be linked to one import.

## State Transitions

Listing:

- `draft` -> `submitted`
- `submitted` -> `approved` or `rejected`
- `approved` -> `active`
- `active` -> `suspended` or `archived`
- `suspended` -> `active` or `archived`

Import:

- `pending` remapping -> `completed` remapping after admin maps required reference dependencies
- `not_required` when no org-specific dependencies exist

Transaction:

- `pending` -> `completed` or `failed`
- `completed` -> `refunded` or `reversed`
