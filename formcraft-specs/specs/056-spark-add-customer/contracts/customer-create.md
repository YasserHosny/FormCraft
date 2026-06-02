# Contract: Customer Create (F056)

**Date**: 2026-06-02  
**Owner**: F056 — Spark Add Customer  
**Stability**: Stable (existing API — no changes required)

## API Endpoint

`POST /api/customers/`

Defined in existing `CustomerService.create()`. This feature introduces no new endpoints or schema changes.

## Request Payload (`CustomerCreate`)

```typescript
{
  name_ar: string;           // required
  name_en?: string;          // optional
  identifier_type: string;   // required; one of: national_id | iqama | commercial_register | passport | other
  identifier: string;        // required
  contact_phone?: string;    // optional; any string, no format constraint
  contact_email?: string;    // optional; RFC 5322 format validated client-side
  address?: string;          // optional
  custom_fields?: {};        // always sent as empty object in v1
}
```

## Response: Success (HTTP 201)

```typescript
Customer {
  id: string;
  org_id: string;
  name_ar: string;
  name_en: string | null;
  identifier_type: string;
  identifier: string;
  contact_phone: string | null;
  contact_email: string | null;
  address: string | null;
  custom_fields: Record<string, any> | null;
  is_active: boolean;
  created_by: string | null;
  created_at: string;
  updated_at: string;
}
```

→ On success: redirect to `/desk/customers/{id}` (Classic detail page)

## Response: Duplicate (HTTP 409)

```json
{ "customer": { "id": "...", ... } }
```

→ Inject `{ duplicate: true }` error onto the `identifier` `FormControl`.

## Response: Other Error (HTTP 4xx / 5xx)

→ Display `err.error?.detail` or generic fallback via snackbar. Form remains open and re-editable.
