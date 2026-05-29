# Tasks: Dual Theme Experience and UI Redesign Rollout

**Branch**: `codex/fix-ui-redesign-templates` | **Plan**: `plan.md` | **Spec**: `spec.md` (rev 2)

## Task Overview

| # | Task | Priority | Depends On | Status |
|---|------|----------|------------|--------|
| 1 | Create ThemePreferenceService | P1 | — | done |
| 2 | Theme-aware app redirect | P1 | 1 | done |
| 3 | Classic shell: use route mapper | P1 | 1 | done |
| 4 | New toolbar: context-aware theme switch | P1 | 1 | done |
| 5 | New toolbar: role-based tab filtering | P1 | — | done |
| 6 | New toolbar: language toggle + dynamic dir | P1 | — | done |
| 7 | New toolbar: real notification count | P1 | — | done |
| 8 | New toolbar: org logo | P2 | — | done |
| 9 | New toolbar: profile navigation | P2 | — | done |
| 10 | New toolbar: global search integration | P2 | — | done |
| 11 | Sidebar: remove mock-data, inline nav config | P1 | — | done |
| 12 | Sidebar: disabled items + tooltip | P2 | 11 | done |
| 13 | Help menu: actionable or hidden | P2 | — | done |
| 14 | Cleanup: remove hardcoded defaults | P1 | 7 | done |
| 15 | Verify: no mock-data imports in production | P3 | 11, 14 | done |

---

## Task 1: Create ThemePreferenceService

**Priority**: P1 | **Depends on**: — | **Spec refs**: FR-034, FR-035, FR-036

**What**: Create `formcraft-frontend/src/app/core/services/theme-preference.service.ts` with:
- `getPreference(): 'classic' | 'new'` — reads `fc_theme_preference` from localStorage, defaults to `classic`
- `setPreference(theme)` — writes to localStorage
- `mapRouteToTheme(currentUrl, target, userRole)` — implements the Route Equivalence Matrix:
  - `/templates` ↔ `/ui/studio/templates`
  - `/designer/:pageId` ↔ `/ui/studio/designer/:pageId` (preserve pageId)
  - `/desk` ↔ `/ui/desk`
  - `/desk/fill/:templateId` ↔ `/ui/desk/fill/:templateId` (preserve templateId)
  - `/admin/analytics` ↔ `/ui/admin/analytics`
  - `/admin` ↔ `/ui/admin/analytics`
  - Fallback: `getDefaultRoute(target, userRole)`
- `getDefaultRoute(theme, userRole)` — role-based landing page per theme

**Files**:
- CREATE: `formcraft-frontend/src/app/core/services/theme-preference.service.ts`

**Acceptance**: Unit tests pass for all route mappings, localStorage read/write, and fallback behavior.

---

## Task 2: Theme-aware app redirect

**Priority**: P1 | **Depends on**: Task 1 | **Spec refs**: FR-035, FR-032, NFR-002

**What**: Modify `AppComponent.ngOnInit()` and `app-routing.module.ts` so that:
- On app init, if the user is authenticated and on `/` or hits the wildcard, redirect to the saved theme's role-default landing page instead of always `/templates`
- The default redirect (`{ path: '', redirectTo: '/templates' }`) becomes a guard or component that checks `ThemePreferenceService.getPreference()`
- The wildcard redirect similarly checks theme preference

**Files**:
- MODIFY: `formcraft-frontend/src/app/app.component.ts`
- MODIFY: `formcraft-frontend/src/app/app-routing.module.ts`

**Acceptance**: Refreshing after selecting New theme lands on `/ui/studio/templates` (for admin). Refreshing after Classic lands on `/templates`. No flash of wrong theme.

---

## Task 3: Classic shell: use route mapper

**Priority**: P1 | **Depends on**: Task 1 | **Spec refs**: FR-005, FR-020, FR-036

**What**: Replace `AppShellComponent.getRedesignRoute()` with a call to `ThemePreferenceService.mapRouteToTheme(this.router.url, 'new', this.user.role)`. The theme switch link should also call `themePreferenceService.setPreference('new')` before navigating.

**Files**:
- MODIFY: `formcraft-frontend/src/app/shared/components/app-shell/app-shell.component.ts`

**Acceptance**: Switching from `/designer/abc-123` in Classic navigates to `/ui/studio/designer/abc-123` in New. Switching from `/desk` navigates to `/ui/desk`.

---

## Task 4: New toolbar: context-aware theme switch

