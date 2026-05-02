# Data Model: Tafqeet Control

**Branch**: `10-tafqeet-control` | **Date**: 2026-05-02

---

## Database Changes

### Migration: `009_tafqeet_element_type.sql`

```sql
-- Add tafqeet to the element_type enum
ALTER TYPE element_type ADD VALUE IF NOT EXISTS 'tafqeet';
```

No new tables or columns. All tafqeet config is stored in the existing `formatting` JSONB column.

---

## Backend Model Changes

### `app/models/enums.py` — ElementType

```python
class ElementType(StrEnum):
    TEXT     = "text"
    NUMBER   = "number"
    DATE     = "date"
    CURRENCY = "currency"
    DROPDOWN = "dropdown"
    RADIO    = "radio"
    CHECKBOX = "checkbox"
    IMAGE    = "image"
    QR       = "qr"
    BARCODE  = "barcode"
    TAFQEET  = "tafqeet"   # NEW
```

### `app/schemas/tafqeet.py` — New Pydantic schemas

```python
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, Field

class TafqeetPreviewRequest(BaseModel):
    amount: Decimal
    currency_code: Literal["EGP", "SAR", "AED", "USD"]
    language: Literal["ar", "en", "both"]
    show_currency: bool = True
    prefix: Literal["none", "faqat"] = "none"
    suffix: Literal["none", "la_ghair", "faqat_la_ghair", "only"] = "none"

class TafqeetPreviewResponse(BaseModel):
    result: str | None   # None when amount is out of range or conversion fails
```

### `formatting` JSONB shape for `tafqeet` elements

```json
{
  "sourceElementKey": "amount_field",   // string | null
  "currencyCode": "EGP",               // string | null — snapshot from source element; updated when source currencyCode changes
  "outputLanguage": "both",             // "ar" | "en" | "both"
  "showCurrency": true,                 // bool, default true
  "prefix": "none",                     // "none" | "faqat"
  "suffix": "faqat_la_ghair",           // "none" | "la_ghair" | "faqat_la_ghair" | "only"
  "previewValue": 12500.50              // number | null — design-time only, not used in PDF
}
```

**Validation constraints** (enforced by backend on save):
- `suffix = "only"` is rejected when `outputLanguage = "ar"` → HTTP 422
- `sourceElementKey`, if set, must reference a `number` or `currency` element on the same page → HTTP 422

---

## Frontend Model Changes

### `src/app/models/template.model.ts`

```typescript
// Before
export type ElementType = 'text' | 'number' | 'date' | 'currency' |
  'dropdown' | 'radio' | 'checkbox' | 'image' | 'qr' | 'barcode';

// After
export type ElementType = 'text' | 'number' | 'date' | 'currency' |
  'dropdown' | 'radio' | 'checkbox' | 'image' | 'qr' | 'barcode' | 'tafqeet';
```

### `src/app/models/element-defaults.ts`

```typescript
tafqeet: {
  type: 'tafqeet',
  width_mm: 120,
  height_mm: 12,
  label_ar: 'المبلغ كتابةً',
  label_en: 'Amount in Words',
  icon: 'spellcheck'
}
```

### `src/app/shared/schemas/tafqeet-formatting.schema.ts` — New Zod schema

```typescript
import { z } from 'zod';

export const TafqeetFormattingSchema = z.object({
  sourceElementKey: z.string().nullable().default(null),
  currencyCode: z.enum(['EGP', 'SAR', 'AED', 'USD']).nullable().default(null),
  outputLanguage: z.enum(['ar', 'en', 'both']).default('ar'),
  showCurrency: z.boolean().default(true),
  prefix: z.enum(['none', 'faqat']).default('none'),
  suffix: z.enum(['none', 'la_ghair', 'faqat_la_ghair', 'only']).default('none'),
  previewValue: z.number().nullable().default(null),
});

export type TafqeetFormatting = z.infer<typeof TafqeetFormattingSchema>;
```

---

## Entity Relationship (unchanged structure)

```
Template (1) ──── (*) Page (1) ──── (*) Element
                                        │
                                        ├── type: 'tafqeet'   ← new value
                                        ├── formatting: JSONB  ← tafqeet config here
                                        └── sourceElementKey  ← logical FK within same page
```

`sourceElementKey` is a logical reference (not a DB foreign key) to another element's `key` field on the same page. No referential integrity constraint at DB level — validated at API level (FR-023).
