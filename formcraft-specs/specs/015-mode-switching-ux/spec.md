# Feature Specification: Mode Switching UX

**Feature Branch**: `014-mode-switching-ux`  
**Created**: 2026-05-16  
**Status**: Draft  
**Input**: Top-level navigation between Design Studio, Form Desk, and Admin Console with role-based routing and persistent mode preference

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Role-Based Default Mode on Login (Priority: P1)

When a user logs in, they are automatically directed to the mode appropriate for their role: operators land on Form Desk, designers land on Design Studio, and admins land on Admin Console. This eliminates confusion about where to start and ensures each persona sees their workspace immediately.

**Why this priority**: Without role-based default routing, the platform feels like a single undifferentiated app. This is the foundational UX that makes the two-mode architecture real for end users.

**Independent Test**: Can be fully tested by logging in with different user roles and verifying each lands on the correct dashboard. Delivers immediate value: operators see their form queue, not a template editor.

**Acceptance Scenarios**:

1. **Given** a user with role "operator" logs in, **When** authentication succeeds, **Then** they are redirected to `/desk` (Form Desk dashboard)
2. **Given** a user with role "designer" logs in, **When** authentication succeeds, **Then** they are redirected to `/studio/templates` (Design Studio template library)
3. **Given** a user with role "admin" logs in, **When** authentication succeeds, **Then** they are redirected to `/admin` (Admin Console dashboard)
4. **Given** a user has a stored mode preference that differs from their role default, **When** they log in, **Then** they are redirected to their stored preference instead of the role default

---

### User Story 2 - Mode Switching via Navigation Bar (Priority: P1)

Authenticated users can switch between modes using clearly labeled tabs in the top navigation bar. The active mode is visually indicated, and switching is instant (no page reload). Only modes the user's role permits are shown.

**Why this priority**: Equal to P1 because the mode tabs are the physical manifestation of the two-mode architecture. Without visible mode switching, the architecture exists only in code, not in user experience.

**Independent Test**: Can be tested by clicking each mode tab and verifying the URL changes, the content area updates, and the active tab is highlighted. Verify that unauthorized modes are hidden.

**Acceptance Scenarios**:

1. **Given** an admin user is on `/desk`, **When** they click the "Design Studio" tab, **Then** they navigate to `/studio/templates` without a full page reload and the Design Studio tab becomes active
2. **Given** an operator user views the nav bar, **When** the page loads, **Then** only the "Form Desk" tab is visible (Design Studio and Admin Console tabs are hidden)
3. **Given** a designer user views the nav bar, **When** the page loads, **Then** "Design Studio" and "Form Desk" tabs are visible but "Admin Console" is hidden
4. **Given** an admin user views the nav bar, **When** the page loads, **Then** all three mode tabs are visible

---

### User Story 3 - Mode Preference Persistence (Priority: P2)

The system remembers which mode a user last used and returns them to that mode on subsequent sessions. The preference is stored server-side so it works across devices.

**Why this priority**: Improves daily experience for users who always work in the same mode (most operators), but the system works fine without it (role default handles first-time routing).

**Independent Test**: Can be tested by switching modes, logging out, logging back in, and verifying the user returns to their last-used mode.

**Acceptance Scenarios**:

1. **Given** a designer switches to Form Desk, **When** they log out and log back in, **Then** they land on Form Desk (not Design Studio)
2. **Given** an admin is using Admin Console, **When** they close the browser and reopen it next day, **Then** they resume in Admin Console
3. **Given** a user's stored preference points to a mode they no longer have access to (role downgraded), **When** they log in, **Then** they fall back to their role's default mode

---

### User Story 4 - Route Guards Enforce Mode Access (Priority: P1)

Users cannot access mode routes their role doesn't permit, even by manually typing URLs. Unauthorized route access shows an appropriate message and redirects to the permitted mode.

**Why this priority**: Security requirement — operators must not access Design Studio routes, viewers must not access Admin Console routes. Without this, the multi-mode architecture is cosmetic only.

**Independent Test**: Can be tested by manually navigating to forbidden URLs and verifying the redirect behavior.

**Acceptance Scenarios**:

1. **Given** an operator user manually navigates to `/studio/templates`, **When** the route guard fires, **Then** they see a toast "غير مصرح بهذا القسم" and are redirected to `/desk`
2. **Given** a designer user manually navigates to `/admin/users`, **When** the route guard fires, **Then** they see a toast and are redirected to `/studio/templates`
3. **Given** an unauthenticated user navigates to any protected route, **When** the auth guard fires, **Then** they are redirected to `/auth/login`

