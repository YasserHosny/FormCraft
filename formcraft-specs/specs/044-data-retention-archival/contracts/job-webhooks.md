# Job Webhooks Contract

## Overview

Retention jobs emit lifecycle events via the existing webhook subscription system (032-data-export-integration). No new webhook infrastructure is required.

## Event Types

| Event | Description | Payload |
|-------|-------------|---------|
| `retention.job.started` | Job transitions from pending to running | `{ job_id, policy_id, started_at }` |
| `retention.job.paused` | Job paused by admin or error threshold | `{ job_id, policy_id, paused_at, checkpoint_cursor }` |
| `retention.job.resumed` | Job resumed from paused/failed | `{ job_id, policy_id, resumed_at, resumed_from_job_id }` |
| `retention.job.completed` | Job finished all batches | `{ job_id, policy_id, manifest_id, actioned_count, skipped_count, completed_at }` |
| `retention.job.failed` | Job encountered unrecoverable error | `{ job_id, policy_id, error_log, failed_at }` |
| `retention.hold.created` | Legal hold placed | `{ hold_id, scope_type, scope_id, hold_type, created_at }` |
| `retention.hold.released` | Legal hold removed | `{ hold_id, released_at }` |
| `retention.manifest.restored` | Archive restore completed | `{ manifest_id, restore_job_id, restored_count, restored_at }` |

## Delivery Guarantees

- At-least-once delivery.
- Webhook consumers must handle duplicate events idempotently using `job_id` + `event` + `timestamp` composite key.
- Failed deliveries retried with exponential backoff (max 5 attempts over 24 hours).

## Subscription

Organizations subscribe to retention events via the existing `/api/v1/webhooks/subscriptions` endpoint by specifying `event_type` in the `retention.*` namespace.
