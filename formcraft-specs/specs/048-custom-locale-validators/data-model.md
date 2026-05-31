# Feature 048: Data Model Design

## Overview
This document details the database schema, relationships, RLS policies, and migration strategy for custom locale validators.

---

## Database Schema

### 1. custom_validators Table

```sql
CREATE TABLE custom_validators (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  regex_pattern VARCHAR(500) NOT NULL,
  error_message_ar TEXT NOT NULL,
  error_message_en TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by UUID NOT NULL REFERENCES profiles(id),
  updated_by UUID NOT NULL REFERENCES profiles(id),
  deleted_at TIMESTAMP,
  
  -- Constraints
  UNIQUE(org_id, name),
  CHECK (char_length(name) > 0 AND char_length(name) <= 255),
  CHECK (char_length(regex_pattern) > 0 AND char_length(regex_pattern) <= 500),
  CHECK (char_length(error_message_ar) > 0),
  CHECK (char_length(error_message_en) > 0),
  
  -- Ensure updated_at >= created_at
  CHECK (updated_at >= created_at)
);

-- Indexes for performance
CREATE INDEX idx_custom_validators_org_id_deleted_at 
  ON custom_validators(org_id, deleted_at) 
  WHERE deleted_at IS NULL;

CREATE INDEX idx_custom_validators_org_id_name 
  ON custom_validators(org_id, name) 
  WHERE deleted_at IS NULL;

CREATE INDEX idx_custom_validators_created_by 
  ON custom_validators(created_by);

CREATE INDEX idx_custom_validators_updated_by 
  ON custom_validators(updated_by);
```

**Column Descriptions:**
- `id`: Unique identifier for the validator (UUID)
- `org_id`: Organization that owns this validator (FK to organizations)
- `name`: Display name for the validator (e.g., "Egypt Commercial Register")
- `description`: Optional description of what this validator checks
- `regex_pattern`: Regular expression pattern to test field value against
- `error_message_ar`: Error message displayed when validation fails (Arabic)
- `error_message_en`: Error message displayed when validation fails (English)
- `created_at`: Timestamp when validator was created
- `updated_at`: Timestamp when validator was last updated
- `created_by`: Profile ID of the user who created the validator
- `updated_by`: Profile ID of the user who last updated the validator
- `deleted_at`: Timestamp when validator was soft-deleted (NULL if active)

---

### 2. Elements Table Extension

Add `custom_validators_ids` column to track which validators apply to an element:

```sql
ALTER TABLE elements 
ADD COLUMN custom_validators_ids UUID[] DEFAULT '{}' NOT NULL;

-- Index for reverse lookups (which elements use this validator)
CREATE INDEX idx_elements_custom_validators_ids 
  ON elements USING GIN(custom_validators_ids);
```

**Note on Array Storage:**
- Using PostgreSQL `UUID[]` for simplicity and direct query support
- Alternative: separate `element_validators` junction table for normalization
- **Rationale**: Array is sufficient for expected use case (< 20 validators per field typical)

---

### 3. Audit Log Entries

Leverage existing `audit_logs` table with these event types:

```sql
-- Example audit log entries:

INSERT INTO audit_logs (
  org_id, user_id, entity_type, entity_id, action, 
  changes, timestamp
) VALUES
  -- VALIDATOR_CREATED
  (
    'org-123',
    'user-456',
    'custom_validator',
    'validator-789',
    'CREATED',
    '{
      "name": "Egypt Commercial Register",
      "regex_pattern": "^[0-9]{12}$",
      "error_message_ar": "يجب أن يكون 12 رقمًا",
      "error_message_en": "Must be 12 digits"
    }'::jsonb,
    CURRENT_TIMESTAMP
  ),
  
  -- VALIDATOR_UPDATED
  (
    'org-123',
    'user-456',
    'custom_validator',
    'validator-789',
    'UPDATED',
    '{
      "error_message_ar": {
        "before": "يجب أن يكون 12 رقمًا",
        "after": "رقم السجل التجاري يجب أن يكون 12 رقمًا"
      }
    }'::jsonb,
    CURRENT_TIMESTAMP
  ),
  
  -- VALIDATOR_DELETED
  (
    'org-123',
    'user-456',
    'custom_validator',
    'validator-789',
    'DELETED',
    '{
      "name": "Egypt Commercial Register",
      "reason": "No longer needed"
    }'::jsonb,
    CURRENT_TIMESTAMP
  );
```

**Event Types:**
- `VALIDATOR_CREATED`: New validator created (full details)
- `VALIDATOR_UPDATED`: Validator modified (before/after values)
- `VALIDATOR_DELETED`: Validator soft-deleted (metadata)

---

## Row-Level Security (RLS) Policies

### Enable RLS on custom_validators Table

```sql
ALTER TABLE custom_validators ENABLE ROW LEVEL SECURITY;
```

### Policy 1: Read Access

```sql
CREATE POLICY custom_validators_read 
  ON custom_validators 
  FOR SELECT 
  USING (org_id = auth.jwt_claim('org_id')::uuid);
```

