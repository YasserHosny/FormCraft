# Tasks: Internationalization & RTL Support

**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Format: `[ID] [Priority] [Story] Description`

## Phase 1: Setup

- [ ] **T02-001** P1 Setup — Install ngx-translate: `npm install @ngx-translate/core @ngx-translate/http-loader`
- [ ] **T02-002** P1 Setup — Configure `TranslateModule` in app.module.ts with `HttpLoaderFactory`
- [ ] **T02-003** P1 Setup — Import `BidiModule` from `@angular/cdk/bidi` in app.module.ts

## Phase 2: Core i18n Infrastructure

- [ ] **T02-010** P1 S1 — Create `src/assets/i18n/ar.json` — Arabic translation file with initial keys (common, auth, templates, designer sections)
- [ ] **T02-011** P1 S1 — Create `src/assets/i18n/en.json` — English translation file mirroring ar.json structure
- [ ] **T02-012** P1 S1 — Create `src/app/core/i18n/direction.service.ts` — Manages `dir$` observable, sets `document.documentElement.dir` and `lang`, exposes `currentDir`, `toggleDirection()`
- [ ] **T02-013** P1 S2 — Create `src/app/core/i18n/language.service.ts` — Get/set language, calls TranslateService.use(), persists to user profile API, defaults to "ar"
- [ ] **T02-014** P1 S1 — Update `app.component.ts` — Subscribe to direction.service, set initial direction to RTL on app init

## Phase 3: RTL Styling

- [ ] **T02-020** P1 S1 — Create `src/styles/_direction-mixins.scss` — SCSS mixins: margin-start, padding-start, float-start, border-start
- [ ] **T02-021** P1 S1 — Create `src/styles/_rtl.scss` — RTL-specific global overrides for Angular Material components if needed
- [ ] **T02-022** P1 S5 — Verify Angular Material CDK Bidi integration — mat-sidenav, mat-form-field, mat-toolbar, mat-table render correctly in RTL

## Phase 4: Shared Components & Directives

- [ ] **T02-030** P1 S4 — Create `src/app/shared/directives/auto-dir.directive.ts` — Applies `dir="auto"` to input/textarea elements for mixed-direction content
- [ ] **T02-031** P1 S3 — Create lint rule or script to detect hardcoded strings in Angular templates (simple grep-based check initially)
- [ ] **T02-032** P1 S2 — Create language toggle component in toolbar — MatButtonToggle or MatMenu with AR/EN options, calls language.service

## Phase 5: Tests

- [ ] **T02-040** P1 S1 — Write unit tests: direction.service.spec.ts — direction changes, HTML attribute updates
- [ ] **T02-041** P1 S2 — Write unit tests: language.service.spec.ts — language switching, persistence, default behavior
- [ ] **T02-042** P1 S3 — Write unit tests: verify ar.json and en.json have identical key structures
- [ ] **T02-043** P1 S4 — Write unit tests: auto-dir.directive.spec.ts — dir="auto" applied correctly
- [ ] **T02-044** P2 S5 — Write visual tests: RTL layout verification for key components (login page, template list)

## Dependencies & Execution Order

```
T02-001 → T02-002 → T02-003 (sequential: package install → config)
T02-010, T02-011 (parallel: translation files)
T02-002 → T02-012 → T02-013 → T02-014 (i18n service chain)
T02-020, T02-021 (parallel: SCSS files)
T02-012 → T02-030 (directive needs direction service)
T02-013 → T02-032 (toggle needs language service)
T02-040-044 (tests after implementation)
```

## Parallel Opportunities

- Translation files (T02-010, T02-011) in parallel
- SCSS files (T02-020, T02-021) in parallel
- All unit tests (T02-040 through T02-043) in parallel after implementation
