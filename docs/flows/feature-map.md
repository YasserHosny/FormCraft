# FormCraft — Feature Map

> System-level view of how all 14 features connect, which roles own them, and how data flows between modules.

---

## Feature dependency graph

```mermaid
graph TD
    F01["F01 · Auth & Users"]
    F02["F02 · i18n / RTL"]
    F03["F03 · Templates"]
    F04["F04 · Design Studio"]
    F05["F05 · AI Suggest"]
    F06["F06 · PDF Engine"]
    F07["F07 · Validation Lib"]
    F08["F08 · Security / Audit"]
    F09["F09 · Performance"]
    F10["F10 · Tafqeet"]
    F11["F11 · Feedback Widget"]
    F12["F12 · Search & Labels"]
    F13["F13 · Rich Media"]
    F14["F14 · Threading"]

    F01 --> F02
    F01 --> F03
    F01 --> F11
    F03 --> F04
    F04 --> F05
    F04 --> F10
    F04 --> F06
    F05 --> F07
    F06 --> F07
    F11 --> F12
    F11 --> F13
    F11 --> F14
    F01 -.->|"audit events"| F08
    F03 -.->|"audit events"| F08
    F04 -.->|"audit events"| F08
    F09 -.->|"wraps"| F05
    F09 -.->|"wraps"| F06
```

---

## Role × Feature access matrix

| Feature | Admin | Designer | Operator | Viewer | Any Auth |
|---------|:-----:|:--------:|:--------:|:------:|:--------:|
| F01 Auth | ✅ manage users | ✅ own profile | ✅ own profile | ✅ own profile | — |
| F02 i18n | ✅ | ✅ | ✅ | ✅ | ✅ |
| F03 Templates | ✅ publish | ✅ create/edit draft | 📖 published only | 📖 published only | — |
| F04 Design Studio | ✅ | ✅ | — | — | — |
| F05 AI Suggest | ✅ | ✅ | — | — | — |
| F06 PDF Engine | ✅ | ✅ preview | ✅ export | — | — |
| F07 Validation | system | system | system | system | — |
| F08 Security / Audit | ✅ view logs | — | — | — | — |
| F09 Performance | system / devops | — | — | — | — |
| F10 Tafqeet | ✅ | ✅ configure | — | — | — |
| F11 Feedback Widget | ✅ | ✅ | ✅ | ✅ | ✅ submit |
| F12 Search & Labels | ✅ | — | — | — | — |
| F13 Rich Media | ✅ view | ✅ attach | ✅ attach | ✅ attach | ✅ attach |
| F14 Threading | ✅ reply | — | ✅ reply | ✅ reply | ✅ reply |

---

## Module map (frontend routes → feature)

```mermaid
graph LR
    subgraph "Public"
        login["/auth/login"]
    end

    subgraph "Any authenticated"
        templates["/templates"]
        myFeedback["/my-feedback"]
    end

    subgraph "Admin only"
        adminFeedback["/admin/feedback"]
        adminUsers["/admin/users"]
        auditLogs["/admin/audit-logs"]
    end

    subgraph "Admin + Designer"
        designer["/designer/:pageId"]
    end

    login -->|"F01"| templates
    templates -->|"F03"| designer
    designer -->|"F04"| designer
    templates -->|"F03"| adminFeedback
    adminFeedback -->|"F11 F12 F14"| adminFeedback
    myFeedback -->|"F14"| myFeedback
    adminUsers -->|"F01"| adminUsers
    auditLogs -->|"F08"| auditLogs
```

---

## Data model relationships (simplified)

```mermaid
erDiagram
    profiles ||--o{ templates : owns
    templates ||--o{ template_pages : contains
    template_pages ||--o{ template_elements : contains
    template_elements ||--o| template_elements : "tafqeet links to"
    profiles ||--o{ feedback_submissions : submits
    feedback_submissions ||--o{ feedback_images : has
    feedback_submissions ||--o| feedback_submissions : "audio_url / video_url"
    feedback_submissions ||--o{ feedback_labels : "tagged with"
    labels ||--o{ feedback_labels : defines
    feedback_submissions ||--o{ feedback_replies : "thread"
    feedback_replies }o--|| profiles : "authored by"
    profiles ||--o{ feedback_notifications : receives
    feedback_notifications }o--|| feedback_replies : "triggered by"
    profiles ||--o{ audit_logs : generates
```

---

## API surface summary

| Domain | Base path | Auth required | Role gate |
|--------|-----------|:-------------:|:---------:|
| Auth | `/api/auth/*` | partial | — |
| Users | `/api/users/*` | ✅ | admin (manage), self (read/update) |
| Templates | `/api/templates/*` | ✅ | role-based per operation |
| Elements | `/api/templates/{id}/pages/{p}/elements/*` | ✅ | admin / designer |
| AI | `/api/ai/suggest` | ✅ | admin / designer |
| PDF | `/api/pdf/render/{id}` | ✅ | admin / designer / operator |
| Admin feedback | `/api/admin/feedback/*` | ✅ | admin |
| Admin labels | `/api/admin/labels/*` | ✅ | admin |
| Feedback (user) | `/api/feedback/*` | ✅ | any authenticated |
| My feedback | `/api/my-feedback` | ✅ | any authenticated |
| Notifications | `/api/notifications/*` | ✅ | any authenticated |
| Health | `/api/health` | — | — |
| Audit | `/api/admin/audit-logs` | ✅ | admin |
