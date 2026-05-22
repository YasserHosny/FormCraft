# Implementation Plan: Performance Optimization & Production Hardening

**Branch**: `09-perf-hardening` | **Date**: 2026-02-21 | **Spec**: [spec.md](./spec.md)

## Summary

Implement AI suggestion caching (LRU+TTL), frontend debounce, LLM timeout fallback, Dockerfiles for both repos, Bunny Magic Container deployment configs, health check endpoints, error boundaries, SSL/TLS, and production environment configuration.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript 5.x (frontend)
**Primary Dependencies**: cachetools (backend cache), uvicorn (ASGI server), Docker, nginx (frontend static server)
**Storage**: N/A (caching is in-memory)
**Testing**: pytest (health checks), Playwright (error boundaries)
**Target Platform**: Bunny Magic Containers (Linux amd64)

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| IX. YAGNI | ✅ Pass | No Redis, no distributed cache, no CDN in Phase 1 |
| VIII. Security | ✅ Pass | SSL/TLS, HSTS, env-based secrets |

## Project Structure

### Backend (formcraft-backend)

```text
app/
├── api/routes/
│   └── health.py               # GET /api/health
├── core/
│   └── config.py               # Settings class with env var validation, fail-fast on missing
├── main.py                     # App factory with startup validation

Dockerfile
bunny.yaml
uvicorn.conf.py                 # Workers, host, port config
```

### Frontend (formcraft-frontend)

```text
src/app/
├── core/
│   └── error-handler/
│       ├── global-error-handler.ts     # Angular ErrorHandler implementation
│       └── error-toast.component.ts    # Toast notification for API errors

Dockerfile
bunny.yaml
nginx.conf                      # Static file serving + SPA fallback + security headers
```

### Dockerfiles

```dockerfile
# formcraft-backend/Dockerfile
FROM python:3.12-slim

# WeasyPrint system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0 \
    libcairo2 libffi-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY assets/ assets/
COPY app/ app/

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

```dockerfile
# formcraft-frontend/Dockerfile
FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build -- --configuration=production

FROM nginx:alpine
COPY --from=build /app/dist/formcraft-frontend/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
```

### Health Check Endpoint

```python
# health.py
@router.get("/api/health")
async def health_check(supabase = Depends(get_supabase)):
    checks = {}
    status = "ok"

    # Check Supabase
    try:
        supabase.table("profiles").select("id").limit(1).execute()
        checks["supabase"] = "healthy"
    except Exception:
        checks["supabase"] = "unreachable"
        status = "degraded"

    status_code = 200 if status == "ok" else 503
    return JSONResponse(
        status_code=status_code,
        content={"status": status, "version": settings.APP_VERSION, "checks": checks}
    )
```

### Nginx Config (Frontend)

```nginx
server {
    listen 80;
    server_name formcraft.iron-sys.com;
    root /usr/share/nginx/html;
    index index.html;

    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Security headers
    add_header X-Content-Type-Options nosniff;
    add_header X-Frame-Options DENY;
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;
}
```

### Environment Variables

```bash
# Backend required env vars
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
CORS_ORIGINS=https://formcraft.iron-sys.com
LOG_LEVEL=info
APP_VERSION=1.0.0

# Frontend (build-time)
API_BASE_URL=https://formcraft.iron-sys.com/api
```

### Frontend Error Handler

```typescript
// global-error-handler.ts
@Injectable()
export class GlobalErrorHandler implements ErrorHandler {
    constructor(private snackBar: MatSnackBar) {}

    handleError(error: any): void {
        console.error('Unhandled error:', error);
        if (error?.status) {
            // HTTP error
            this.snackBar.open(
                `Server error (${error.status}). Please try again.`,
                'Dismiss',
                { duration: 5000 }
            );
        } else {
            // JS runtime error
            this.snackBar.open(
                'An unexpected error occurred.',
                'Dismiss',
                { duration: 5000 }
            );
        }
    }
}
```

## Research Notes

- **Bunny Magic Containers**: Supports Docker images, custom domains, SSL via Let's Encrypt. Config via `bunny.yaml`. Free tier available.
- **Frontend bundle size target**: < 500KB gzipped. Angular Material tree-shaking + lazy-loaded feature modules (designer, templates, auth) keeps initial bundle small.
- **Auto-save retry**: Exponential backoff (1s, 2s, 4s) for failed saves. After 3 failures, show persistent warning banner.

## Complexity Tracking

No constitution violations.
