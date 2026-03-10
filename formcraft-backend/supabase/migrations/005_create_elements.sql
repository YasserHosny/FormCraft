CREATE TABLE public.elements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    page_id UUID NOT NULL REFERENCES public.pages(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('text','number','date','currency','dropdown','radio','checkbox','image','qr','barcode')),
    key TEXT NOT NULL,
    label_ar TEXT DEFAULT '',
    label_en TEXT DEFAULT '',
    x_mm NUMERIC(7,2) NOT NULL DEFAULT 0,
    y_mm NUMERIC(7,2) NOT NULL DEFAULT 0,
    width_mm NUMERIC(7,2) NOT NULL DEFAULT 50,
    height_mm NUMERIC(7,2) NOT NULL DEFAULT 10,
    validation JSONB DEFAULT '{}',
    formatting JSONB DEFAULT '{}',
    required BOOLEAN NOT NULL DEFAULT false,
    direction TEXT NOT NULL DEFAULT 'auto' CHECK (direction IN ('rtl','ltr','auto')),
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_elements_page ON public.elements(page_id);

CREATE TRIGGER elements_updated_at
    BEFORE UPDATE ON public.elements
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at();