**Priority**: P1 | **Depends on**: Task 1 | **Spec refs**: FR-005, FR-020, FR-036

**What**: Replace the hardcoded `routerLink="/templates"` on the theme-switch link in `toolbar.component.html` with a dynamic link computed by `ThemePreferenceService.mapRouteToTheme(currentUrl, 'classic', userRole)`. On click, also call `setPreference('classic')`. Similarly update theme switch items in the help menu and user menu.

**Files**:
- MODIFY: `formcraft-frontend/src/app/features/ui-redesign/shell/toolbar.component.ts`
- MODIFY: `formcraft-frontend/src/app/features/ui-redesign/shell/toolbar.component.html`

**Acceptance**: Switching from `/ui/studio/designer/:pageId` goes to `/designer/:pageId`. Switching from `/ui/desk` goes to `/desk`.

---

## Task 5: New toolbar: role-based tab filtering

**Priority**: P1 | **Depends on**: — | **Spec refs**: FR-006, FR-038

**What**: The `tabs` array in `toolbar.component.ts` currently shows all 3 tabs to every user. Add role metadata to each tab and filter `tabs` based on `this.user.role` from `AuthService.currentUser$`.

Tab-role mapping (matching Classic shell):
- Studio: admin, designer
- Desk: admin, branch_manager, operator
- Admin: admin

**Files**:
- MODIFY: `formcraft-frontend/src/app/features/ui-redesign/shell/toolbar.component.ts`

**Acceptance**: Operator user sees only Desk tab. Designer sees Studio and Desk. Admin sees all three.

---

## Task 6: New toolbar: language toggle + dynamic dir

**Priority**: P1 | **Depends on**: — | **Spec refs**: FR-037, FR-016, NFR-004

**What**:
1. Inject `LanguageService` into `ToolbarComponent`
2. Add `currentLang` property tracking current language
3. Add `toggleLanguage()` method calling `languageService.toggleLanguage()`
4. Add a language toggle button/menu-item in the toolbar UI (in user menu, matching Classic)
5. In `LayoutComponent`: change `dir="rtl"` to `[attr.dir]="currentDir"` bound to language service

**Files**:
- MODIFY: `formcraft-frontend/src/app/features/ui-redesign/shell/toolbar.component.ts`
- MODIFY: `formcraft-frontend/src/app/features/ui-redesign/shell/toolbar.component.html`
- MODIFY: `formcraft-frontend/src/app/features/ui-redesign/shell/layout.component.ts`

**Acceptance**: Clicking language toggle in New toolbar switches between Arabic RTL and English LTR. Layout direction updates without reload.

---

## Task 7: New toolbar: real notification count

**Priority**: P1 | **Depends on**: — | **Spec refs**: FR-040, FR-029, FR-030

**What**:
1. Inject `MyFeedbackService` and `FeedbackRealtimeService` into `ToolbarComponent`
2. On init, fetch initial unread count from `myFeedbackService.getNotifications()`
3. Subscribe to `realtimeService.notificationEvents$` to increment count
4. Replace the hardcoded `@Input() unreadCount = 7` with an internally managed count
5. On destroy, clean up realtime subscription

**Files**:
- MODIFY: `formcraft-frontend/src/app/features/ui-redesign/shell/toolbar.component.ts`

**Acceptance**: Notification badge shows real count from API. Badge updates in real-time.

---

## Task 8: New toolbar: org logo

**Priority**: P2 | **Depends on**: — | **Spec refs**: FR-039, FR-029

**What**:
1. Inject `OrgAdminService` into `ToolbarComponent`
2. On init, fetch org settings and extract `logo_url`
3. Display org logo `<img>` before brand name when available (matching Classic shell pattern)

**Files**:
- MODIFY: `formcraft-frontend/src/app/features/ui-redesign/shell/toolbar.component.ts`
- MODIFY: `formcraft-frontend/src/app/features/ui-redesign/shell/toolbar.component.html`
- MODIFY: `formcraft-frontend/src/app/features/ui-redesign/shell/toolbar.component.scss`

**Acceptance**: Org logo appears in New toolbar when org settings include a `logo_url`.

---

## Task 9: New toolbar: profile navigation

**Priority**: P2 | **Depends on**: — | **Spec refs**: FR-041, FR-023

**What**: Add `routerLink="/auth/profile"` to the "الملف الشخصي" menu item in `toolbar.component.html`.

**Files**:
- MODIFY: `formcraft-frontend/src/app/features/ui-redesign/shell/toolbar.component.html`

**Acceptance**: Clicking "الملف الشخصي" in user menu navigates to `/auth/profile`.

