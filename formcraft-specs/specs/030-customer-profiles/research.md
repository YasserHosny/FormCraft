# Research: Customer Profiles & Auto-Populate

**Feature**: 030-customer-profiles
**Date**: 2026-05-25

---

## R1: Customer Search Strategy for 50K Records

**Decision**: Use PostgreSQL full-text search with `tsvector` + GIN index for customer search. Create a generated column `search_vector` combining name_ar, name_en, identifier, phone, and email. Use `plainto_tsquery` for query parsing with `ts_rank` for relevance sorting. ILIKE fallback for short queries (<3 chars) or exact identifier lookups.

**Rationale**: PostgreSQL full-text search handles Arabic text natively (with `simple` text search config), supports compound queries, and performs well at 50K rows with GIN indexing. No external search engine (Elasticsearch, Meilisearch) needed at this scale, avoiding infrastructure complexity. The `simple` config is preferred over language-specific configs because the search spans mixed Arabic/English/numeric content.

**Alternatives considered**:
- ILIKE with trigram (pg_trgm) — good for fuzzy matching but slower at scale and harder to rank results
- External search engine (Elasticsearch) — over-engineering for 50K records; adds deployment complexity
- Supabase full-text search — uses the same PostgreSQL FTS underneath; we use it directly

---

## R2: Auto-Populate Field Mapping Architecture

**Decision**: Two-tier mapping system. Tier 1: a hardcoded default mapping table in the backend that maps common field key patterns (e.g., `national_id`, `customer_name_ar`, `phone`, `email`, `address`) to customer profile columns. Tier 2: a `customer_field_mappings` table storing per-template designer overrides. At auto-populate time, the system checks Tier 2 first (template-specific mappings), then falls back to Tier 1 (defaults).

**Rationale**: Convention-based matching works for 80% of templates that follow standard naming. The override table handles the remaining 20% where templates use non-standard field keys. The two-tier approach means auto-populate "just works" for new templates without designer configuration, while still supporting full customization.

**Default mapping table**:
| Customer Field | Default Element Key Patterns |
|---------------|------------------------------|
| name_ar | `customer_name_ar`, `name_ar`, `beneficiary_name_ar` |
| name_en | `customer_name_en`, `name_en`, `beneficiary_name_en` |
| identifier | `national_id`, `iqama`, `commercial_register`, `passport_number`, `customer_id_number` |
| contact_phone | `phone`, `mobile`, `contact_phone`, `customer_phone` |
| contact_email | `email`, `customer_email`, `contact_email` |
| address | `address`, `customer_address`, `mailing_address` |

**Alternatives considered**:
- Pure convention-only (no overrides) — too rigid for diverse template naming across organizations
- Fully manual (designer must configure every mapping) — too much friction; auto-populate should work out-of-the-box
- AI-based field matching — interesting but over-engineering for MVP; could be added later

---

## R3: Customer Profile Custom Fields Schema Storage

**Decision**: Store the custom field schema definition in org `settings` JSONB under a `customer_custom_fields` key. Store customer custom field values in the `customers.custom_fields` JSONB column. Schema structure follows the same pattern as reference data list schemas (F24): array of `{key, label_ar, label_en, type, required, options}` objects.

**Rationale**: JSONB storage is already used for org settings and element properties across FormCraft. The F24 reference data schema pattern is proven and familiar to the codebase. Storing schema in org settings means it's loaded once per session (already cached by org settings service) and validates efficiently against customer custom field values.

**Schema shape**:
```json
{
  "customer_custom_fields": [
    {"key": "account_number", "label_ar": "رقم الحساب", "label_en": "Account Number", "type": "text", "required": false},
    {"key": "credit_rating", "label_ar": "التصنيف الائتماني", "label_en": "Credit Rating", "type": "dropdown", "required": false, "options": ["A", "B", "C", "D"]}
  ]
}
```

**Alternatives considered**:
- Separate `customer_field_schemas` table — adds a table for what's essentially a configuration blob; JSONB in org settings is simpler
- EAV (Entity-Attribute-Value) pattern — poor query performance and complex to manage

---

## R4: Admin Customer Merge Strategy

**Decision**: Merge is a three-step atomic operation: (1) admin selects surviving profile and picks field values from each source, (2) backend updates all `form_submissions.customer_id` references from duplicate to survivor, (3) backend deletes the duplicate profile. All three steps run in a single database transaction. Audit log records both source profiles, the surviving profile, and which fields were kept from which source.

**Rationale**: Atomic transactions ensure data consistency — either all submissions are re-linked and the duplicate removed, or nothing changes. The side-by-side field selection UI lets admins make informed choices rather than blindly keeping one profile's data.

**Alternatives considered**:
- Soft-delete duplicates (mark as merged, keep the row) — simpler but leaves orphan data and complicates queries
- Automatic merge (keep newer values) — risky without human review; a typo in a newer record would overwrite correct data

---

## R5: Customer-Submission Link on Existing Data

**Decision**: Add `customer_id UUID REFERENCES customers(id) ON DELETE SET NULL` to `form_submissions` table. Nullable (existing submissions have no customer link). ON DELETE SET NULL ensures deleting a customer doesn't cascade-delete submissions — they just lose their customer reference. No backfill of existing submissions — only new submissions with customer selection will have the link.

**Rationale**: SET NULL is safer than CASCADE for financial/compliance data — submissions must never be lost due to customer data changes. Nullable column means zero impact on existing submission workflows. Backfilling old data is impractical without knowing which customer each past submission was for.

**Alternatives considered**:
- Junction table (customer_submissions) — adds query complexity for a simple 1:N relationship
- CASCADE delete — unacceptable for compliance; submissions are audit records
- Backfill via identifier matching — unreliable (field keys vary, data quality uncertain)

---

## R6: Auto-Create Customer Profile Trigger

**Decision**: Auto-create is a frontend prompt, not an automatic backend action. After successful form submission, the frontend checks if (1) auto-create is enabled in org settings, (2) the submitted form contains an identifier-type field with a value, and (3) no existing customer matches that identifier. If all three conditions are met, a dialog prompts the operator to confirm creating a customer profile from the submission data. On confirmation, the frontend calls the standard customer create endpoint.

**Rationale**: A prompt-based approach gives operators control — they can dismiss the prompt for one-time customers or non-person entities. Backend-automatic creation would generate profiles for every submission, flooding the customer database with entries operators don't want. The frontend prompt also makes it easy to show the operator exactly what data will be used.

**Alternatives considered**:
- Fully automatic backend creation — too aggressive; generates unwanted profiles
- Batch auto-create (admin reviews and approves) — more work for admins; prompt is simpler
- Only manual creation (no auto-create feature) — forces operators to navigate to customer profiles and re-enter data they just typed
