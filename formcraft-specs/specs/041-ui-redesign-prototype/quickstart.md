# Quickstart: Dual Theme Experience

## Prerequisites

- Node.js 18+ and Angular CLI
- Running FormCraft backend with Supabase connection
- At least one user account with admin role for full testing

## Development Setup

```bash
cd formcraft-frontend
npm install
ng serve
```

## Key Files to Modify

| File | Purpose |
|------|---------|
| `src/app/core/services/theme-preference.service.ts` | **NEW** — localStorage persistence + route mapper |
| `src/app/app.component.ts` | Theme-aware init redirect |
| `src/app/app-routing.module.ts` | Theme-aware default/wildcard redirect |
| `src/app/shared/components/app-shell/app-shell.component.ts` | Classic shell: use route mapper |
| `src/app/features/ui-redesign/shell/toolbar.component.ts` | New toolbar: all feature parity |
| `src/app/features/ui-redesign/shell/toolbar.component.html` | New toolbar: control bindings |
| `src/app/features/ui-redesign/shell/layout.component.ts` | Dynamic RTL/LTR direction |
| `src/app/features/ui-redesign/shell/sidebar.component.ts` | Remove mock-data, inline nav config |

## Testing Theme Switching

1. Sign in as admin → should land on Classic (`/templates`)
2. Click "الثيم الجديد" in Classic toolbar → should navigate to `/ui/studio/templates`
3. In New toolbar, click "الثيم الكلاسيكي" → should return to `/templates`
4. Refresh page → should stay on last selected theme
5. Sign out and back in → should restore last selected theme
6. Navigate to `/designer/:pageId` in Classic → switch to New → should land on `/ui/studio/designer/:pageId` or fallback
7. Test with operator role → should only see Desk tab in New toolbar

## Verification Checklist

- [ ] No page shows both Classic and New toolbars simultaneously
- [ ] Theme preference survives refresh
- [ ] Role-based tabs match between Classic and New
- [ ] Language toggle works in New toolbar
- [ ] Notification badge shows real count
- [ ] Org logo appears when org has one configured
- [ ] Sidebar items without routes are visually disabled
- [ ] No `mock-data.ts` import in production components
