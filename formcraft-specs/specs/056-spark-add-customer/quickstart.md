# Quickstart: F056 — Spark Add Customer

## Prerequisites

- Node.js 20+, Angular CLI 19
- Local FormCraft frontend running (`ng serve` or `npm start` in `formcraft-frontend/`)
- Supabase local instance or staging credentials in `environment.ts`

## Branch

```bash
git checkout 056-spark-add-customer
```

## Run the frontend

```bash
cd formcraft-frontend
npm install
npm start
```

Navigate to `http://localhost:4200/ui/desk/customers/new` and log in as an operator-role user.

## Verify the feature

1. The form renders natively (no "not yet available" placeholder).
2. Save with required fields only → redirected to Classic customer detail.
3. Save with a duplicate identifier → inline error beneath the Identifier field.
4. Submit with empty required fields → inline validation errors, no network call.
5. Click Cancel → returns to `/ui/desk/customers`.
6. Switch UI language to Arabic → all labels/placeholders are in Arabic, layout is RTL.

## Run tests

```bash
cd formcraft-frontend
npx ng test --include="**/add-customer.component.spec.ts"
```
