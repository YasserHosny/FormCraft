# Data Model: Advanced Form Validation & Conditional Logic

**Date**: 2026-05-17

## Schema Changes

### Modified Table: `elements`

| Column | Type | Change | Notes |
|--------|------|--------|-------|
| visible_when | JSONB | ADD | Condition object: {conditions: [{field, operator, value}], logic: "AND"} |
| required_when | JSONB | ADD | Same schema as visible_when |
| computed_value | TEXT | ADD | Math expression string referencing other element keys |
| default_value | TEXT | ADD | Static value or template token (e.g., "{{today}}") |
| placeholder_text | JSONB | ADD | Bilingual placeholder: {"ar": "...", "en": "..."} |

All columns are nullable. Elements without these columns behave exactly as today.

**Migration file**: `024_advanced_form_validation.sql`

```sql
-- Add conditional logic and computed value columns to elements
ALTER TABLE elements
ADD COLUMN visible_when JSONB,
ADD COLUMN required_when JSONB,
ADD COLUMN computed_value TEXT,
ADD COLUMN default_value TEXT,
ADD COLUMN placeholder_text JSONB;

COMMENT ON COLUMN elements.visible_when IS
  'Condition object controlling element visibility. Format: {conditions: [{field, operator, value}], logic: "AND"}';
COMMENT ON COLUMN elements.required_when IS
  'Condition object controlling dynamic required validation. Same format as visible_when.';
COMMENT ON COLUMN elements.computed_value IS
  'Math expression for auto-calculated fields. References other element keys. E.g., "subtotal * (1 + tax_rate / 100)"';
COMMENT ON COLUMN elements.default_value IS
  'Pre-populated value on form load. Static string or template token: {{today}}, {{user_name}}, {{user_email}}, {{org_name}}, {{now}}';
COMMENT ON COLUMN elements.placeholder_text IS
  'Bilingual placeholder text shown when field is empty. Format: {"ar": "أدخل...", "en": "Enter..."}';
```

## Condition Schema

### visible_when / required_when Format

```json
{
  "conditions": [
    {
      "field": "marital_status",
      "operator": "equals",
      "value": "married"
    },
    {
      "field": "age",
      "operator": "greater_than",
      "value": 18
    }
  ],
  "logic": "AND"
}
```

**Supported operators**:
| Operator | Description | Applicable Types |
|----------|-------------|------------------|
| equals | Exact match (case-sensitive) | text, number, date, dropdown |
| not_equals | Not exact match | text, number, date, dropdown |
| contains | Substring match (case-insensitive) | text |
| greater_than | Numeric/date comparison | number, date |
| less_than | Numeric/date comparison | number, date |
| is_empty | Field has no value | all types |
| is_not_empty | Field has a value | all types |

### computed_value Format

Plain text expression. Supported syntax:
- Arithmetic operators: `+`, `-`, `*`, `/`
- Parentheses: `(`, `)`
- Field references: bare element keys (e.g., `subtotal`, `tax_rate`)
- Numeric literals: `100`, `0.14`

Examples:
- `subtotal * (1 + tax_rate / 100)`
- `quantity * unit_price`
- `total_income - total_expenses`

### default_value Tokens

| Token | Resolves To |
|-------|-------------|
| `{{today}}` | Current date YYYY-MM-DD (local timezone) |
| `{{now}}` | Current datetime ISO format |
| `{{user_name}}` | Authenticated user's display name |
| `{{user_email}}` | Authenticated user's email |
| `{{org_name}}` | Current organization name |
| (any other string) | Used as literal static value |

## Entity Relationships

```
elements (MODIFIED — 5 new nullable columns)
├── visible_when (JSONB, nullable) — references other elements by key
├── required_when (JSONB, nullable) — references other elements by key
├── computed_value (TEXT, nullable) — references other elements by key
├── default_value (TEXT, nullable) — static or token
└── placeholder_text (JSONB, nullable) — {ar, en}

Dependency graph (logical, not stored):
  element_A.visible_when.conditions[].field → element_B.key
  element_A.computed_value expression → element_C.key, element_D.key
```

## Validation Rules

| Rule | Enforced At | Error |
|------|-------------|-------|
| Condition field must reference existing element key in same template | API service (design time) | 422 "Referenced field 'X' does not exist" |
| Condition operator must be one of the supported set | API (Pydantic) | 422 "Invalid operator" |
| Computed expression must parse without syntax errors | API (ast.parse) | 422 "Invalid expression syntax" |
| Computed expression must only reference existing element keys | API service | 422 "Referenced field 'X' does not exist" |
| No circular dependencies in visible_when/required_when/computed_value | API service (DFS cycle detection) | 422 "Circular dependency detected between A → B → A" |
| placeholder_text must have both ar and en keys if provided | API (Pydantic) | 422 "Both ar and en required" |
| Default token must be recognized or treated as literal | No validation needed — unrecognized treated as literal |
| On submission: hidden field values stripped from final data | API service (ConditionEngine) | N/A (silent strip) |

## Data Volume Impact

- 5 nullable JSONB/TEXT columns added to elements — negligible per row (most will be NULL)
- No new tables
- No new indexes needed (conditions are read as part of template load, not queried directly)
- Dependency graph computed in application memory on form load, not stored in DB
