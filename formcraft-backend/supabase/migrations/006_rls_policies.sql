-- =====================
-- Profiles RLS
-- =====================
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "admin_full_profiles" ON public.profiles
    FOR ALL USING (
        EXISTS (SELECT 1 FROM public.profiles p WHERE p.id = auth.uid() AND p.role = 'admin')
    );

CREATE POLICY "own_profile_select" ON public.profiles
    FOR SELECT USING (id = auth.uid());

CREATE POLICY "own_profile_update" ON public.profiles
    FOR UPDATE USING (id = auth.uid())
    WITH CHECK (id = auth.uid());

-- =====================
-- Templates RLS
-- =====================
ALTER TABLE public.templates ENABLE ROW LEVEL SECURITY;

CREATE POLICY "admin_all_templates" ON public.templates
    FOR ALL USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
    );

CREATE POLICY "designer_select_templates" ON public.templates
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'designer')
        AND (created_by = auth.uid() OR status = 'published')
    );

CREATE POLICY "designer_insert_templates" ON public.templates
    FOR INSERT WITH CHECK (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'designer')
        AND created_by = auth.uid()
    );

CREATE POLICY "designer_update_templates" ON public.templates
    FOR UPDATE USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'designer')
        AND created_by = auth.uid() AND status = 'draft'
    );

CREATE POLICY "designer_delete_templates" ON public.templates
    FOR DELETE USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'designer')
        AND created_by = auth.uid() AND status = 'draft'
    );

CREATE POLICY "readonly_published_templates" ON public.templates
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role IN ('operator', 'viewer'))
        AND status = 'published'
    );

-- =====================
-- Pages RLS
-- =====================
ALTER TABLE public.pages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "admin_all_pages" ON public.pages
    FOR ALL USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
    );

CREATE POLICY "designer_pages" ON public.pages
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.templates t
            JOIN public.profiles p ON p.id = auth.uid()
            WHERE t.id = template_id
            AND p.role = 'designer'
            AND t.created_by = auth.uid()
            AND t.status = 'draft'
        )
    );

CREATE POLICY "read_published_pages" ON public.pages
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.templates t
            WHERE t.id = template_id AND t.status = 'published'
        )
    );

-- =====================
-- Elements RLS
-- =====================
ALTER TABLE public.elements ENABLE ROW LEVEL SECURITY;

CREATE POLICY "admin_all_elements" ON public.elements
    FOR ALL USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
    );

CREATE POLICY "designer_elements" ON public.elements
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.pages pg
            JOIN public.templates t ON t.id = pg.template_id
            JOIN public.profiles p ON p.id = auth.uid()
            WHERE pg.id = page_id
            AND p.role = 'designer'
            AND t.created_by = auth.uid()
            AND t.status = 'draft'
        )
    );

CREATE POLICY "read_published_elements" ON public.elements
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.pages pg
            JOIN public.templates t ON t.id = pg.template_id
            WHERE pg.id = page_id AND t.status = 'published'
        )
    );

-- =====================
-- Audit Logs RLS (admin only)
-- =====================
ALTER TABLE public.audit_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "admin_audit_logs" ON public.audit_logs
    FOR ALL USING (
        EXISTS (SELECT 1 FROM public.profiles WHERE id = auth.uid() AND role = 'admin')
    );

-- Service role can always insert (for backend audit logging)
CREATE POLICY "service_insert_audit" ON public.audit_logs
    FOR INSERT WITH CHECK (true);
