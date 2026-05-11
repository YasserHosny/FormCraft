# FormCraft — Feature Flows

> Structured documentation of every user journey, system flow, and wireflow across all 14 features.
> Last updated: 2026-05-11

---

## How to read this folder

| File | What it covers |
|------|---------------|
| [feature-map.md](feature-map.md) | System-level feature dependency graph, role–feature matrix |
| [user-flows.md](user-flows.md) | Cross-cutting flows: role hierarchy, error handling, RTL/bilingual |
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

---

## Feature dependency overview

```
Auth (F01) ──────────────────────────────────────┐
 ├── i18n (F02)                                   │
 ├── Templates (F03) ──► Design Studio (F04)      │
 │                          ├── AI Suggest (F05)  │
 │                          ├── Tafqeet (F10)     │
 │                          └── PDF Engine (F06)  │
 │                                └── Validation (F07)
 ├── Security / Audit (F08) ◄──── all features    │
 ├── Performance (F09) ◄──── all features         │
 └── Feedback Widget (F11) ◄──────────────────────┘
          ├── Search & Labels (F12)
          ├── Rich Media (F13)
          └── Threading (F14)
```

---

## Quick navigation by role

| I am a… | Start reading |
|---------|--------------|
| **Admin** | [F01](f01-auth.md) → [F08](f08-security.md) → [F11](f11-feedback-widget.md) → [F12](f12-feedback-labels.md) → [F14](f14-feedback-threading.md) |
| **Designer** | [F03](f03-templates.md) → [F04](f04-design-studio.md) → [F05](f05-ai-suggestions.md) → [F10](f10-tafqeet.md) → [F06](f06-pdf-engine.md) |
| **Operator / Viewer** | [F03](f03-templates.md) → [F06](f06-pdf-engine.md) |
| **All users** | [F02](f02-i18n.md) → [F11](f11-feedback-widget.md) → [F14](f14-feedback-threading.md) |
