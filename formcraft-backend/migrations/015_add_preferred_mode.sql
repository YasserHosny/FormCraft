ALTER TABLE profiles
ADD COLUMN preferred_mode TEXT
CHECK (preferred_mode IN ('studio', 'desk', 'admin'))
DEFAULT NULL;

COMMENT ON COLUMN profiles.preferred_mode IS
  'Last-used product mode. NULL means use role default.';