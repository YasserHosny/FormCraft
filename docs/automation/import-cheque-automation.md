# Import Cheque Automation (DevTools)

## Preconditions
- Backend running: `http://127.0.0.1:8000`
- Frontend running: `http://localhost:4200`
- Dev credentials in `formcraft-frontend/.env.local`:
  - `FC_TEST_EMAIL`
  - `FC_TEST_PASSWORD`
- Optional automation flag (either):
  - Query param: `?automation=1`
  - Runtime: `window.FC_AUTOMATION = true`

## Steps (Chrome DevTools MCP)
1. Open the login page: `http://localhost:4200/auth/login`.
2. Fill email/password with values from `.env.local` and submit.
3. Wait for the templates list (`/templates`).
4. Click the **first** template’s **استوديو التصميم** button.
5. On the designer page, set automation flag:
   - `window.FC_AUTOMATION = true`
6. Click **Import Cheque**.
7. Wait for **Detections** panel to load:
   - Verify it shows `Detections (N)` and **Accept/Reject** controls.
8. (Optional) Undock panel and drag to verify movable state.
9. Capture screenshot/logs if needed.

## Notes
- If you hit the login page after navigation, re-authenticate and retry step 4.
- The local sample import path is handled by backend preview endpoint; no local path is exposed to the frontend.
