# Data Model: Granular Template Permissions

## Custom Template Role

- Table: `custom_template_roles`
- Fields: `id`, `org_id`, `key`, `name_ar`, `name_en`, `description_ar`, `description_en`, `capabilities`, `is_active`, `created_by`, `created_at`, `updated_at`
- Validation: `key` is unique per organization; `capabilities` contains known template capability names only.
- Relationships: Assigned to users through `custom_template_role_assignments`.

## Custom Template Role Assignment

- Table: `custom_template_role_assignments`
- Fields: `id`, `org_id`, `role_id`, `user_id`, `starts_at`, `ends_at`, `is_active`, `created_by`, `created_at`, `updated_at`
- Validation: Assignment is active only when role is active, assignment is active, start is absent or in the past, and end is absent or in the future.
- Relationships: Links a profile to a custom role.

## Template Access Policy

- Table: `template_access_policies`
- Fields: `id`, `org_id`, `template_id`, `name`, `description`, `is_active`, `default_import_policy`, `created_by`, `created_at`, `updated_at`
- Validation: One active template policy is evaluated per template; imported templates with no active policy use `admin_only`.
- Relationships: Owns grants in `template_access_grants`.

## Template Access Grant

- Table: `template_access_grants`
- Fields: `id`, `org_id`, `policy_id`, `effect`, `principal_type`, `principal_id`, `capabilities`, `lifecycle_states`, `created_by`, `created_at`, `updated_at`
- Validation: `effect` is `allow` or `deny`; `principal_type` is `base_role`, `custom_role`, `department`, `branch`, or `user`; deny wins over allow.
- Relationships: Evaluated against user profile, custom role assignments, departments, branches, and template lifecycle state.

## Access Decision Record

- Table: `template_access_decisions`
- Fields: `id`, `org_id`, `template_id`, `user_id`, `capability`, `allowed`, `reason`, `matched_grants`, `matched_restrictions`, `stale_cache`, `created_at`
- Validation: Stored for diagnostics and audit export; no authorization depends on old decision rows.
