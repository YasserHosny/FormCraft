# Data Model: Dual Theme Experience

No database schema changes required. This feature operates entirely at the frontend application layer using existing entities.

## Entities Referenced (existing — no modifications)

| Entity | Table | Used By |
|--------|-------|---------|
| User | `profiles` | Toolbar user display, role filtering, notification count |
| Organization | `organizations` + `org_settings` | Org logo in toolbar |
| Template | `templates` | Template list, sidebar badge count |
| Notification | via `MyFeedbackService` | Toolbar notification badge |

## New Client-Side State

| State | Storage | Format | Lifecycle |
|-------|---------|--------|-----------|
| Theme Preference | `localStorage` key `fc_theme_preference` | `"classic"` \| `"new"` | Written on theme switch; read on app init, refresh, login redirect. Cleared on explicit user action only (not on logout — preference survives re-login). |
