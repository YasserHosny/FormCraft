# API Contracts: Multi-Tenancy (Organizations, Departments, Branches)

**Date**: 2026-05-17

## Endpoints

### Organizations (Platform Admin)

#### `POST /api/platform/organizations`

Create a new organization.

**Auth**: Platform Admin only  
**Request**:
```json
{
  "name_ar": "البنك الأهلي المصري",
  "name_en": "National Bank of Egypt",
  "default_language": "ar",
  "default_country": "EG",
  "default_currency": "EGP",
  "subscription_tier": "enterprise"
}
```

**Response 201**:
```json
{
  "id": "uuid",
  "name_ar": "البنك الأهلي المصري",
  "name_en": "National Bank of Egypt",
  "logo_url": null,
  "primary_color": null,
  "default_language": "ar",
  "default_country": "EG",
  "default_currency": "EGP",
  "custom_domain": null,
  "settings": { "approval_workflow_enabled": false, "draft_expiry_days": 7, ... },
  "subscription_tier": "enterprise",
  "is_active": true,
  "created_at": "2026-05-17T10:00:00Z"
}
```

---

#### `GET /api/platform/organizations`

List all organizations.

**Auth**: Platform Admin only  
**Response 200**: Array of org objects with user_count, template_count summaries

---

#### `PATCH /api/platform/organizations/:id`

Update org details (platform admin level).

**Auth**: Platform Admin only

---

### Organization Settings (Org Admin)

#### `GET /api/org/settings`

Get current org settings and profile.

**Auth**: Org Admin  
**Response 200**:
```json
{
  "id": "uuid",
  "name_ar": "البنك الأهلي المصري",
  "name_en": "National Bank of Egypt",
  "logo_url": "https://storage.../org/logo.png",
  "primary_color": "#003366",
  "settings": {
    "approval_workflow_enabled": true,
    "draft_expiry_days": 14,
    "data_retention_months": 84,
    "allowed_file_types": ["image/png", "image/jpeg"],
    "max_batch_size": 500,
    "customer_profiles_enabled": true,
    "hijri_date_support": false,
    "notification_preferences": { "email": true, "in_app": true }
  }
}
```

---

#### `PATCH /api/org/settings`

Update org settings.

**Auth**: Org Admin  
**Request** (partial):
```json
{
  "primary_color": "#004488",
  "settings": {
    "draft_expiry_days": 30,
    "approval_workflow_enabled": true
  }
}
```

**Response 200**: Updated org settings  
**Errors**: 422, 403

---

#### `POST /api/org/logo`

Upload org logo.

**Auth**: Org Admin  
**Content-Type**: multipart/form-data  
**Response 200**: `{ "logo_url": "https://storage.../org/logo.png" }`

---

### Departments

#### `POST /api/departments`

Create a department.

**Auth**: Org Admin  
**Request**:
```json
{
  "name_ar": "الخدمات المصرفية للأفراد",
  "name_en": "Retail Banking"
}
```

**Response 201**: Department object  
**Errors**: 422, 403

---

#### `GET /api/departments`

List departments for current org.

**Auth**: Any authenticated  
**Query Params**: `include_inactive` (boolean, default false)  
**Response 200**:
```json
{
  "items": [
    { "id": "uuid", "name_ar": "...", "name_en": "Retail Banking", "is_active": true, "branch_count": 5, "user_count": 20 }
  ]
}
```

---

#### `PATCH /api/departments/:id`

Update a department.

**Auth**: Org Admin  
**Response 200**: Updated department

---

#### `DELETE /api/departments/:id`

Soft-delete a department (set is_active=false).

**Auth**: Org Admin  
**Response 200**: `{ "id": "uuid", "is_active": false }`  
**Errors**: 409 "Department has active users — reassign before deactivating"

---

### Branches

#### `POST /api/departments/:dept_id/branches`

Create a branch under a department.

**Auth**: Org Admin  
**Request**:
```json
{
  "name_ar": "فرع القاهرة الرئيسي",
  "name_en": "Cairo Main Branch",
  "location": "1 Champollion St, Downtown Cairo"
}
```

**Response 201**: Branch object

---

#### `GET /api/departments/:dept_id/branches`

List branches for a department.

**Auth**: Any authenticated  
**Response 200**: Array of branch objects with user_count

---

#### `GET /api/branches`

List all branches for current org (flat, cross-department).

**Auth**: Any authenticated  
**Response 200**: Array of branch objects with department_name

