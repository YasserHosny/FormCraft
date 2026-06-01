-- Store a template card thumbnail reference.
-- The image itself should live in object storage; this column stores the URL or storage path.

ALTER TABLE public.templates
ADD COLUMN IF NOT EXISTS thumbnail_asset TEXT;
