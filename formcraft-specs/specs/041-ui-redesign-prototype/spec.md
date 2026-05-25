# Feature Specification: UI Redesign from Claude Design Prototype

**Feature Branch**: `041-ui-redesign-prototype`
**Created**: 2026-05-26
**Status**: In Progress

## Overview

Convert 8 high-fidelity Claude Design prototype screens into Angular 19 standalone components with Angular Material MD3 styling, Arabic RTL default layout, and feature-based architecture.

## Screens

1. **App Shell** - Toolbar (56px indigo) + Sidebar (232px) per mode
2. **Template List** (Studio) - 4-col card grid with status tabs/filters
3. **Designer Canvas** (Studio) - 3-column Figma-like form designer
4. **Desk Dashboard** - KPIs, pinned templates, recent table, drafts
5. **Form Filler** - A4 paper form + customer picker dialog
6. **Customer Directory** - Table + stat strip + pagination
7. **Analytics Dashboard** (Admin) - Charts + KPIs + performance table
8. **Notification Center** - Dropdown panel from bell icon

## Technical Requirements

- Angular 19 standalone components
- Angular Material / MD3
- Arabic RTL default (logical CSS properties)
- Feature-based structure: shell, studio, desk, admin, shared
- Mock data in separate .data.ts files
- No backend API connections
- SCSS with design tokens (--fc-* variables)
- Design tokens: Indigo #3F51B5, Amber #FFC107, compact density

## Routes

- /ui/studio/templates
- /ui/studio/designer/:pageId
- /ui/desk
- /ui/desk/fill/:templateId
- /ui/desk/customers
- /ui/admin/analytics
