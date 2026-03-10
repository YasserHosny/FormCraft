# FormCraft Frontend

Angular frontend for the Universal Form Designer & Print Studio.

## Tech Stack

- **Angular 19** (latest LTS)
- **Angular Material** (UI components)
- **Konva.js** (canvas editor)
- **ngx-translate** (i18n with runtime switching)
- **Zod** (runtime validation)
- **RxJS** (reactive state)

## Project Structure

```
src/app/
├── core/              # Singleton services
│   ├── auth/          # AuthService, guards, interceptor
│   ├── i18n/          # DirectionService, LanguageService
│   ├── error-handler/ # GlobalErrorHandler
│   └── services/      # TemplateService
├── shared/            # SharedModule, directives, pipes, Material re-exports
├── models/            # TypeScript interfaces, element defaults
├── features/
│   ├── auth/          # Login page (lazy-loaded)
│   ├── templates/     # Template list (lazy-loaded)
│   └── designer/      # Design studio with Konva canvas (lazy-loaded)
└── app.module.ts      # Root module
```

## Setup

### Prerequisites

- Node.js 20+
- npm 10+

### Install

```bash
npm install
```

### Dev Server

```bash
npm start
# Opens at http://localhost:4200
```

### Build

```bash
npm run build
```

### Test

```bash
npm test
```

### Docker

```bash
docker build -t formcraft-frontend .
docker run -p 80:80 formcraft-frontend
```

## Key Features

- **Arabic-first, RTL-native** — Default direction is RTL, instant language toggle
- **Lazy-loaded modules** — Auth, Templates, Designer loaded on demand
- **Angular Material** — Consistent Material Design components
- **Translation-key architecture** — All strings via ngx-translate (`ar.json`, `en.json`)
- **Role-based routing** — AuthGuard + RoleGuard on all protected routes
- **Global error handler** — MatSnackBar toasts for unhandled errors

## Environment

| File | Purpose |
|------|---------|
| `src/environments/environment.ts` | Development (localhost:8000) |
| `src/environments/environment.prod.ts` | Production (relative /api) |

## Features

### Designer Canvas
- **Pure Konva.js** integration (no Angular wrappers)
- **Element palette** with 10 element types
- **Property inspector** for selected elements
- **Toolbar** with zoom, undo/redo, grid snap
- **Millimeter-precision** positioning
- **RTL/LTR** direction support per element

### Template Management
- **List view** with search and filters
- **Create dialog** with validation
- **Draft/Published** workflow
- **Version control** display
- **Multi-language** and multi-country support

### Authentication
- **Login page** with Supabase Auth
- **Profile page** with language selector
- **Register page** (admin-only)
- **Auth guard** on protected routes
- **Role guard** for admin/designer routes

### Internationalization
- **Runtime language switching** (AR ↔ EN)
- **Auto-direction** directive for inputs
- **Translation keys** (~120 keys per language)
- **RTL/LTR** layout switching

### AI Suggestions
- **Suggestion chips** appear on element selection
- **Confidence score** display
- **Manual approval** required (never auto-applied)
- **Debounced requests** to AI service

## Routes

| Path | Component | Guard | Description |
|------|-----------|-------|-------------|
| `/` | AppComponent | - | Root with app-shell |
| `/auth/login` | LoginComponent | - | Login page |
| `/auth/register` | RegisterComponent | AuthGuard, RoleGuard(admin) | Admin-only registration |
| `/auth/profile` | ProfileComponent | AuthGuard | User profile with language selector |
| `/templates` | TemplateListComponent | AuthGuard | Template list |
| `/designer/:id` | DesignerPageComponent | AuthGuard | Canvas designer |

## Services

### Core Services
- **AuthService** - Login, logout, token management, user state
- **TemplateService** - CRUD operations for templates
- **CanvasService** - Konva stage management, element operations
- **AiSuggestionService** - AI suggestion requests with debounce
- **DirectionService** - RTL/LTR direction management
- **LanguageService** - Language switching (ar/en)

### Guards
- **AuthGuard** - Requires authenticated user
- **RoleGuard** - Requires specific role (admin, designer, etc.)

### Interceptors
- **AuthInterceptor** - Adds JWT token to all API requests

## Components

### Shared Components
- **AppShellComponent** - Toolbar, navigation, language toggle, logout

### Feature Components
- **LoginComponent** - Email/password login form
- **RegisterComponent** - User registration (admin-only)
- **ProfileComponent** - User profile with language selector
- **TemplateListComponent** - Template list with MatDialog for create
- **TemplateCreateDialogComponent** - Create template dialog
- **DesignerPageComponent** - 3-panel layout (palette, canvas, properties)
- **AiSuggestionChipComponent** - AI suggestion display

## Directives
- **AutoDirDirective** - Automatically sets `dir="auto"` on inputs/textareas

## Translation Keys

All UI strings are in `src/assets/i18n/`:
- **ar.json** - Arabic translations (~120 keys)
- **en.json** - English translations (~120 keys)

Example keys:
```json
{
  "APP_TITLE": "FormCraft",
  "LOGIN_TITLE": "تسجيل الدخول",
  "TEMPLATES_LIST": "قائمة النماذج",
  "DESIGNER_CANVAS": "لوحة التصميم"
}
```

## Environment Configuration

```typescript
// src/environments/environment.ts
export const environment = {
  production: false,
  apiUrl: 'http://localhost:8000/api',
  supabaseUrl: 'https://thwjbagnrcasioiymlsi.supabase.co',
  supabaseAnonKey: 'eyJ...'
};
```

## Build & Deployment

### Development Build
```bash
ng build
# Output: dist/formcraft-frontend/
```

### Production Build
```bash
ng build --configuration production
# Optimized bundle with AOT compilation
```

### Docker Deployment
```bash
docker build -t formcraft-frontend .
docker run -p 80:80 formcraft-frontend
# Serves via nginx on port 80
```

### Bunny Magic Containers
Dockerfile is ready for deployment. See deployment guide in specs repo.

## Angular 19 Notes

This project uses **Angular 19** with:
- **NgModule architecture** (not standalone components)
- **Explicit `standalone: false`** on all components/directives
- **Sass with `@use`** instead of deprecated `@import`
- **Strict TypeScript** mode enabled
- **Material 19** components

## Related Repositories

- **[formcraft-specs](https://github.com/YasserHosny/formcraft-specs)** - Specification and planning documents
- **[formcraft-backend](https://github.com/YasserHosny/formcraft-backend)** - FastAPI backend

## License

Proprietary - Iron Systems