**Purpose**: Users can only see validators for their organization.

### Policy 2: Insert Access

```sql
CREATE POLICY custom_validators_insert 
  ON custom_validators 
  FOR INSERT 
  WITH CHECK (
    org_id = auth.jwt_claim('org_id')::uuid
    AND auth.uid() = created_by
  );
```

**Purpose**: Users can only create validators for their org, with themselves as creator.

### Policy 3: Update Access

```sql
CREATE POLICY custom_validators_update 
  ON custom_validators 
  FOR UPDATE 
  USING (org_id = auth.jwt_claim('org_id')::uuid)
  WITH CHECK (
    org_id = auth.jwt_claim('org_id')::uuid
    AND updated_by = auth.uid()
  );
```

**Purpose**: Users can only update validators for their org, and must set themselves as the updater.

### Policy 4: Delete Access

```sql
CREATE POLICY custom_validators_delete 
  ON custom_validators 
  FOR DELETE 
  USING (org_id = auth.jwt_claim('org_id')::uuid);
```

**Purpose**: Users can only soft-delete validators for their org.

### Policy 5: Admin-Only Management

Optional stricter policy for admin-only access:

```sql
CREATE POLICY custom_validators_admin_only 
  ON custom_validators 
  FOR ALL 
  USING (
    org_id = auth.jwt_claim('org_id')::uuid
    AND auth.jwt_claim('role') = 'admin'
  );
```

---

## Reverse Relationships

### Element → Validators (via array)

```sql
-- Query: Get all validators for an element
SELECT cv.* 
FROM custom_validators cv 
WHERE cv.id = ANY(elements.custom_validators_ids)
  AND cv.deleted_at IS NULL;
```

### Validator → Elements (via GIN index)

```sql
-- Query: Find all elements using a specific validator
SELECT e.* 
FROM elements e 
WHERE v.id = ANY(e.custom_validators_ids)
  AND e.org_id = $1;
```

### Validator → Templates (multi-level relationship)

```sql
-- Query: Find all templates that use a validator (via elements)
SELECT DISTINCT t.id, t.name, MAX(e.updated_at) as last_used_date
FROM templates t
JOIN pages p ON p.template_id = t.id
JOIN elements e ON e.page_id = p.id
WHERE $1 = ANY(e.custom_validators_ids)
  AND t.org_id = $2
GROUP BY t.id, t.name
ORDER BY last_used_date DESC;
```

---

## Validation Rules

### Regex Pattern Validation

Before storing a validator, validate the regex pattern:

```javascript
// Backend validation (Python)
import re

def validate_regex_pattern(pattern: str, timeout_ms: int = 100) -> tuple[bool, str]:
    """Validate regex pattern for ReDoS vulnerabilities."""
    try:
        # Test pattern compiles
        compiled = re.compile(pattern)
        
        # Test against sample strings (< 100ms execution)
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError("Regex pattern evaluation took too long")
        
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(1)  # 1 second timeout
        
        # Test against empty string
        compiled.search("")
        
        signal.alarm(0)  # Cancel alarm
        
        return True, "Pattern valid"
    except re.error as e:
        return False, f"Invalid regex: {str(e)}"
    except TimeoutError:
        return False, "Regex pattern execution timeout (possible ReDoS)"
```

### Message Length Validation

```sql
-- Constraints ensure non-empty messages
CHECK (char_length(error_message_ar) > 0)
CHECK (char_length(error_message_en) > 0)

-- Recommended max lengths (not enforced)
-- error_message_ar: max 200 characters
-- error_message_en: max 200 characters
```

---

## Migration Strategy

### Migration 1: Create custom_validators Table

```sql
-- File: migrations/001_create_custom_validators.sql

CREATE TABLE custom_validators (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name VARCHAR(255) NOT NULL,
  description TEXT,
  regex_pattern VARCHAR(500) NOT NULL,
  error_message_ar TEXT NOT NULL,
  error_message_en TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  created_by UUID NOT NULL REFERENCES profiles(id),
  updated_by UUID NOT NULL REFERENCES profiles(id),
  deleted_at TIMESTAMP,
  
  UNIQUE(org_id, name),
  CHECK (char_length(name) > 0 AND char_length(name) <= 255),
  CHECK (char_length(regex_pattern) > 0 AND char_length(regex_pattern) <= 500),
  CHECK (char_length(error_message_ar) > 0),
  CHECK (char_length(error_message_en) > 0),
  CHECK (updated_at >= created_at)
);

CREATE INDEX idx_custom_validators_org_id_deleted_at 
  ON custom_validators(org_id, deleted_at) 
  WHERE deleted_at IS NULL;

CREATE INDEX idx_custom_validators_org_id_name 
  ON custom_validators(org_id, name) 
  WHERE deleted_at IS NULL;

CREATE INDEX idx_custom_validators_created_by ON custom_validators(created_by);
CREATE INDEX idx_custom_validators_updated_by ON custom_validators(updated_by);

ALTER TABLE custom_validators ENABLE ROW LEVEL SECURITY;

-- RLS Policies
CREATE POLICY custom_validators_read ON custom_validators FOR SELECT 
  USING (org_id = auth.jwt_claim('org_id')::uuid);

CREATE POLICY custom_validators_insert ON custom_validators FOR INSERT 
  WITH CHECK (org_id = auth.jwt_claim('org_id')::uuid AND auth.uid() = created_by);

CREATE POLICY custom_validators_update ON custom_validators FOR UPDATE 
  USING (org_id = auth.jwt_claim('org_id')::uuid)
  WITH CHECK (org_id = auth.jwt_claim('org_id')::uuid AND updated_by = auth.uid());

CREATE POLICY custom_validators_delete ON custom_validators FOR DELETE 
  USING (org_id = auth.jwt_claim('org_id')::uuid);
```

