# Database Migrations - Run in Supabase SQL Editor

Your `.env` file is now configured with Supabase Cloud credentials. Next, run these 6 migrations in order.

## How to Run Migrations

1. Go to your Supabase Dashboard: https://app.supabase.com
2. Select your project: `formcraft`
3. Click **SQL Editor** (left sidebar)
4. Click **"New query"**
5. Copy and paste each migration below
6. Click **"Run"** (or Ctrl+Enter)
7. Verify no errors appear
8. Repeat for each migration

---

## Migration 1: Create Profiles Table

```sql
-- Profiles table (extends Supabase auth.users)
CREATE TABLE public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT NOT NULL DEFAULT 'viewer' CHECK (role IN ('admin', 'designer', 'operator', 'viewer')),
    language TEXT NOT NULL DEFAULT 'ar' CHECK (language IN ('ar', 'en')),
    display_name TEXT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID REFERENCES auth.users(id)
);

-- Auto-create profile on new user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, role, language, is_active)
    VALUES (NEW.id, 'viewer', 'ar', true);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION public.handle_new_user();

-- Updated_at trigger
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at();
```

---

## Migration 2: Create Audit Logs Table

```sql
CREATE TABLE public.audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id),
    action TEXT NOT NULL,
    resource_type TEXT NOT NULL,
    resource_id TEXT,
    metadata JSONB DEFAULT '{}',
    ip_address TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_audit_logs_user ON public.audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON public.audit_logs(action);
CREATE INDEX idx_audit_logs_created ON public.audit_logs(created_at DESC);
```

---

## Migration 3: Create Templates Table

```sql
CREATE TABLE public.templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    category TEXT NOT NULL DEFAULT 'general',
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'published')),
    version INTEGER NOT NULL DEFAULT 1,
    language TEXT NOT NULL DEFAULT 'ar' CHECK (language IN ('ar', 'en')),
    country TEXT NOT NULL DEFAULT 'EG' CHECK (country IN ('EG', 'SA', 'AE')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    created_by UUID NOT NULL REFERENCES auth.users(id)
);

CREATE INDEX idx_templates_status ON public.templates(status);
CREATE INDEX idx_templates_created_by ON public.templates(created_by);
CREATE INDEX idx_templates_updated ON public.templates(updated_at DESC);

CREATE TRIGGER templates_updated_at
    BEFORE UPDATE ON public.templates
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at();
```

---

## Migration 4: Create Pages Table

```sql
CREATE TABLE public.pages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES public.templates(id) ON DELETE CASCADE,
    width_mm NUMERIC(7,2) NOT NULL DEFAULT 210,
    height_mm NUMERIC(7,2) NOT NULL DEFAULT 297,
    background_asset TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX idx_pages_template ON public.pages(template_id);

CREATE TRIGGER pages_updated_at
    BEFORE UPDATE ON public.pages
    FOR EACH ROW
    EXECUTE FUNCTION public.update_updated_at();
```

---

## Migration 5: Create Elements Table

```sql
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
```

---

## Migration 6: Enable RLS Policies

```sql
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
```

---

## After Running All 6 Migrations

1. Go to **Table Editor** (left sidebar)
2. Verify these 5 tables exist:
   - `profiles`
   - `audit_logs`
   - `templates`
   - `pages`
   - `elements`

3. Once confirmed, the backend server will automatically connect to Supabase Cloud
4. You can then test the app at http://localhost:4200

## Next Steps

Once migrations are complete, I'll:
1. Restart the backend server
2. Help you create the first admin user
3. Test the full application (signup, login, templates, designer)
