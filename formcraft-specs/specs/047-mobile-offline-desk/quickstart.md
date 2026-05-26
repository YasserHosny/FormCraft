# Quickstart: Mobile and Offline Form Desk

1. Apply `formcraft-backend/migrations/047_mobile_offline_desk.sql`.
2. Run `cd formcraft-backend && pytest tests/unit/test_offline_desk_service.py`.
3. Run `cd formcraft-frontend && npx tsc -p tsconfig.app.json --noEmit`.
4. Open Form Desk at 360px Arabic RTL and 768px English LTR.
5. Save an encrypted offline draft, reload, queue a submission, reconnect, and verify sync or conflict state.
