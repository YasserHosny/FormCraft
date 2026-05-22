# FormCraft — Feature Map

> System-level view of how all 25 features connect, which roles own them, and how data flows between modules.

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
    F15["F15 · Mode Switching"]
    F16["F16 · Operator Dashboard"]
    F17["F17 · Form Filler"]
    F18["F18 · Submission History"]
    F19["F19 · Template Versioning"]
    F20["F20 · Template Feedback"]
    F21["F21 · Signature + Table"]
    F22["F22 · Advanced Validation"]
    F23["F23 · Overlay Print Mode"]
    F24["F24 · Reference Data"]
    F25["F25 · Multi-Tenancy"]

    F01 --> F02
    F01 --> F03
    F01 --> F11
    F01 --> F15
    F01 --> F25
    F03 --> F04
    F03 --> F19
    F04 --> F05
    F04 --> F10
    F04 --> F06
    F04 --> F21
    F04 --> F24
    F05 --> F07
    F06 --> F07
    F06 --> F23
    F07 --> F22
    F11 --> F12
    F11 --> F13
    F11 --> F14
    F15 --> F16
    F16 --> F17
    F17 --> F18
    F17 --> F20
    F19 -.->|"lineage tracking"| F03
    F20 -.->|"designer panel"| F04
    F25 -.->|"org scoping"| F03
    F25 -.->|"org scoping"| F23
    F25 -.->|"org scoping"| F24
    F21 -.->|"new types"| F06
    F22 -.->|"conditions"| F21
    F01 -.->|"audit events"| F08
    F03 -.->|"audit events"| F08
    F04 -.->|"audit events"| F08
    F09 -.->|"wraps"| F05
    F09 -.->|"wraps"| F06
```

---

## Role x Feature access matrix

| Feature | Platform Admin | Org Admin | Designer | Branch Mgr | Operator | Viewer | Any Auth |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| F01 Auth | ✅ all | ✅ manage users | ✅ own profile | ✅ own profile | ✅ own profile | ✅ own profile | — |
| F02 i18n | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| F03 Templates | ✅ | ✅ publish | ✅ create/edit | 📖 published | 📖 published | 📖 published | — |
| F04 Design Studio | ✅ | ✅ | ✅ | — | — | — | — |
| F05 AI Suggest | ✅ | ✅ | ✅ | — | — | — | — |
| F06 PDF Engine | ✅ | ✅ | ✅ preview | ✅ export | ✅ export | — | — |
| F07 Validation | system | system | system | system | system | system | — |
| F08 Security / Audit | ✅ | ✅ view logs | — | — | — | — | — |
| F09 Performance | system | system | — | — | — | — | — |
| F10 Tafqeet | ✅ | ✅ | ✅ configure | — | — | — | — |
| F11 Feedback Widget | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ submit |
| F12 Search & Labels | ✅ | ✅ | — | — | — | — | — |
| F13 Rich Media | ✅ | ✅ view | ✅ attach | ✅ attach | ✅ attach | ✅ attach | ✅ attach |
| F14 Threading | ✅ | ✅ reply | — | ✅ reply | ✅ reply | ✅ reply | ✅ reply |
| F15 Mode Switching | ✅ all modes | ✅ all modes | ✅ Studio+Desk | ✅ Desk | ✅ Desk | — | — |
| F16 Operator Dashboard | — | ✅ view | — | ✅ view | ✅ primary | — | — |
| F17 Form Filler | — | ✅ fill | — | ✅ fill | ✅ primary | — | — |
| F18 Submission History | — | ✅ org-wide | — | ✅ dept-scoped | ✅ own | — | — |
| F19 Template Versioning | — | ✅ publish/archive | ✅ create versions | — | — | — | — |
| F20 Template Feedback | — | ✅ overview | ✅ resolve | — | ✅ submit | — | — |
| F21 Signature + Table | ✅ | ✅ | ✅ configure | — | ✅ fill | — | — |
| F22 Advanced Validation | system | system | ✅ configure | system | system | system | — |
| F23 Overlay Print | ✅ | ✅ profiles | ✅ overlay flag | ✅ print | ✅ print | — | — |
| F24 Reference Data | ✅ | ✅ manage lists | ✅ bind dropdowns | ✅ use | ✅ use | — | — |
| F25 Multi-Tenancy | ✅ create orgs | ✅ org admin | ✅ scoped | ✅ scoped | ✅ scoped | ✅ scoped | — |

---

## Module map (frontend routes -> feature)

```mermaid
graph LR
    subgraph "Public"
        login["/auth/login"]
        branding["/auth/branding/:domain"]
        inviteAccept["/invite/:token"]
    end

    subgraph "Mode: Form Desk /desk"
        desk["/desk"]
        deskFill["/desk/fill/:templateId"]
        deskHistory["/desk/history"]
    end

    subgraph "Mode: Design Studio /studio"
        studioTemplates["/studio/templates"]
        designer["/designer/:pageId"]
    end

    subgraph "Mode: Admin Console /admin"
        adminFeedback["/admin/feedback"]
        adminTemplateFeedback["/admin/template-feedback"]
        adminUsers["/admin/users"]
        adminDepts["/admin/departments"]
        adminInvitations["/admin/invitations"]
        adminOrgSettings["/admin/settings"]
        adminRefData["/admin/reference-data"]
        adminPrinter["/admin/printer-profiles"]
        auditLogs["/admin/audit-logs"]
    end

    subgraph "Any Authenticated"
        templates["/templates"]
        myFeedback["/my-feedback"]
    end

    login -->|"F01 F25"| desk
    login -->|"F01 F25"| studioTemplates
    login -->|"F01 F25"| templates
    inviteAccept -->|"F25"| login
    branding -->|"F25"| login
    desk -->|"F16"| deskFill
    deskFill -->|"F17"| deskHistory
    studioTemplates -->|"F03 F19"| designer
    designer -->|"F04 F21 F24"| designer
    adminFeedback -->|"F11 F12 F14"| adminFeedback
    adminTemplateFeedback -->|"F20"| adminTemplateFeedback
    adminRefData -->|"F24"| adminRefData
    adminPrinter -->|"F23"| adminPrinter
    adminUsers -->|"F01 F25"| adminUsers
    adminDepts -->|"F25"| adminDepts
    adminInvitations -->|"F25"| adminInvitations
    adminOrgSettings -->|"F25"| adminOrgSettings
    auditLogs -->|"F08"| auditLogs
    myFeedback -->|"F14"| myFeedback
