-- Migration: 008_form_detections
-- Add form_detections table for OCR field detection storage

CREATE TABLE IF NOT EXISTS public.form_detections (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES public.templates(id) ON DELETE CASCADE,
    page_index INT NOT NULL DEFAULT 0,
    detected_fields JSONB NOT NULL DEFAULT '[]'::jsonb,
    page_dimensions JSONB, -- {width, height} in mm
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT form_detections_page_index_check CHECK (page_index >= 0)
);

-- Index for fast lookup by template
CREATE INDEX IF NOT EXISTS idx_form_detections_template_id 
    ON public.form_detections(template_id);

-- Index for cleanup queries (find old detections)
CREATE INDEX IF NOT EXISTS idx_form_detections_created_at 
    ON public.form_detections(created_at);

-- RLS policies
ALTER TABLE public.form_detections ENABLE ROW LEVEL SECURITY;

-- Admins can do everything
CREATE POLICY "Admins can manage all form detections"
    ON public.form_detections
    FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.profiles
            WHERE profiles.id = auth.uid()
            AND profiles.role = 'admin'
        )
    );

-- Designers can manage their own template detections
CREATE POLICY "Designers can manage own template detections"
    ON public.form_detections
    FOR ALL
    TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM public.templates
            WHERE templates.id = form_detections.template_id
            AND templates.created_by = auth.uid()
        )
    );

-- Grant permissions
GRANT SELECT, INSERT, UPDATE, DELETE ON public.form_detections TO authenticated;

-- Add comment
COMMENT ON TABLE public.form_detections IS 'Stores OCR detection results for form import feature. Detections persist until template is saved.';
