# F08 — Security & Audit Logging

**Roles**: Admin (view logs) · All users (actions logged automatically)  
**Related**: [F01 Auth](f01-auth.md)

---

## Audit event flow

```mermaid
sequenceDiagram
    participant U as Any User
    participant SVC as Backend Service
    participant DB as Supabase DB
    participant ADM as Admin

    U->>SVC: Perform action (CRUD / login / role change / etc.)
    SVC->>DB: Primary operation (e.g., INSERT template)
    SVC->>DB: INSERT audit_logs row (async — never blocks primary op)
    DB-->>SVC: 201
    SVC-->>U: Success response

    ADM->>SVC: GET /api/admin/audit-logs?user=&action=&from=&to=
    SVC->>DB: SELECT audit_logs filtered
    DB-->>SVC: rows
    SVC-->>ADM: [{timestamp, user, action, resource, ip, metadata}]
    ADM->>SVC: GET audit_logs/:id (expand metadata)
    SVC-->>ADM: { before: {...}, after: {...} }
```

---

## RLS access matrix

```mermaid
graph TD
    subgraph "Supabase Row-Level Security"
        Admin["Admin\nSELECT / INSERT / UPDATE / DELETE\non all rows"]
        Designer["Designer\nSELECT own + published templates\nINSERT / UPDATE / DELETE own drafts"]
        Operator["Operator\nSELECT published templates only"]
        Viewer["Viewer\nSELECT published templates only"]
        AnyUser["Any User\nSELECT / INSERT own profile only"]
        ServiceRole["Service Role Key\nBypasses RLS\n(backend-to-DB only — never exposed to client)"]
    end
```

---

## Flows

### 8.1 Automatic audit logging

```
Any user performs a template CRUD, AI suggestion, authentication, or role-change action
→ Backend middleware / service layer creates AuditLog row:
    user_id, action (CREATE / UPDATE / DELETE / LOGIN / LOGOUT / ROLE_CHANGE / etc.),
    resource_type, resource_id, metadata JSONB (before/after snapshots), ip_address, created_at
→ Audit write failure does NOT block the primary operation
```

### 8.2 Admin views audit logs

```
Admin navigates to GET /api/admin/audit-logs
→ Filter by user, action type, date range
→ Each row shows: timestamp, user, action, resource, IP address
→ Expand row → see full before/after JSON metadata
```

### 8.3 RLS enforcement (data access)

```
Every DB query passes through Supabase RLS:
  Admin       → SELECT / INSERT / UPDATE / DELETE on all rows
  Designer    → SELECT own templates + published; INSERT/UPDATE/DELETE own drafts
  Operator    → SELECT published templates only
  Viewer      → SELECT published templates only
  Any user    → SELECT / INSERT own profile only
Bypassed by service-role key (backend-to-DB calls only; never exposed to client)
```

---

## Logged action types

| Action | Trigger |
|--------|---------|
| `LOGIN` | Successful user login |
| `LOGOUT` | User logout |
| `ROLE_CHANGE` | Admin changes a user's role |
| `CREATE` | Template / element / label created |
| `UPDATE` | Template / element / label updated |
| `DELETE` | Template / element / label deleted |
| `PUBLISH` | Template status changed to published |
| `AI_SUGGEST` | AI suggestion called |
| `AI_TIMEOUT` | AI suggestion timed out |
| `PDF_RENDER` | PDF generated |