---

### User Story 5 - Bilingual Navigation (Priority: P2)

The mode tabs and navigation elements display correctly in both Arabic (RTL) and English (LTR), respecting the user's language preference. Tab order flips for RTL layout.

**Why this priority**: Arabic-first is a core principle, and the nav bar is the most visible UI element. However, it builds on the same i18n infrastructure that already exists.

**Independent Test**: Can be tested by switching language and verifying tab labels, direction, and layout change appropriately.

**Acceptance Scenarios**:

1. **Given** the user's language is Arabic, **When** the nav bar renders, **Then** mode tabs display Arabic labels ("استوديو التصميم", "مكتب النماذج", "لوحة الإدارة") and the bar is RTL-oriented
2. **Given** the user's language is English, **When** the nav bar renders, **Then** mode tabs display English labels ("Design Studio", "Form Desk", "Admin Console") and the bar is LTR-oriented
3. **Given** the user switches language while on any page, **When** the toggle is clicked, **Then** the nav bar re-renders with new language labels without navigation change

---

### Edge Cases

- What happens when a user's role is changed while they are logged in? The session's cached role may be stale. On next API call returning 403, the frontend should refresh the user profile and update visible mode tabs.
- What happens when all three modes are accessed via browser back/forward buttons? Mode state should be properly reflected in browser history so back button returns to the previous mode view.
- What happens when deep-links are shared between users with different roles? If user A shares `/admin/reports/123` with operator B, operator B should be gracefully redirected with a message, not shown a broken page.
- What happens on very narrow screens (mobile)? Mode tabs should collapse into a dropdown or hamburger menu while maintaining the same functionality.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display a persistent top-level navigation bar with mode tabs on all authenticated pages
- **FR-002**: System MUST show only the mode tabs that the current user's role permits (operator: Desk only; designer: Studio + Desk; admin: all three)
- **FR-003**: System MUST visually indicate which mode is currently active (highlighted tab, distinct styling)
- **FR-004**: System MUST navigate to the selected mode's root route on tab click without a full page reload (SPA navigation)
- **FR-005**: System MUST redirect users to their role-appropriate default mode after successful login
- **FR-006**: System MUST persist the user's last-used mode preference to their profile (server-side)
- **FR-007**: System MUST redirect unauthorized route access to the user's permitted default mode with a bilingual toast notification
- **FR-008**: System MUST support URL structure: `/studio/*` for Design Studio, `/desk/*` for Form Desk, `/admin/*` for Admin Console
- **FR-009**: System MUST update browser URL and history when switching modes (enabling back/forward navigation)
- **FR-010**: System MUST display mode tab labels in the user's selected language (Arabic or English)
- **FR-011**: System MUST flip navigation layout direction based on active language (RTL for Arabic, LTR for English)
- **FR-012**: System MUST handle role changes gracefully — if a 403 is received, refresh user profile and update visible tabs

### Non-Functional Requirements

- **NFR-001**: Mode switching MUST complete in under 200ms (no perceptible delay)
- **NFR-002**: Route guards MUST execute before any component renders (no flash of unauthorized content)
- **NFR-003**: Nav bar MUST render within 100ms of page load
- **NFR-004**: Mode preference save MUST be non-blocking (fire-and-forget PATCH to user profile)

### Key Entities

- **User Profile**: Extended with `preferred_mode` field (enum: studio, desk, admin) and `role` (enum: admin, designer, operator, viewer)
- **Mode Configuration**: Maps each mode to: route prefix, label (ar + en), icon, permitted roles, default route within mode
- **Route Guard Result**: Contains: authorized (boolean), redirect_url, toast_message_key

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users land on their correct mode within 1 second of login completion, without any intermediate redirect visible to the user
- **SC-002**: 100% of unauthorized route access attempts result in redirect (zero unauthorized page renders)
- **SC-003**: Mode switching completes in under 200ms as measured by navigation end event
- **SC-004**: All mode tab labels render correctly in both Arabic and English with proper directional layout
- **SC-005**: User mode preference survives logout/login cycle — verified by logging out, logging in, and confirming same mode
- **SC-006**: Browser back/forward buttons correctly navigate mode history without breaking app state