---

## Task 10: New toolbar: global search integration

**Priority**: P2 | **Depends on**: — | **Spec refs**: FR-042, FR-023

**What**: Replace the non-functional `<input>` in the toolbar search area with the existing `<fc-global-search-bar>` component. Import `GlobalSearchBarComponent` in the toolbar's standalone imports. Style to match the New toolbar aesthetic.

**Files**:
- MODIFY: `formcraft-frontend/src/app/features/ui-redesign/shell/toolbar.component.ts`
- MODIFY: `formcraft-frontend/src/app/features/ui-redesign/shell/toolbar.component.html`
- MODIFY: `formcraft-frontend/src/app/features/ui-redesign/shell/toolbar.component.scss`

**Acceptance**: Global search in New toolbar is functional, matching Classic shell behavior.

---

## Task 11: Sidebar: remove mock-data, inline nav config

**Priority**: P1 | **Depends on**: — | **Spec refs**: FR-043, FR-030, SC-020

**What**:
1. Move the navigation structure (icons, labels, routes) from `SIDEBAR_DATA` in `mock-data.ts` into inline config within `sidebar.component.ts`
2. Remove the `import { SIDEBAR_DATA } from '../shared/mock-data'` line
3. Remove badge counts that don't have a production API source — keep only structural navigation
4. Remove `SIDEBAR_DATA` export from `mock-data.ts` (keep other exports for test/demo only)

**Files**:
- MODIFY: `formcraft-frontend/src/app/features/ui-redesign/shell/sidebar.component.ts`
- MODIFY: `formcraft-frontend/src/app/features/ui-redesign/shared/mock-data.ts`

**Acceptance**: Sidebar renders correctly without importing mock-data.ts. No hardcoded business counts.

---

## Task 12: Sidebar: disabled items + tooltip

**Priority**: P2 | **Depends on**: Task 11 | **Spec refs**: FR-044, FR-031

**What**: For sidebar items with empty/null routes:
1. Add `[class.disabled]="!item.route"` to the link element
2. Add `[matTooltip]="'قريباً'"` when route is empty
3. Prevent navigation on click for disabled items
4. Add disabled CSS styling (reduced opacity, no pointer cursor)

**Files**:
- MODIFY: `formcraft-frontend/src/app/features/ui-redesign/shell/sidebar.component.html`
- MODIFY: `formcraft-frontend/src/app/features/ui-redesign/shell/sidebar.component.ts` (if click guard needed)
- ADD CSS to sidebar stylesheet

**Acceptance**: Sidebar items without routes are visually grayed out, show "قريباً" on hover, and don't navigate.

---

## Task 13: Help menu: actionable or hidden

**Priority**: P2 | **Depends on**: — | **Spec refs**: FR-023, FR-031

**What**: Update the help menu in `toolbar.component.html`:
- Keep "فتح الثيم الكلاسيكي" as an actionable item (uses route mapper from Task 4)
- Add a disabled "اختصارات لوحة المفاتيح" item with `disabled` attribute
- If neither item is actionable, hide the help button with a tooltip

**Files**:
- MODIFY: `formcraft-frontend/src/app/features/ui-redesign/shell/toolbar.component.html`

**Acceptance**: Help menu has at least one actionable item. Non-actionable items show disabled state.

---

## Task 14: Cleanup: remove hardcoded defaults

**Priority**: P1 | **Depends on**: Task 7 | **Spec refs**: FR-030, SC-010

**What**: Remove `@Input() unreadCount = 7` from toolbar. The count is now managed internally via Task 7. Also remove the `@Input()` decorator since it's no longer passed from parent. Default to `0`.

**Files**:
- MODIFY: `formcraft-frontend/src/app/features/ui-redesign/shell/toolbar.component.ts`

**Acceptance**: No hardcoded business values in toolbar defaults.

---

## Task 15: Verify: no mock-data imports in production

**Priority**: P3 | **Depends on**: Tasks 11, 14 | **Spec refs**: FR-030, SC-020

**What**: Run a grep across all production components under `features/ui-redesign/` to confirm no file imports from `mock-data.ts` except test files (`*.spec.ts`). The `mock-data.ts` file itself may remain for test utilities but must not be referenced by any production component, service, or template.

**Verification command**:
```bash
grep -rn "mock-data" formcraft-frontend/src/app/features/ui-redesign/ --include="*.ts" | grep -v ".spec.ts"
```

**Acceptance**: Zero matches from the grep (excluding spec files).