---

#### `PATCH /api/branches/:id`

Update a branch.

**Auth**: Org Admin

---

#### `DELETE /api/branches/:id`

Soft-delete a branch.

**Auth**: Org Admin  
**Errors**: 409 "Branch has active users — reassign before deactivating"

---

### User Invitations

#### `POST /api/invitations`

Send a user invitation.

**Auth**: Org Admin  
**Request**:
```json
{
  "email": "ahmed@bank.eg",
  "role": "operator",
  "department_id": "uuid",
  "branch_id": "uuid"
}
```

**Response 201**:
```json
{
  "id": "uuid",
  "email": "ahmed@bank.eg",
  "role": "operator",
  "department_id": "uuid",
  "branch_id": "uuid",
  "status": "pending",
  "expires_at": "2026-05-20T10:00:00Z"
}
```

**Side effect**: Sends invitation email with link `{app_url}/invite/{token}`  
**Errors**: 422, 409 "User already exists in this org"

---

#### `GET /api/invitations`

List pending invitations for current org.

**Auth**: Org Admin  
**Response 200**: Array of invitation objects

---

#### `DELETE /api/invitations/:id`

Cancel a pending invitation.

**Auth**: Org Admin  
**Response 204**

---

#### `POST /api/invitations/:token/accept`

Accept an invitation (public endpoint, no auth required).

**Request**:
```json
{
  "display_name": "Ahmed Mohamed",
  "password": "SecurePass123!"
}
```

**Response 201**:
```json
{
  "user_id": "uuid",
  "email": "ahmed@bank.eg",
  "role": "operator",
  "org_id": "uuid",
  "department_id": "uuid",
  "branch_id": "uuid"
}
```

**Errors**: 410 "Invitation expired", 409 "Invitation already accepted", 422 (password too weak)

---

### User Management (Enhanced)

#### `GET /api/users`

List users in current org (enhanced).

**Auth**: Org Admin, Branch Manager  
**Query Params**: `department_id`, `branch_id`, `role`, `is_active`, `page`, `page_size`  
**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "email": "ahmed@bank.eg",
      "display_name": "Ahmed Mohamed",
      "role": "operator",
      "department": { "id": "uuid", "name_en": "Retail Banking" },
      "branch": { "id": "uuid", "name_en": "Cairo Main" },
      "is_active": true,
      "last_login_at": "2026-05-17T08:00:00Z"
    }
  ],
  "total": 50
}
```

---

#### `PATCH /api/users/:id`

Update user assignment (role, department, branch, active status).

**Auth**: Org Admin  
**Request** (partial):
```json
{
  "department_id": "uuid",
  "branch_id": "uuid",
  "role": "branch_manager"
}
```

**Response 200**: Updated user object  
**Errors**: 422, 403, 404

---

#### `POST /api/users/:id/deactivate`

Deactivate a user account.

**Auth**: Org Admin  
**Response 200**: `{ "id": "uuid", "is_active": false }`

---

#### `POST /api/users/:id/activate`

Reactivate a user account.

**Auth**: Org Admin  
**Response 200**: `{ "id": "uuid", "is_active": true }`

---

### Auth (Modified)

#### `POST /api/auth/login` (modified response)

If user's email exists in multiple orgs, return org selector:

**Response 200** (single org — normal):
```json
{
  "access_token": "jwt...",
  "user": { "id": "...", "org_id": "...", "role": "..." }
}
```

**Response 200** (multi-org):
```json
{
  "requires_org_selection": true,
  "organizations": [
    { "id": "uuid", "name_en": "National Bank", "logo_url": "..." },
    { "id": "uuid", "name_en": "Audit Firm", "logo_url": "..." }
  ]
}
```

#### `POST /api/auth/login/select-org`

Complete login after org selection.

**Request**: `{ "org_id": "uuid" }`  
**Response 200**: Normal login response with JWT containing selected org_id claim

---

### Org Branding (Public)

#### `GET /api/branding/:domain`

Get org branding for a custom domain (used by login page).

**Auth**: None (public)  
**Response 200**:
```json
{
  "org_name_ar": "البنك الأهلي",
  "org_name_en": "National Bank",
  "logo_url": "https://...",
  "primary_color": "#003366"
}
```

**Response 404**: No org configured for this domain

## Error Response Format

Standard FormCraft format:
```json
{
  "detail": "Human-readable error message",
  "errors": [{ "field": "email", "message": "User already exists in this organization" }]
}
```
