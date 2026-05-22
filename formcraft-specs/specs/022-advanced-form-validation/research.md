# Research: Advanced Form Validation & Conditional Logic

**Date**: 2026-05-17

## Research Questions

No NEEDS CLARIFICATION items. Research focused on condition engine architecture, expression parser safety, dependency graph strategy, and submission stripping behavior.

## Findings

### 1. ConditionEngine Architecture

**Decision**: Create a `ConditionEngine` class with implementations in both Python (backend validation on submit) and TypeScript (frontend reactive evaluation). Both share the same condition schema and evaluation logic.

**Python ConditionEngine** (`formcraft-backend/app/services/condition_engine.py`):
- Used during form submission to validate required_when and strip hidden field values
- Stateless: takes form data + element conditions → returns evaluation results

**TypeScript ConditionEngine** (`formcraft-frontend/src/app/features/desk/services/condition-engine.service.ts`):
- Used during form filling for real-time visibility/required toggling and computed value updates
- Reactive: subscribes to form valueChanges and re-evaluates affected conditions

### 2. Condition Schema

Stored in new element columns (`visible_when`, `required_when`):

```json
{
  "conditions": [
    {
      "field": "marital_status",
      "operator": "equals",
      "value": "married"
    }
  ],
  "logic": "AND"
}
```

Supported operators: `equals`, `not_equals`, `contains`, `greater_than`, `less_than`, `is_empty`, `is_not_empty`.

All conditions within a group use AND logic (v1). OR logic and nested groups are future extensions.

### 3. Computed Value Expression Parser

**Safety concern**: Cannot use `eval()` — security risk.

**Decision**: Implement a simple expression parser supporting:
- Arithmetic: `+`, `-`, `*`, `/`, `(`, `)`
- Field references: element keys (resolved at evaluation time)
- Numeric literals
- No function calls, no string operations (v1)

Python: use `ast.parse()` in expression mode with a whitelist of allowed node types (Num, BinOp, Name, UnaryOp).
TypeScript: implement a recursive-descent parser (~100 lines) or use a minimal safe math expression evaluator.

### 4. Dependency Graph

**Decision**: Build a directed dependency graph on form load:
- Nodes: element keys
- Edges: "element A depends on element B" (A has condition referencing B, or A computed from B)

On form load:
1. Parse all elements' visible_when, required_when, computed_value
2. Build adjacency list: `dependents[source_key] = [dependent_key_1, ...]`
3. Detect cycles using DFS — if found at design time, reject save with error

On field change:
1. Look up `dependents[changed_key]`
2. Re-evaluate only those dependents
3. If a dependent's visibility changed, cascade: look up ITS dependents

This gives O(1) lookup per field change + O(k) evaluation where k = number of direct dependents.

### 5. Submission Data Stripping

**Design decision (important)**:
- **Draft save**: Stores ALL field values, including hidden fields. Reason: if operator fills spouse_name, then changes marital_status to "single" (hiding spouse_name), then saves draft — if they later change back to "married", the data should still be there.
- **Final submission**: Strips values for fields that are currently hidden at submission time. The backend ConditionEngine re-evaluates all conditions using final form data and removes hidden field values from the stored submission.

### 6. Database Column Additions

Five new nullable columns on the `elements` table:
- `visible_when` (JSONB, nullable) — condition object
- `required_when` (JSONB, nullable) — condition object
- `computed_value` (TEXT, nullable) — expression string
- `default_value` (TEXT, nullable) — static value or template token like {{today}}
- `placeholder_text` (JSONB, nullable) — {ar: "...", en: "..."}

All nullable to maintain backwards compatibility. Elements without these columns behave exactly as before.

### 7. Dynamic Default Tokens

Supported tokens for `default_value`:
- `{{today}}` — current date in YYYY-MM-DD
- `{{now}}` — current datetime in ISO format
- `{{user_name}}` — current authenticated user's display name
- `{{user_email}}` — current authenticated user's email
- `{{org_name}}` — current organization name

Frontend resolves tokens on form load. Static values used as-is.