```

---

## Data model relationships (simplified)

```mermaid
erDiagram
    organizations ||--o{ departments : contains
    departments ||--o{ branches : contains
    organizations ||--o{ profiles : employs
    profiles }o--o| departments : "assigned to"
    profiles }o--o| branches : "assigned to"
    organizations ||--o{ user_invitations : issues
    organizations ||--o{ templates : owns
    profiles ||--o{ templates : creates
    templates ||--o{ template_pages : contains
    template_pages ||--o{ template_elements : contains
    template_elements ||--o| template_elements : "tafqeet links to"
    templates }o--o| departments : "scoped to"
    templates ||--o{ templates : "lineage (parent_version_id)"
    organizations ||--o{ reference_lists : owns
    reference_lists ||--o{ reference_entries : contains
    template_elements }o--o| reference_lists : "dropdown binds to"
    organizations ||--o{ printer_profiles : owns
    organizations ||--o{ submissions : contains
    submissions }o--o| branches : "tagged with"
    submissions }o--|| templates : "references version"
    organizations ||--o{ drafts : contains
    profiles ||--o{ drafts : saves
    profiles ||--o{ operator_pins : bookmarks
    profiles ||--o{ feedback_submissions : submits
    feedback_submissions ||--o{ feedback_images : has
    feedback_submissions ||--o{ feedback_replies : "thread"
    feedback_replies }o--|| profiles : "authored by"
    profiles ||--o{ feedback_notifications : receives
    profiles ||--o{ template_feedback : submits
    template_feedback }o--|| templates : "references version"
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
| Template feedback | `/api/template-feedback/*` | ✅ | operator (submit), designer (resolve), admin (overview) |
| Notifications | `/api/notifications/*` | ✅ | any authenticated |
| Desk dashboard | `/api/desk/dashboard` | ✅ | operator / admin |
| Desk templates | `/api/desk/templates` | ✅ | operator / admin |
| Desk pins | `/api/desk/pins/*` | ✅ | operator |
| Desk drafts | `/api/desk/drafts/*` | ✅ | operator |
| Submissions | `/api/desk/submissions/*` | ✅ | operator (own), admin (org-wide) |
| Health | `/api/health` | — | — |
| Audit | `/api/admin/audit-logs` | ✅ | admin |
| Organizations | `/api/organizations/*` | ✅ | platform admin |
| Org Settings | `/api/org-settings` | ✅ | org admin |
| Departments | `/api/departments/*` | ✅ | org admin |
| Branches | `/api/branches/*` | ✅ | org admin |
| Invitations | `/api/invitations/*` | ✅ / partial | org admin (manage), public (accept) |
| Printer Profiles | `/api/printer-profiles/*` | ✅ | admin |
| Reference Lists | `/api/reference-lists/*` | ✅ | admin (manage), any auth (dropdown) |
| Branding | `/api/auth/branding/{domain}` | — | public |
