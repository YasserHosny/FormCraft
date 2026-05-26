-- F043: Granular template permissions and custom roles

create table if not exists custom_template_roles (
    id uuid primary key default gen_random_uuid(),
    org_id uuid not null references organizations(id) on delete cascade,
    key text not null,
    name_ar text not null,
    name_en text not null,
    description_ar text,
    description_en text,
    capabilities text[] not null default '{}',
    is_active boolean not null default true,
    created_by uuid references profiles(id),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (org_id, key)
);

create table if not exists custom_template_role_assignments (
    id uuid primary key default gen_random_uuid(),
    org_id uuid not null references organizations(id) on delete cascade,
    role_id uuid not null references custom_template_roles(id) on delete cascade,
    user_id uuid not null references profiles(id) on delete cascade,
    starts_at timestamptz,
    ends_at timestamptz,
    is_active boolean not null default true,
    created_by uuid references profiles(id),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now(),
    unique (org_id, role_id, user_id)
);

create table if not exists template_access_policies (
    id uuid primary key default gen_random_uuid(),
    org_id uuid not null references organizations(id) on delete cascade,
    template_id uuid not null references templates(id) on delete cascade,
    name text not null,
    description text,
    default_import_policy text not null default 'admin_only'
        check (default_import_policy in ('admin_only', 'inherit_policy')),
    is_active boolean not null default true,
    created_by uuid references profiles(id),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create unique index if not exists uq_template_access_policies_active
    on template_access_policies(org_id, template_id)
    where is_active;

create table if not exists template_access_grants (
    id uuid primary key default gen_random_uuid(),
    org_id uuid not null references organizations(id) on delete cascade,
    policy_id uuid not null references template_access_policies(id) on delete cascade,
    effect text not null check (effect in ('allow', 'deny')),
    principal_type text not null check (principal_type in ('base_role', 'custom_role', 'department', 'branch', 'user')),
    principal_id text not null,
    capabilities text[] not null default '{}',
    lifecycle_states text[] not null default '{}',
    created_by uuid references profiles(id),
    created_at timestamptz not null default now(),
    updated_at timestamptz not null default now()
);

create index if not exists idx_template_access_grants_policy
    on template_access_grants(policy_id);

create index if not exists idx_template_access_grants_principal
    on template_access_grants(org_id, principal_type, principal_id);

create table if not exists template_access_decisions (
    id uuid primary key default gen_random_uuid(),
    org_id uuid not null references organizations(id) on delete cascade,
    template_id uuid not null references templates(id) on delete cascade,
    user_id uuid not null references profiles(id) on delete cascade,
    capability text not null,
    allowed boolean not null,
    reason text not null,
    matched_grants jsonb not null default '[]'::jsonb,
    matched_restrictions jsonb not null default '[]'::jsonb,
    stale_cache boolean not null default false,
    created_at timestamptz not null default now()
);

create index if not exists idx_template_access_decisions_lookup
    on template_access_decisions(org_id, template_id, user_id, capability, created_at desc);

alter table custom_template_roles enable row level security;
alter table custom_template_role_assignments enable row level security;
alter table template_access_policies enable row level security;
alter table template_access_grants enable row level security;
alter table template_access_decisions enable row level security;
