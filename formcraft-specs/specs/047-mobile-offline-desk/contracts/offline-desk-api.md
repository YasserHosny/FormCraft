# API Contract: Offline Form Desk

- `POST /api/offline-desk/devices`: register device, returns device id, status, and policy.
- `GET /api/offline-desk/packages/manifest?device_id={uuid}`: returns downloadable template manifest and policy.
- `POST /api/offline-desk/sync`: accepts idempotent encrypted queued work and returns submitted or conflict status.
- `POST /api/offline-desk/conflicts/{conflict_id}/resolve`: records conflict resolution.
- `POST /api/offline-desk/devices/{device_id}/revoke`: revokes a device and returns wipe policy.
