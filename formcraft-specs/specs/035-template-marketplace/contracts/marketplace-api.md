# Marketplace API Contract

All endpoints require Supabase JWT authentication. Endpoints that create listings, imports, purchases, reviews, or moderation actions require `admin` role unless otherwise noted.

## Browse Listings

`GET /api/marketplace/listings`

Query parameters:

- `search`: optional text
- `country`: optional country code
- `category`: optional text
- `language`: optional language code
- `compliance`: optional comma-separated badge list
- `price_type`: optional `free` or `premium`
- `sort_by`: optional `quality_score`, `download_count`, `average_rating`, `created_at`
- `sort_dir`: optional `asc` or `desc`
- `page`: integer, default 1
- `page_size`: integer, default 24, maximum 100

Response `200`:

```json
{
  "items": [
    {
      "id": "uuid",
      "name": "Municipal Permit",
      "publisher_org_name": "Example Publisher",
      "category": "permits",
      "country": "AE",
      "language": "ar",
      "compliance_badges": ["VAT"],
      "quality_score": 94,
      "download_count": 15,
      "average_rating": 4.5,
      "review_count": 8,
      "price_type": "free",
      "price_amount": null,
      "currency": "USD",
      "preview_image_urls": []
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 24
}
```

## Listing Detail

`GET /api/marketplace/listings/{listing_id}`

Response `200` includes listing metadata, sanitized template pages/elements for read-only canvas preview, sample PDF URL, rating summary, and dependency warnings.

Errors:

- `404` if the listing is not active or visible to the caller.

## Import Listing

`POST /api/marketplace/listings/{listing_id}/import`

Request:

```json
{
  "draft_name": "Imported permit template",
  "reference_mappings": {
    "publisher-reference-id": "consumer-reference-id"
  },
  "accept_disabled_dependencies": true
}
```

Response `201`:

```json
{
  "import_id": "uuid",
  "template_id": "uuid",
  "remapping_status": "completed",
  "disabled_dependency_warnings": []
}
```

Errors:

- `402` when the listing is premium and no completed transaction exists.
- `409` when reference remapping is required but not provided.
- `422` when the listing is suspended or archived.

## Purchase Premium Listing

`POST /api/marketplace/listings/{listing_id}/purchase`

Request:

```json
{
  "provider": "internal",
  "idempotency_key": "unique-client-key"
}
```

Response `201`:

```json
{
  "transaction_id": "uuid",
  "payment_status": "completed",
  "amount": 50,
  "currency": "USD",
  "publisher_share": 35,
  "platform_share": 15
}
```

## Publish Listing

`POST /api/marketplace/listings`

Request:

```json
{
  "template_id": "uuid",
  "description": "Template description",
  "tags": ["permit", "municipality"],
  "preview_image_urls": [],
  "compliance_badges": ["VAT"],
  "price_type": "premium",
  "price_amount": 50,
  "currency": "USD"
}
```

Response `201` returns the created listing with `status = submitted`.

Errors:

- `403` if the caller does not own the template org.
- `422` if the template is not published.

## Moderate Listing

`POST /api/admin/marketplace/listings/{listing_id}/moderation`

Platform admin endpoint.

Request:

```json
{
  "action": "approve",
  "comment": "Approved for catalog"
}
```

Response `200` returns the updated listing.

Allowed actions: `approve`, `reject`, `suspend`, `reactivate`, `archive`.

## Submit Or Update Review

`POST /api/marketplace/listings/{listing_id}/reviews`

Request:

```json
{
  "import_id": "uuid",
  "rating": 4,
  "review_text": "Useful template with clean layout."
}
```

Response `201` returns the review and updated aggregate rating.

Errors:

- `403` if the org has not imported the listing.
- `409` if another active review exists and update mode is not allowed.

## List Reviews

`GET /api/marketplace/listings/{listing_id}/reviews`

Response `200`:

```json
{
  "items": [
    {
      "id": "uuid",
      "rating": 4,
      "review_text": "Useful template with clean layout.",
      "verified_import": true,
      "created_at": "2026-05-26T00:00:00Z"
    }
  ],
  "total": 1
}
```
