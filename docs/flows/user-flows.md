# FormCraft — Cross-Cutting User Flows

> Flows and rules that apply across all features.

---

## Role hierarchy

```mermaid
graph TD
    Admin["🔑 Admin\nFull system access\nUser management\nAudit logs\nFeedback dashboard"]
    Designer["🎨 Designer\nCreate & edit own templates\nCanvas editor\nAI suggestions\nTafqeet\nPDF preview/export"]
    Operator["⚙️ Operator\nView published templates\nExport PDF\nSubmit & reply to feedback"]
    Viewer["👁 Viewer\nView published templates only\nSubmit & reply to feedback"]
    AnyAuth["🙋 Any Authenticated\nSubmit feedback\nView /my-feedback\nSwitch language"]

    Admin --> Designer
    Designer --> Operator
    Operator --> Viewer
    Viewer --> AnyAuth
```

---

## Route guard matrix

| Route | Guard | Allowed roles |
|-------|-------|:-------------:|
| `/auth/login` | — | public |
| `/templates` | AuthGuard | any authenticated |
| `/designer/:pageId` | AuthGuard + RoleGuard | admin, designer |
| `/admin/feedback` | AuthGuard + RoleGuard | admin |
| `/admin/users` | AuthGuard + RoleGuard | admin |
| `/admin/audit-logs` | AuthGuard + RoleGuard | admin |
| `/my-feedback` | AuthGuard | any authenticated |

---

## Session lifecycle

```mermaid
sequenceDiagram
    participant U as User / Browser
    participant FE as Frontend
    participant API as Backend API
    participant SB as Supabase Auth

    U->>FE: Open /auth/login
    FE->>API: POST /api/auth/login {email, password}
    API->>SB: verifyCredentials()
    SB-->>API: JWT access_token + refresh_token
    API-->>FE: 200 {access_token, refresh_token}
    FE->>FE: store tokens in localStorage
    FE->>API: GET /api/users/me
    API-->>FE: {id, email, role, language, display_name}
    FE->>U: Redirect to /templates

    Note over FE,API: Later — token expiry
    FE->>API: any protected request → 401
    FE->>API: POST /api/auth/refresh {refresh_token}
    API-->>FE: new access_token + refresh_token
    FE->>API: retry original request

    U->>FE: Logout
    FE->>API: POST /api/auth/logout
    FE->>FE: clearSession() — remove tokens
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
