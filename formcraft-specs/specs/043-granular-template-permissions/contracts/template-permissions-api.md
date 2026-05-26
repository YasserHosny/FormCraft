# Contract: Template Permissions API

## Capabilities

Known capability values: `view`, `edit`, `clone`, `import`, `export`, `submit_review`, `review`, `publish`, `fill`, `print`, `reprint`, `report`.

## PUT /api/admin/template-permissions/templates/{template_id}/policy

Creates or replaces the active policy and grants for one template.

Request:

```json
{
  "name": "Branch policy",
  "description": "Restrict cheque forms",
  "default_import_policy": "admin_only",
  "grants": [
    {
      "effect": "allow",
      "principal_type": "branch",
      "principal_id": "55555555-5555-5555-5555-555555555555",
      "capabilities": ["view", "fill", "print"],
      "lifecycle_states": ["published"]
    },
    {
      "effect": "deny",
      "principal_type": "user",
      "principal_id": "33333333-3333-3333-3333-333333333333",
      "capabilities": ["print"],
      "lifecycle_states": []
    }
  ]
}
```

Response:

```json
{
  "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
  "template_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
  "name": "Branch policy",
  "is_active": true,
  "default_import_policy": "admin_only",
  "grants": []
}
```

## GET /api/template-permissions/templates/{template_id}/decision?capability=fill

Returns the current user's decision for one template action.

Response:

```json
{
  "allowed": true,
  "reason": "allow_grant_matched",
  "capability": "fill",
  "template_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
  "user_id": "11111111-1111-1111-1111-111111111111",
  "matched_grants": [],
  "matched_restrictions": [],
  "role_sources": ["operator"],
  "scope_matches": ["branch"],
  "stale_cache": false
}
```

## GET /api/admin/template-permissions/templates/{template_id}/diagnostics

Query parameters: `user_id`, `capability`.

Returns the same decision body for an admin-selected user-template pair.
