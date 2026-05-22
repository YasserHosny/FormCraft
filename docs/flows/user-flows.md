# FormCraft — Cross-Cutting User Flows

> Flows and rules that apply across all features.

---

## Role hierarchy

```mermaid
graph TD
    PlatformAdmin["🌐 Platform Admin\nManage all organizations\nCreate/deactivate orgs\nCross-org visibility"]
    OrgAdmin["🔑 Org Admin\nFull org access\nUser management\nOrg settings\nDepartments & branches\nInvitations\nReference data\nPrinter profiles\nAudit logs\nFeedback dashboard"]
    Designer["🎨 Designer\nCreate & edit own templates\nCanvas editor (signature, table)\nAI suggestions\nTafqeet\nPDF preview/export\nBind reference dropdowns\nConfigure conditions"]
    BranchManager["🏢 Branch Manager\nView dept-scoped templates\nManage branch operations\nExport PDF"]
    Operator["⚙️ Operator\nView published templates\nFill forms (signature, table, bound dropdowns)\nExport PDF\nSubmit & reply to feedback"]
    Viewer["👁 Viewer\nView published templates only\nSubmit & reply to feedback"]
    AnyAuth["🙋 Any Authenticated\nSubmit feedback\nView /my-feedback\nSwitch language"]

    PlatformAdmin --> OrgAdmin
    OrgAdmin --> Designer
    Designer --> BranchManager
    BranchManager --> Operator
    Operator --> Viewer
    Viewer --> AnyAuth
```

---

## Route guard matrix

| Route | Guard | Allowed roles |
|-------|-------|:-------------:|
| `/auth/login` | — | public |
| `/auth/branding/:domain` | — | public |
| `/invite/:token` | — | public |
| `/invite/expired` | — | public |
| `/templates` | AuthGuard | any authenticated |
| `/my-feedback` | AuthGuard | any authenticated |
| **Mode: Design Studio** | | |
| `/studio/templates` | AuthGuard + RoleGuard | admin, designer |
| `/designer/:pageId` | AuthGuard + RoleGuard | admin, designer |
| **Mode: Form Desk** | | |
| `/desk` | AuthGuard + RoleGuard | admin, branch_manager, operator |
| `/desk/fill/:templateId` | AuthGuard + RoleGuard | admin, branch_manager, operator |
| `/desk/history` | AuthGuard + RoleGuard | admin, branch_manager, operator |
| **Mode: Admin Console** | | |
| `/admin/feedback` | AuthGuard + RoleGuard | admin |
| `/admin/template-feedback` | AuthGuard + RoleGuard | admin |
| `/admin/users` | AuthGuard + RoleGuard | org admin |
| `/admin/settings` | AuthGuard + RoleGuard | org admin |
| `/admin/departments` | AuthGuard + RoleGuard | org admin |
| `/admin/invitations` | AuthGuard + RoleGuard | org admin |
| `/admin/reference-data` | AuthGuard + RoleGuard | admin |
| `/admin/printer-profiles` | AuthGuard + RoleGuard | admin |
| `/admin/audit-logs` | AuthGuard + RoleGuard | admin |

---

## Session lifecycle

```mermaid
sequenceDiagram
    participant U as User / Browser
    participant FE as Frontend
    participant API as Backend API
    participant SB as Supabase Auth

    U->>FE: Open /auth/login
    Note over FE: Check custom_domain → GET /api/auth/branding/{domain}
    FE->>FE: Apply org logo + colors if branding found
    U->>FE: Enter email + password → Submit
    FE->>API: POST /api/auth/login {email, password}
    API->>SB: verifyCredentials()
    SB-->>API: JWT access_token + refresh_token
    API->>API: Query active profiles across all orgs

    alt Single org
        API-->>FE: 200 {access_token, refresh_token}
        FE->>FE: store tokens in localStorage
    else Multiple orgs
        API-->>FE: 200 {requires_org_select: true, orgs: [...]}
        FE->>U: Show org selector cards
        U->>FE: Click organization card
        FE->>API: POST /api/auth/login/select-org {org_id}
        API-->>FE: {user_id, org_id, role, display_name}
        FE->>FE: store org context + tokens
    end

    FE->>API: GET /api/users/me
    API-->>FE: {id, email, role, org_id, department_id, branch_id}
    FE->>U: Redirect to /templates

    Note over FE,API: Later — token expiry
    FE->>API: any protected request → 401
    FE->>API: POST /api/auth/refresh {refresh_token}
    API-->>FE: new access_token + refresh_token
    FE->>API: retry original request

    U->>FE: Logout
    FE->>API: POST /api/auth/logout
    FE->>FE: clearSession() — remove tokens + org context
    FE->>U: Redirect to /auth/login
```

---

## Language switching wireflow

```mermaid
flowchart LR
    A[App loads] --> B{stored preference?}
    B -- no --> C[default: Arabic · RTL]
    B -- yes --> D[load stored language]
    C --> E[render UI]
    D --> E

    E --> F{user clicks AR/EN toggle}
    F --> G[TranslateService.use]
    G --> H[load i18n JSON from cache or HTTP]
    H --> I[all translate pipes re-render]
    I --> J[flip document dir rtl/ltr]
    J --> K[PATCH /api/users/me language]
    K --> E
```

---

## Error handling (all features)

| HTTP status | Frontend behaviour |
|-------------|-------------------|
| Network / 5xx | Toast "حدث خطأ، حاول مرة أخرى" |
| 401 Unauthorized | Attempt token refresh → on failure, redirect to `/auth/login` |
| 403 Forbidden | Toast "غير مصرح بهذا الإجراء"; redirect to `/templates` |
| 404 Not Found | Inline empty state or toast |
| 422 Validation | Inline field-level error messages |
| 429 Rate Limited | Submit button disabled; countdown shown until cooldown ends |

---

## RTL / Bilingual consistency rules

- All flows operate equally in Arabic (RTL) and English (LTR)
- Form labels, error messages, toasts, and email notifications are served from the active language's i18n JSON
- Arabic text in PDFs uses Noto Naskh Arabic font with proper Unicode shaping (`arabic-reshaper` + `python-bidi`)
- Western Arabic numerals (0–9) always used; no Eastern Arabic digits
- Missing translation key → key string shown as fallback (no crash)
- Long strings in fixed containers → `text-overflow: ellipsis`; full text on tooltip
