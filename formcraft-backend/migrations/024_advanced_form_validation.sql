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
  'Bilingual placeholder text shown when field is empty. Format: {"ar": "...", "en": "..."}';
