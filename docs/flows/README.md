# FormCraft — Feature Flows

> Structured documentation of every user journey, system flow, and wireflow across all 26 features.
> Last updated: 2026-05-24

---

## How to read this folder

| File | What it covers |
|------|---------------|
| [feature-map.md](feature-map.md) | System-level feature dependency graph, role-feature matrix |
| [user-flows.md](user-flows.md) | Cross-cutting flows: role hierarchy, error handling, RTL/bilingual |
| [comprehensive-flow.md](comprehensive-flow.md) | End-to-end platform flow across all 26 features |
| [f01-auth.md](f01-auth.md) | Authentication & User Management |
| [f02-i18n.md](f02-i18n.md) | Internationalization & RTL Support |
| [f03-templates.md](f03-templates.md) | Template Domain Model |
| [f04-design-studio.md](f04-design-studio.md) | Design Studio (Canvas Editor) |
| [f05-ai-suggestions.md](f05-ai-suggestions.md) | AI Smart Control Suggestion |
| [f06-pdf-engine.md](f06-pdf-engine.md) | PDF Rendering Engine |
| [f07-validation.md](f07-validation.md) | Arabic-Specific Validation Library |
| [f08-security.md](f08-security.md) | Security & Audit Logging |
| [f09-performance.md](f09-performance.md) | Performance & Production Hardening |
| [f10-tafqeet.md](f10-tafqeet.md) | Tafqeet Control (Amount-to-Words) |
| [f11-feedback-widget.md](f11-feedback-widget.md) | Customer Feedback Widget |
| [f12-feedback-labels.md](f12-feedback-labels.md) | Feedback Dashboard Search & Labels |
| [f13-feedback-media.md](f13-feedback-media.md) | Feedback Rich Media |
| [f14-feedback-threading.md](f14-feedback-threading.md) | Feedback Threading & Replies |
| [f15-mode-switching.md](f15-mode-switching.md) | Mode Switching UX |
| [f16-operator-dashboard.md](f16-operator-dashboard.md) | Operator Dashboard (Form Desk) |
| [f17-form-filler.md](f17-form-filler.md) | Form Filler |
| [f18-submission-history.md](f18-submission-history.md) | Submission History & Reprint |
| [f19-template-versioning.md](f19-template-versioning.md) | Template Versioning & Cloning |
| [f20-template-feedback.md](f20-template-feedback.md) | Template Feedback |
| [f21-new-element-types.md](f21-new-element-types.md) | New Element Types (Signature + Table) |
| [f22-advanced-validation.md](f22-advanced-validation.md) | Advanced Form Validation & Conditions |
| [f23-overlay-print-mode.md](f23-overlay-print-mode.md) | Overlay Print Mode & Printer Profiles |
| [f24-reference-data.md](f24-reference-data.md) | Reference Data Manager |
| [f25-multi-tenancy.md](f25-multi-tenancy.md) | Multi-Tenancy (Orgs, Departments, Branches) |
| [f26-form-import-ocr.md](f26-form-import-ocr.md) | Form Import & OCR Detection |

---

## Feature dependency overview

```
Auth (F01) ──────────────────────────────────────────────────┐
 ├── i18n (F02)                                              │
 ├── Templates (F03) ──► Design Studio (F04)                 │
 │                          ├── AI Suggest (F05)             │
 │                          ├── Tafqeet (F10)                │
 │                          ├── New Elements (F21)           │
 │                          ├── Ref Data Binding (F24)       │
 │                          └── PDF Engine (F06)             │
 │                                ├── Validation (F07)       │
 │                                │     └── Adv. Valid (F22) │
 │                                └── Overlay Print (F23)    │
 ├── Template Versioning (F19) ◄── Templates (F03)           │
 ├── Template Feedback (F20) ◄── Studio (F04) + Desk (F17)   │
 ├── Mode Switching (F15) ──► Nav bar & route guards          │
 │     ├── Operator Dashboard (F16)                          │
 │     │     └── Form Filler (F17)                           │
 │     │           └── Submission History (F18)              │
 │     └── Admin Console                                     │
 ├── Security / Audit (F08) ◄──── all features               │
 ├── Performance (F09) ◄──── all features                    │
 ├── Feedback Widget (F11) ◄─────────────────────────────────┘
 │        ├── Search & Labels (F12)
 │        ├── Rich Media (F13)
 │        └── Threading (F14)
 ├── Multi-Tenancy (F25) ──► Orgs, Departments, Branches
 └── Form Import / OCR (F26) ◄── Design Studio (F04)
```

---

## Quick navigation by role

| I am a... | Start reading |
|---------|--------------|
| **Platform Admin** | [F25](f25-multi-tenancy.md) → [F01](f01-auth.md) → [F08](f08-security.md) |
| **Org Admin** | [F25](f25-multi-tenancy.md) → [F15](f15-mode-switching.md) → [F24](f24-reference-data.md) → [F23](f23-overlay-print-mode.md) |
| **Designer** | [F03](f03-templates.md) → [F04](f04-design-studio.md) → [F19](f19-template-versioning.md) → [F21](f21-new-element-types.md) → [F22](f22-advanced-validation.md) |
| **Operator** | [F15](f15-mode-switching.md) → [F16](f16-operator-dashboard.md) → [F17](f17-form-filler.md) → [F18](f18-submission-history.md) |
| **Branch Manager** | [F25](f25-multi-tenancy.md) → [F16](f16-operator-dashboard.md) → [F18](f18-submission-history.md) |
| **All users** | [F02](f02-i18n.md) → [F11](f11-feedback-widget.md) → [F14](f14-feedback-threading.md) → [F20](f20-template-feedback.md) |
