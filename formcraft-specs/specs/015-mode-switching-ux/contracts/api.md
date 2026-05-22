# API Contract: Mode Switching UX

## Modified Endpoint: `PATCH /api/users/me`

### Request

```json
{
  "preferred_mode": "desk"
}
```

| Field | Type | Required | Values | Notes |
|-------|------|----------|--------|-------|
| preferred_mode | string \| null | optional | "studio", "desk", "admin", null | null resets to role default |

### Response (200 OK)

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "operator@bank.eg",
  "role": "operator",
  "language": "ar",
  "display_name": "أحمد محمد",
  "preferred_mode": "desk"
}
```

### Error Response (422 Unprocessable Entity)

```json
{
  "detail": "Role 'operator' does not have access to mode 'studio'"
}
```

Triggered when: user attempts to set preferred_mode to a mode their role doesn't permit.

## Modified Endpoint: `GET /api/users/me`

### Response (200 OK)

Same as PATCH response — now includes `preferred_mode` field.

## No New Endpoints

Mode configuration is frontend-only (hardcoded mode definitions). No API needed for listing modes or checking permissions — the frontend derives permitted modes from the user's role.
