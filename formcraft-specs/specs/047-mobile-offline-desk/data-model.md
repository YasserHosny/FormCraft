# Data Model: Mobile and Offline Form Desk

## OfflineDevice

`id`, `org_id`, `user_id`, `device_fingerprint`, `display_name`, `public_key`, `status`, `last_seen_at`, `revoked_at`, `revoked_by`, audit fields.

## OfflinePolicy

`id`, `org_id`, `max_offline_age_hours`, `max_storage_mb`, `wipe_on_revocation`, `allowed_template_statuses`, audit fields.

## OfflinePackage

`id`, `org_id`, `device_id`, `template_id`, `template_version`, `reference_snapshot_version`, `customer_snapshot_hash`, `expires_at`, audit fields.

## SyncOperation

`id`, `org_id`, `device_id`, `user_id`, `template_id`, `template_version`, `idempotency_key`, `operation_type`, `status`, `payload_digest`, `client_created_at`, `server_received_at`, `submitted_id`, `error_code`, audit fields.

## SyncConflict

`id`, `sync_operation_id`, `conflict_type`, `status`, `blocking_reason`, `resolution`, `resolved_by`, `resolved_at`, audit fields.
