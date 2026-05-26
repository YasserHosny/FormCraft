# Quickstart: Digital Signatures

## Prerequisites

- Backend dependencies installed from `formcraft-backend/requirements.txt`
- Frontend dependencies installed in `formcraft-frontend/`
- Supabase database available with existing FormCraft migrations applied
- An admin or designer user with an organization and at least one published template

## Backend Validation

1. Apply the migration:

   ```bash
   cd formcraft-backend
   supabase db push
   ```

2. Run backend tests:

   ```bash
   cd formcraft-backend
   pytest tests/unit/test_digital_signature_service.py tests/unit/test_signer_identity_service.py tests/unit/test_signature_evidence_service.py tests/integration/test_digital_signature_routes.py
   ```

3. Start the API:

   ```bash
   cd formcraft-backend
   uvicorn app.main:app --reload
   ```

4. Verify workflow creation with an admin token:

   ```bash
   curl -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"template_id":"...","name":"Test Workflow","is_ordered":true,"expiration_days":7,"decline_policy":"stop","require_all_signers":true}' \
     "http://localhost:8000/api/digital-signatures/workflows"
   ```

5. Create and send a signature request:

   ```bash
   curl -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"workflow_id":"...","submission_id":"...","signers":[{"signer_type":"internal","profile_id":"...","name":"Manager","order_index":0}]}' \
     "http://localhost:8000/api/digital-signatures/requests"

   curl -H "Authorization: Bearer $TOKEN" \
     -X POST \
     "http://localhost:8000/api/digital-signatures/requests/{request_id}/send"
   ```

6. Verify evidence after signing:

   ```bash
   curl -H "Authorization: Bearer $TOKEN" \
     "http://localhost:8000/api/digital-signatures/evidence/{request_id}"
   ```

## Frontend Validation

1. Start the Angular app:

   ```bash
   cd formcraft-frontend
   npm start
   ```

2. Navigate to the Digital Signatures section (admin workflow config and operator request list).

3. Verify in RTL and LTR:

   - Workflow configuration page loads with translated labels.
   - Ordered and parallel signer settings save correctly.
   - Operator can create a signature request from a submission.
   - Request list shows status, expiration, and signer progress.
   - Request detail shows event timeline and allows resend/cancel.
   - Public signer portal opens from invitation link and enforces OTP for external signers.
   - Internal signer portal enforces password re-authentication.
   - Evidence viewer shows document hash and integrity status.
   - Arabic signer-facing messages render correctly.

## Critical Scenarios

- External signers without FormCraft accounts can sign via email OTP without creating an account.
- Ordered workflows unlock the next signer only after the previous completes.
- Decline with `stop` policy halts the workflow; `continue_next` advances anyway.
- Expired requests transition to `expired` and remain auditable.
- Signed documents cannot be silently regenerated without invalidating the evidence package.
- Duplicate signature callbacks/events do not create duplicate signed documents.
- Evidence integrity verification re-computes the hash and reports match/mismatch.

## Implementation Validation Notes

- Focused backend tests pass with the shared backend virtual environment.
- Ruff passes for new F046 backend files.
- `npm run build` contains no F046-specific Angular errors.
