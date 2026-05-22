# Quickstart: Tafqeet Control Development

**Branch**: `10-tafqeet-control` | **Date**: 2026-05-02

---

## Prerequisites

- Python 3.12 with existing venv activated
- Node 20+ with existing `node_modules`
- Supabase CLI for migrations

---

## Backend Setup

```bash
cd formcraft-backend

# Activate venv
source venv/bin/activate

# Install new dependencies
pip install tafqit num2words

# Update requirements.txt
pip freeze | grep -E "tafqit|num2words" >> requirements.txt

# Apply DB migration
# Run via Supabase MCP or CLI:
# supabase migration new tafqeet_element_type
# (copy 009_tafqeet_element_type.sql content)
# supabase db push

# Run tests (TDD — write tests first, they should fail)
pytest tests/services/test_tafqeet_converter.py -v
pytest tests/api/test_tafqeet_route.py -v

# Start backend
uvicorn app.main:app --reload --port 8000
```

## Verify backend

```bash
# Test preview endpoint (requires valid JWT)
curl -X POST http://localhost:8000/api/tafqeet/preview \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"amount": 5500.75, "currency_code": "SAR", "language": "ar", "show_currency": true, "prefix": "none", "suffix": "faqat_la_ghair"}'

# Expected: {"result": "خمسة آلاف وخمسمائة ريال سعودي وخمسة وسبعون هللة فقط لا غير"}
```

---

## Frontend Setup

```bash
cd formcraft-frontend

# No new npm packages required
npm install

# Start dev server
npx ng serve --port 4200
```

## Verify frontend

1. Open http://localhost:4200
2. Log in as Designer
3. Open any template in the Design Studio
4. Verify "تفقيط / In Words" appears in the element toolbox
5. Drag it onto the canvas — should appear with dashed border and lock icon
6. In the property panel, enter a Preview Value — canvas should update within 300ms

---

## Key Files to Implement (in TDD order)

### Backend
1. `tests/services/test_tafqeet_converter.py` — write tests first
2. `app/services/tafqeet/converter.py` — implement until tests pass
3. `tests/api/test_tafqeet_route.py` — write contract tests
4. `app/api/routes/tafqeet.py` + register in `main.py`
5. `app/services/pdf/element_renderers/tafqeet_renderer.py` + register in `__init__.py`
6. `app/models/enums.py` — add `TAFQEET`
7. `migrations/009_tafqeet_element_type.sql`

### Frontend
1. `src/app/models/template.model.ts` — add `'tafqeet'` to `ElementType`
2. `src/app/models/element-defaults.ts` — add tafqeet default
3. `src/app/shared/schemas/tafqeet-formatting.schema.ts` — Zod schema
4. `src/app/features/designer/services/tafqeet.service.ts` — preview API call
5. `src/app/features/designer/components/tafqeet-property-panel/` — new component
6. Update `designer-page.component.ts` — toolbox + canvas rendering + property panel wiring
