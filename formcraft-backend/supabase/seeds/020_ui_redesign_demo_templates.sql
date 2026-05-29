-- Seed enough structural template data for the dual-theme UI redesign.
-- Idempotent: adds one page to templates without pages and lightweight sample
-- fields to pages that have no elements, without replacing user-created data.

DO $$
DECLARE
  template_record RECORD;
  page_record RECORD;
  seeded_page_id UUID;
BEGIN
  FOR template_record IN
    SELECT id
    FROM public.templates t
    WHERE NOT EXISTS (
      SELECT 1 FROM public.pages p WHERE p.template_id = t.id
    )
  LOOP
    INSERT INTO public.pages (
      template_id,
      width_mm,
      height_mm,
      background_asset,
      sort_order
    )
    VALUES (
      template_record.id,
      210,
      297,
      NULL,
      0
    )
    RETURNING id INTO seeded_page_id;

    INSERT INTO public.elements (
      page_id,
      type,
      key,
      label_ar,
      label_en,
      x_mm,
      y_mm,
      width_mm,
      height_mm,
      required,
      direction,
      sort_order
    )
    VALUES
      (seeded_page_id, 'text', 'customer_name', 'اسم العميل', 'Customer name', 20, 30, 90, 8, true, 'auto', 0),
      (seeded_page_id, 'date', 'request_date', 'تاريخ الطلب', 'Request date', 120, 30, 45, 8, true, 'auto', 1),
      (seeded_page_id, 'text', 'notes', 'ملاحظات', 'Notes', 20, 48, 145, 14, false, 'auto', 2);
  END LOOP;

  FOR page_record IN
    SELECT p.id
    FROM public.pages p
    WHERE NOT EXISTS (
      SELECT 1 FROM public.elements e WHERE e.page_id = p.id
    )
  LOOP
    INSERT INTO public.elements (
      page_id,
      type,
      key,
      label_ar,
      label_en,
      x_mm,
      y_mm,
      width_mm,
      height_mm,
      required,
      direction,
      sort_order
    )
    VALUES
      (page_record.id, 'text', 'customer_name', 'اسم العميل', 'Customer name', 20, 30, 90, 8, true, 'auto', 0),
      (page_record.id, 'date', 'request_date', 'تاريخ الطلب', 'Request date', 120, 30, 45, 8, true, 'auto', 1),
      (page_record.id, 'text', 'notes', 'ملاحظات', 'Notes', 20, 48, 145, 14, false, 'auto', 2);
  END LOOP;
END $$;
