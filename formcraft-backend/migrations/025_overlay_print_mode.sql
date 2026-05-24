-- Template print settings
CREATE TABLE template_print_settings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
  print_mode TEXT NOT NULL DEFAULT 'full' CHECK (print_mode IN ('full', 'overlay', 'both')),
  org_id UUID NOT NULL REFERENCES organizations(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (template_id)
);

ALTER TABLE template_print_settings ENABLE ROW LEVEL SECURITY;
CREATE POLICY template_print_settings_org_isolation ON template_print_settings
  USING (org_id = current_setting('app.current_org_id', true)::UUID);

-- Printer profiles
CREATE TABLE printer_profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  description TEXT,
  x_offset_mm NUMERIC(5,1) NOT NULL DEFAULT 0.0,
  y_offset_mm NUMERIC(5,1) NOT NULL DEFAULT 0.0,
  is_default BOOLEAN NOT NULL DEFAULT false,
  is_active BOOLEAN NOT NULL DEFAULT true,
  org_id UUID NOT NULL REFERENCES organizations(id),
  created_by UUID NOT NULL REFERENCES auth.users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX idx_printer_profiles_default_per_org
  ON printer_profiles(org_id) WHERE is_default = true AND is_active = true;

CREATE INDEX idx_printer_profiles_org ON printer_profiles(org_id);

ALTER TABLE printer_profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY printer_profiles_org_isolation ON printer_profiles
  USING (org_id = current_setting('app.current_org_id', true)::UUID);

-- Add include_in_overlay to elements
ALTER TABLE elements
ADD COLUMN include_in_overlay BOOLEAN NOT NULL DEFAULT true;

COMMENT ON TABLE template_print_settings IS
  'Per-template print mode configuration: full, overlay, or both.';
COMMENT ON TABLE printer_profiles IS
  'Printer calibration profiles with X/Y offset for overlay print alignment.';
COMMENT ON COLUMN printer_profiles.x_offset_mm IS
  'Horizontal offset applied to all element positions in overlay mode. Positive = shift right.';
COMMENT ON COLUMN printer_profiles.y_offset_mm IS
  'Vertical offset applied to all element positions in overlay mode. Positive = shift down.';
COMMENT ON COLUMN elements.include_in_overlay IS
  'Whether this element appears in overlay PDF mode. Default true for data elements, false for decorative.';
