# Tasks: Performance Optimization & Production Hardening

**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Format: `[ID] [Priority] [Story] Description`

## Phase 1: Backend — Caching & Timeout

- [ ] **T09-001** P1 S1 — Verify `app/services/ai/cache.py` is implemented (from spec 05), ensure TTLCache with 1000 max entries and 5min TTL
- [ ] **T09-002** P1 S3 — Verify LLM timeout is 5 seconds with fallback (from spec 05), add explicit test for timeout scenario

## Phase 2: Frontend — Debounce & Error Handling

- [ ] **T09-010** P1 S2 — Verify ai-suggestion.service.ts uses RxJS debounceTime(300) (from spec 05)
- [ ] **T09-011** P1 S5 — Create `src/app/core/error-handler/global-error-handler.ts` — Angular ErrorHandler implementation, catches unhandled errors, shows MatSnackBar toast
- [ ] **T09-012** P1 S5 — Register GlobalErrorHandler in app.module.ts as `{ provide: ErrorHandler, useClass: GlobalErrorHandler }`
- [ ] **T09-013** P1 S5 — Implement auto-save retry: exponential backoff (1s, 2s, 4s), max 3 retries, persistent warning banner on final failure

## Phase 3: Health Check

- [ ] **T09-020** P1 S4 — Create `app/api/routes/health.py` — GET /api/health, checks Supabase connectivity, returns status + version + dependency checks
- [ ] **T09-021** P1 S4 — Add startup validation in `app/main.py` — Verify all required env vars present, fail fast with clear error listing missing vars

## Phase 4: Docker — Backend

- [ ] **T09-030** P1 S4 — Create `formcraft-backend/Dockerfile` — python:3.12-slim base, WeasyPrint system deps, copy fonts, copy app, uvicorn CMD with 4 workers
- [ ] **T09-031** P1 S4 — Create `formcraft-backend/uvicorn.conf.py` — Workers, host, port from env vars
- [ ] **T09-032** P1 S4 — Create `formcraft-backend/.dockerignore` — Exclude tests, .git, __pycache__, .env

## Phase 5: Docker — Frontend

- [ ] **T09-040** P1 S4 — Create `formcraft-frontend/Dockerfile` — Multi-stage: node:20-alpine build stage (npm ci + ng build --configuration=production), nginx:alpine serve stage
- [ ] **T09-041** P1 S4 — Create `formcraft-frontend/nginx.conf` — SPA fallback, /api/ proxy to backend, security headers, gzip
- [ ] **T09-042** P1 S4 — Create `formcraft-frontend/.dockerignore` — Exclude node_modules, .git, dist

## Phase 6: Bunny Deployment Config

- [ ] **T09-050** P1 S4 — Create `formcraft-backend/bunny.yaml` — Bunny Magic Container config: image, port 8000, env vars, health check path
- [ ] **T09-051** P1 S4 — Create `formcraft-frontend/bunny.yaml` — Bunny Magic Container config: image, port 80, custom domain formcraft.iron-sys.com
- [ ] **T09-052** P1 S6 — Configure domain: DNS CNAME for formcraft.iron-sys.com → Bunny container endpoint
- [ ] **T09-053** P1 S6 — Configure SSL: Enable Let's Encrypt on Bunny for formcraft.iron-sys.com, verify HSTS header

## Phase 7: Environment Configuration

- [ ] **T09-060** P1 S4 — Create `formcraft-backend/.env.example` — All required env vars with placeholder values and descriptions
- [ ] **T09-061** P1 S4 — Create `formcraft-frontend/src/environments/environment.ts` — Development API URL (localhost:8000)
- [ ] **T09-062** P1 S4 — Create `formcraft-frontend/src/environments/environment.prod.ts` — Production API URL (formcraft.iron-sys.com/api)

## Phase 8: Frontend Optimization

- [ ] **T09-070** P2 S4 — Configure lazy loading for feature modules: designer, templates, auth (in routing modules)
- [ ] **T09-071** P2 S4 — Verify AOT compilation is enabled in production build config (angular.json)
- [ ] **T09-072** P2 S4 — Verify tree-shaking: check bundle size with `ng build --stats-json`, ensure < 500KB gzipped

## Phase 9: Tests

- [ ] **T09-080** P1 S4 — Write `tests/unit/test_health.py` — Health check with healthy Supabase, health check with unreachable Supabase
- [ ] **T09-081** P1 S4 — Write `tests/unit/test_startup.py` — App fails fast when required env vars are missing
- [ ] **T09-082** P1 S5 — Write unit tests: global-error-handler.spec.ts — HTTP errors show toast, JS errors show toast
- [ ] **T09-083** P1 S4 — Manual deployment test: build both Docker images, run locally with docker-compose, verify end-to-end

## Phase 10: README & Documentation

- [ ] **T09-090** P1 Setup — Create `formcraft-backend/README.md` — Setup instructions, env vars, running locally, running tests
- [ ] **T09-091** P1 Setup — Create `formcraft-frontend/README.md` — Setup instructions, dev server, building, env config
- [ ] **T09-092** P1 Setup — Create `FormCraft/README.md` (specs repo) — Project overview, architecture, links to specs, getting started

## Dependencies & Execution Order

```
T09-001, T09-002 (verify, after spec 05 implementation)
T09-010 (verify, after spec 05 frontend)
T09-011 → T09-012 (error handler → register)
T09-020, T09-021 (parallel: health + startup)
T09-030, T09-031, T09-032 (sequential: backend Docker)
T09-040, T09-041, T09-042 (sequential: frontend Docker)
T09-050, T09-051 (parallel: bunny configs)
T09-052 → T09-053 (DNS → SSL, sequential)
T09-060, T09-061, T09-062 (parallel: env configs)
T09-070, T09-071, T09-072 (sequential: FE optimization)
```

## Parallel Opportunities

- Backend Docker (Phase 4) and Frontend Docker (Phase 5) in parallel
- Both bunny.yaml files (T09-050, T09-051) in parallel
- All env config files (T09-060, T09-061, T09-062) in parallel
- All README files (T09-090, T09-091, T09-092) in parallel
