-- F047 Mobile and Offline Form Desk

create table if not exists offline_policies (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null unique references organizations(id) on delete cascade,
  max_offline_age_hours integer not null default 168 check (max_offline_age_hours between 1 and 720),
  max_storage_mb integer not null default 250 check (max_storage_mb between 10 and 2048),
  wipe_on_revocation boolean not null default true,
  allowed_template_statuses text[] not null default array['published'],
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  created_by uuid references profiles(id)
);

create table if not exists offline_devices (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id) on delete cascade,
  user_id uuid not null references profiles(id) on delete cascade,
  device_fingerprint text not null,
  display_name text,
  public_key text not null,
  status text not null default 'active' check (status in ('active', 'revoked', 'wiped')),
  last_seen_at timestamptz,
  revoked_at timestamptz,
  revoked_by uuid references profiles(id),
  revocation_reason text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  created_by uuid references profiles(id),
  unique (org_id, user_id, device_fingerprint)
);

create table if not exists offline_packages (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id) on delete cascade,
  device_id uuid not null references offline_devices(id) on delete cascade,
  template_id uuid not null references templates(id) on delete cascade,
  template_version integer not null,
  reference_snapshot_version text,
  customer_snapshot_hash text,
  expires_at timestamptz not null,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  created_by uuid references profiles(id),
  unique (device_id, template_id, template_version)
);

create table if not exists offline_sync_operations (
  id uuid primary key default gen_random_uuid(),
  org_id uuid not null references organizations(id) on delete cascade,
  device_id uuid not null references offline_devices(id) on delete cascade,
  user_id uuid not null references profiles(id) on delete cascade,
  template_id uuid not null references templates(id),
  template_version integer not null,
  idempotency_key text not null,
  operation_type text not null check (operation_type in ('draft', 'submission', 'attachment', 'status_update')),
  status text not null check (status in ('pending', 'syncing', 'submitted', 'failed', 'conflict')),
  payload_digest text not null,
  client_created_at timestamptz not null,
  server_received_at timestamptz,
  submitted_id uuid,
  error_code text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  created_by uuid references profiles(id),
  unique (org_id, idempotency_key)
);

create table if not exists offline_sync_conflicts (
  id uuid primary key default gen_random_uuid(),
  sync_operation_id uuid not null references offline_sync_operations(id) on delete cascade,
  conflict_type text not null check (conflict_type in ('template_version', 'customer_profile', 'reference_data', 'user_permission', 'duplicate_submission', 'account_status', 'device_revoked')),
  status text not null default 'open' check (status in ('open', 'resolved', 'dismissed')),
  blocking_reason text not null,
  resolution text check (resolution in ('discard', 'reload_template', 'manager_approve', 'retry')),
  resolved_by uuid references profiles(id),
  resolved_at timestamptz,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  created_by uuid references profiles(id)
);

create index if not exists idx_offline_devices_org_user_status on offline_devices(org_id, user_id, status);
create index if not exists idx_offline_packages_device_expires on offline_packages(device_id, expires_at);
create index if not exists idx_offline_sync_operations_device_status on offline_sync_operations(device_id, status);
create index if not exists idx_offline_sync_conflicts_status on offline_sync_conflicts(status);

alter table offline_policies enable row level security;
alter table offline_devices enable row level security;
alter table offline_packages enable row level security;
alter table offline_sync_operations enable row level security;
alter table offline_sync_conflicts enable row level security;

create policy offline_devices_owner_read on offline_devices for select using (user_id = auth.uid());
create policy offline_devices_owner_write on offline_devices for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy offline_packages_owner_read on offline_packages for select using (device_id in (select id from offline_devices where user_id = auth.uid()));
create policy offline_sync_owner_write on offline_sync_operations for all using (user_id = auth.uid()) with check (user_id = auth.uid());
create policy offline_conflicts_owner_read on offline_sync_conflicts for select using (
  sync_operation_id in (select id from offline_sync_operations where user_id = auth.uid())
);
