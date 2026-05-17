-- Expand element type CHECK to include signature and table
-- Feature 020: New Element Types

ALTER TABLE elements
DROP CONSTRAINT IF EXISTS elements_type_check;

ALTER TABLE elements
ADD CONSTRAINT elements_type_check
CHECK (type IN (
  'text', 'number', 'date', 'checkbox', 'radio', 'dropdown',
  'textarea', 'image', 'label', 'barcode', 'qr_code',
  'currency', 'tafqeet',
  'signature', 'table'
));

-- Create Supabase Storage bucket for signatures (large signature uploads)
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES (
  'signatures',
  'signatures',
  false,
  524288,
  '["image/png"]'
) ON CONFLICT (id) DO NOTHING;