### Migration 2: Extend elements Table

```sql
-- File: migrations/002_add_custom_validators_to_elements.sql

ALTER TABLE elements 
ADD COLUMN custom_validators_ids UUID[] DEFAULT '{}' NOT NULL;

CREATE INDEX idx_elements_custom_validators_ids 
  ON elements USING GIN(custom_validators_ids);
```

### Rollback Strategy

```sql
-- Rollback Migration 2
ALTER TABLE elements 
DROP COLUMN custom_validators_ids;

-- Rollback Migration 1
DROP TABLE custom_validators;
```

---

## Performance Considerations

### Query Optimization

1. **List validators for org** (with pagination):
   ```sql
   SELECT * FROM custom_validators 
   WHERE org_id = $1 AND deleted_at IS NULL 
   ORDER BY name ASC 
   LIMIT 20 OFFSET $2;
   ```
   **Index used**: `idx_custom_validators_org_id_deleted_at`

2. **Find elements using a validator**:
   ```sql
   SELECT * FROM elements 
   WHERE $1 = ANY(custom_validators_ids);
   ```
   **Index used**: `idx_elements_custom_validators_ids` (GIN)

3. **Find templates using a validator**:
   ```sql
   SELECT DISTINCT t.id, t.name 
   FROM templates t
   JOIN pages p ON p.template_id = t.id
   JOIN elements e ON e.page_id = p.id
   WHERE $1 = ANY(e.custom_validators_ids);
   ```
   **Optimization**: Cache this query, re-compute on validator update

### Caching Strategy

- **Validator list per org**: Cache in memory, invalidate on CRUD
- **Validator details**: Cache per validator ID, invalidate on update
- **Template usage**: Cache per validator, invalidate on element update

---

## Example Data

```sql
-- Insert sample validators
INSERT INTO custom_validators 
  (org_id, name, description, regex_pattern, error_message_ar, 
   error_message_en, created_by, updated_by)
VALUES
  (
    'org-123',
    'Egypt Commercial Register',
    'Commercial register number format for Egyptian companies',
    '^[0-9]{12}$',
    'رقم السجل التجاري يجب أن يكون 12 رقمًا',
    'Commercial register must be 12 digits',
    'user-456',
    'user-456'
  ),
  (
    'org-123',
    'Saudi SADAD Bill Number',
    'SADAD bill reference number for Saudi Arabia',
    '^[0-9]{13}$',
    'رقم الفاتورة يجب أن يكون 13 رقمًا',
    'Bill number must be 13 digits',
    'user-456',
    'user-456'
  ),
  (
    'org-123',
    'International Phone',
    'International phone number format',
    '^\+?[1-9]\d{1,14}$',
    'يجب أن يكون رقم الهاتف بالصيغة الدولية',
    'Phone must be in international format (+1234567890)',
    'user-456',
    'user-456'
  );

-- Example: Apply validator to element
UPDATE elements 
SET custom_validators_ids = ARRAY['validator-123', 'validator-456']
WHERE id = 'elem-789';
```

---

## Monitoring & Observability

### Key Metrics
- **Validators per org**: Average, max (alert if > 1000)
- **Regex evaluation time**: P50, P95, P99 (alert if P95 > 100ms)
- **Query latency**: For list, lookup, usage queries
- **Cache hit rate**: For validator list and usage caches
- **Audit log completeness**: All CRUD operations logged

### Alerts
- Regex evaluation time P95 > 500ms
- List query latency > 1s
- Cache hit rate < 80%
- RLS policy violations detected
- Missing audit log entries

---

## Security Considerations

### SQL Injection Prevention
- All queries use parameterized statements
- RLS policies enforce at database level
- Input validation at application layer

### ReDoS Prevention
- Regex pattern validation before storage (timeout)
- Timeout on regex evaluation during form fill (100ms)
- Monitoring of regex execution times

### Cross-Org Access Prevention
- RLS policies strictly enforce org_id matching
- All queries include org_id filter
- Audit log all access attempts
- Regular security audits

### Data Integrity
- Soft delete (deleted_at) prevents orphaned references
- Foreign key constraints prevent dangling references
- Audit trail maintains change history
- Version history (created_at, updated_at)
