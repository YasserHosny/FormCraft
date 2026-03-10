# FormCraft Backend

Python FastAPI backend for the Universal Form Designer & Print Studio.

## Tech Stack

- **Python 3.12** + **FastAPI**
- **Supabase** (Auth, DB, Storage)
- **WeasyPrint** (PDF rendering)
- **AWS Bedrock** (AI suggestions)
- **Pydantic v2** (validation)

## Project Structure

```
app/
├── api/           # FastAPI routes and dependencies
├── core/          # Config, security, audit, middleware
├── models/        # Pydantic domain models
├── schemas/       # Request/response schemas
└── services/      # Business logic (AI, PDF, validators, templates, users)
supabase/
├── migrations/    # SQL migrations
└── seed.sql       # Seed data
tests/
├── unit/          # Unit tests
└── integration/   # Integration tests
```

## Setup

### Prerequisites

- Python 3.12+
- System deps for WeasyPrint: `libpango`, `libcairo`, `libgdk-pixbuf`

### Install

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure

```bash
cp .env.example .env
# Edit .env with your Supabase and AWS credentials
```

### Run

```bash
uvicorn app.main:app --reload --port 8000
```

### Test

```bash
pytest
```

### Docker

```bash
docker build -t formcraft-backend .
docker run -p 8000:8000 --env-file .env formcraft-backend
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/health | Health check |
| POST | /api/auth/login | User login |
| POST | /api/auth/register | Register user (admin) |
| POST | /api/auth/refresh | Refresh token |
| GET | /api/users/me | Get profile |
| PUT | /api/users/me | Update profile |
| CRUD | /api/templates/* | Template management |
| CRUD | /api/templates/pages/* | Page management |
| CRUD | /api/templates/elements/* | Element management |
| POST | /api/ai/suggest-control | AI suggestion |
| POST | /api/pdf/render/{id} | Render PDF |
| GET | /api/pdf/preview/{id} | Preview PDF |
| GET | /api/admin/audit-logs | Query audit logs |

## Documentation

- **[Setup Guide](SETUP_COMPLETE.md)** - Complete setup instructions with credentials and testing
- **[Database ERD](DATABASE_ERD.md)** - Full database schema with relationships and RLS policies
- **[Supabase Setup](SUPABASE_CLOUD_SETUP.md)** - Supabase Cloud configuration guide
- **[Migrations](MIGRATIONS_TO_RUN.md)** - SQL migration scripts

## Features

### Authentication & Authorization
- JWT-based auth via Supabase
- Role-based access control (admin, designer, operator, viewer)
- Audit logging for all actions
- Row-level security (RLS) policies

### Template Management
- Multi-language support (Arabic, English)
- Multi-country support (Egypt, Saudi Arabia, UAE)
- Version control
- Draft/Published workflow

### Form Designer
- 10 element types: text, number, date, currency, dropdown, radio, checkbox, image, QR, barcode
- Millimeter-precision positioning
- Country-specific validators (Egypt phone, Saudi ID, UAE Emirates ID)
- Custom validation rules via JSONB

### AI Integration
- AWS Bedrock integration for field suggestions
- Confidence scoring
- Manual approval required (never auto-applied)
- Fallback to rule-based suggestions

### PDF Export
- WeasyPrint rendering engine
- 10 specialized renderers per element type
- RTL/LTR support
- A4 page size (configurable)

## Testing

**58/58 tests passing** ✅

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/unit/test_validators.py -v
```

### Test Coverage
- **Unit Tests**: Security, dependencies, validators, AI pipeline, PDF renderers
- **Integration Tests**: Health endpoints, auth endpoints

## Environment Variables

```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_KEY=eyJ...
SUPABASE_JWT_SECRET=your-jwt-secret

# AWS Bedrock (optional)
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
AWS_ACCESS_KEY_ID=your-key
AWS_SECRET_ACCESS_KEY=your-secret

# App
CORS_ORIGINS=http://localhost:4200,https://formcraft.iron-sys.com
LOG_LEVEL=info
APP_VERSION=0.1.0
```

## Database Migrations

All migrations are in `supabase/migrations/`:

1. **001_create_profiles.sql** - User profiles with roles
2. **002_create_audit_logs.sql** - Audit logging
3. **003_create_templates.sql** - Form templates
4. **004_create_pages.sql** - Template pages
5. **005_create_elements.sql** - Form elements
6. **006_rls_policies.sql** - Row-level security

See [DATABASE_ERD.md](DATABASE_ERD.md) for complete schema documentation.

## Deployment

### Docker
```bash
docker build -t formcraft-backend .
docker run -p 8000:8000 --env-file .env formcraft-backend
```

### Bunny Magic Containers
Dockerfile is ready for deployment. See deployment guide in specs repo.

## Related Repositories

- **[formcraft-specs](https://github.com/YasserHosny/formcraft-specs)** - Specification and planning documents
- **[formcraft-frontend](https://github.com/YasserHosny/formcraft-frontend)** - Angular 19 frontend

## License

Proprietary - Iron Systems
