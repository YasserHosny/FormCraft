import { z } from 'zod';

export const ExportFormatSchema = z.enum(['csv', 'xlsx', 'json']);
export const ExportScopeSchema = z.enum(['flattened', 'structured']);
export const ExportFiltersSchema = z.object({
  template_id: z.string().uuid().optional(),
  date_from: z.string().optional(),
  date_to: z.string().optional(),
  department_id: z.string().uuid().optional(),
  branch_id: z.string().uuid().optional(),
  operator_id: z.string().uuid().optional(),
  status: z.string().optional(),
});

export const ExportPreviewRequestSchema = z.object({
  filters: ExportFiltersSchema.default({}),
  format: ExportFormatSchema,
  scope: ExportScopeSchema,
});

export const ExportPreviewResponseSchema = z.object({
  matching_count: z.number().int().nonnegative(),
  estimated_file_size_bytes: z.number().int().nonnegative().nullable().optional(),
  can_download: z.boolean(),
  rejection_reason: z.string().nullable().optional(),
  warnings: z.array(z.string()).default([]),
});

export const ExportRequestRecordSchema = z.object({
  id: z.string().uuid(),
  dataset: z.literal('submissions'),
  format: ExportFormatSchema,
  scope: ExportScopeSchema,
  status: z.enum(['previewed', 'completed', 'rejected', 'failed']),
  matching_count: z.number().int().nonnegative(),
  rejection_reason: z.string().nullable().optional(),
  created_at: z.string(),
});

export const ExportScheduleSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  filters: ExportFiltersSchema,
  format: ExportFormatSchema,
  scope: ExportScopeSchema,
  frequency: z.enum(['daily', 'weekly']),
  email_recipients: z.array(z.string().email()).min(1),
  no_data_behavior: z.enum(['send_empty_file', 'send_notice']),
  status: z.enum(['active', 'paused', 'disabled']),
  next_run_at: z.string(),
  last_run_at: z.string().nullable().optional(),
  created_at: z.string(),
  updated_at: z.string(),
});

export const TemplatePackageSchema = z.object({
  package_version: z.string(),
  exported_at: z.string(),
  source_template_id: z.string().uuid().nullable().optional(),
  template_lineage_id: z.string().uuid().nullable().optional(),
  template: z.record(z.unknown()),
  pages: z.array(z.record(z.unknown())),
  elements: z.array(z.record(z.unknown())),
  validators: z.array(z.record(z.unknown())).default([]),
  conditions: z.array(z.record(z.unknown())).default([]),
  reference_bindings: z.array(z.record(z.unknown())).default([]),
  checksum: z.string(),
});

export const PackageImportReviewSchema = z.object({
  can_import: z.boolean(),
  import_mode: z.enum(['new_draft', 'new_version']),
  target_template_id: z.string().uuid().nullable().optional(),
  warnings: z.array(z.string()).default([]),
  remapping_required: z.array(z.record(z.unknown())).default([]),
});

export const IntegrationCredentialSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  key_prefix: z.string(),
  scopes: z.array(
    z.enum(['submissions:read', 'templates:read', 'templates:write', 'webhooks:write']),
  ),
  status: z.enum(['active', 'revoked', 'expired']),
  expires_at: z.string().nullable().optional(),
  last_used_at: z.string().nullable().optional(),
  created_at: z.string(),
});

export const IntegrationCredentialCreatedSchema = IntegrationCredentialSchema.extend({
  secret: z.string(),
});

export const WebhookSubscriptionSchema = z.object({
  id: z.string().uuid(),
  name: z.string(),
  event_type: z.enum(['form_submitted', 'form_printed', 'template_published', 'batch_completed']),
  target_url: z.string().url(),
  signing_secret_prefix: z.string().nullable().optional(),
  status: z.enum(['active', 'paused', 'disabled']),
  created_at: z.string(),
});

export const WebhookDeliverySchema = z.object({
  id: z.string().uuid(),
  subscription_id: z.string().uuid(),
  event_type: z.string(),
  event_id: z.string().uuid(),
  payload_preview: z.record(z.unknown()),
  signature_header: z.string(),
  status: z.enum(['queued', 'delivered', 'failed']),
  attempt_count: z.number().int().nonnegative(),
  next_retry_at: z.string().nullable().optional(),
  last_response_code: z.number().int().nullable().optional(),
  last_response_body_preview: z.string().nullable().optional(),
  created_at: z.string(),
});

export type ExportFilters = z.infer<typeof ExportFiltersSchema>;
export type ExportPreviewRequest = z.infer<typeof ExportPreviewRequestSchema>;
export type ExportPreviewResponse = z.infer<typeof ExportPreviewResponseSchema>;
export type ExportRequestRecord = z.infer<typeof ExportRequestRecordSchema>;
export type ExportSchedule = z.infer<typeof ExportScheduleSchema>;
export type TemplatePackage = z.infer<typeof TemplatePackageSchema>;
export type PackageImportReview = z.infer<typeof PackageImportReviewSchema>;
export type IntegrationCredential = z.infer<typeof IntegrationCredentialSchema>;
export type IntegrationCredentialCreated = z.infer<typeof IntegrationCredentialCreatedSchema>;
export type WebhookSubscription = z.infer<typeof WebhookSubscriptionSchema>;
export type WebhookDelivery = z.infer<typeof WebhookDeliverySchema>;
