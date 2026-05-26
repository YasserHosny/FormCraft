# Research: Mobile and Offline Form Desk

- **Decision**: Use IndexedDB with WebCrypto envelope encryption. **Rationale**: It supports structured offline payloads and avoids plaintext persistence.
- **Decision**: Keep backend authoritative for policy, revocation, template version, permission, and duplicate conflict checks. **Rationale**: Offline clients cannot reliably know central state.
- **Decision**: Use one idempotency key per queued submission. **Rationale**: Safe retries after timeout without duplicate submissions.
- **Decision**: Default policy is 7 days, 250 MB, wipe on revocation. **Rationale**: Balances resilience and device-loss risk.
- **Decision**: Block automatic submission on conflicts. **Rationale**: Prevents silent submission under stale template, reference, customer, or permission state.
