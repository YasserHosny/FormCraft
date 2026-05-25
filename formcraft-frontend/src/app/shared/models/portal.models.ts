import { z } from 'zod';

export const PublicPortalSettingsSchema = z.object({
  otp_required: z.boolean(),
  allowed_otp_modes: z.array(z.enum(['sms', 'email'])),
  captcha_enabled: z.boolean(),
  captcha_provider: z.enum(['hcaptcha', 'recaptcha']).nullable(),
  allow_pdf_download: z.boolean(),
});

export const PublicFormSessionSchema = z.object({
  session_token: z.string(),
  template_id: z.string().uuid(),
  template_version: z.number().int(),
  title: z.string(),
  language_default: z.enum(['ar', 'en']),
  fields: z.array(z.record(z.any())),
  settings: PublicPortalSettingsSchema,
});

export const OtpSendRequestSchema = z.object({
  contact_mode: z.enum(['sms', 'email']),
  contact_value: z.string().min(1),
});

export const OtpSendResponseSchema = z.object({
  status: z.literal('sent'),
  expires_at: z.string().datetime(),
});

export const OtpVerifyRequestSchema = z.object({
  code: z.string().min(1),
});

export const OtpVerifyResponseSchema = z.object({
  status: z.literal('verified'),
});

export const PublicSubmissionRequestSchema = z.object({
  field_values: z.record(z.any()),
  captcha_token: z.string().nullable().optional(),
});

export const PublicSubmissionResponseSchema = z.object({
  reference_number: z.string(),
  pdf_download_url: z.string().nullable(),
  email_confirmation_status: z.enum(['not_requested', 'queued', 'sent', 'failed']).nullable(),
});

export const PortalConfigurationSchema = z.object({
  template_id: z.string().uuid(),
  public_slug: z.string().min(1),
  public_url: z.string(),
  public_qr_svg: z.string().nullable(),
  enabled: z.boolean(),
  verification_required: z.boolean(),
  allowed_otp_modes: z.array(z.enum(['sms', 'email'])),
  captcha_enabled: z.boolean(),
  captcha_provider: z.enum(['hcaptcha', 'recaptcha']).nullable(),
  allow_pdf_download: z.boolean(),
  send_email_confirmation: z.boolean(),
  rate_limit_max: z.number().int().min(1),
  rate_limit_window_minutes: z.number().int().min(1),
});

export const PortalConfigurationUpdateSchema = PortalConfigurationSchema;

export const PortalTemplateListResponseSchema = z.object({
  items: z.array(PortalConfigurationSchema),
});

export const PortalAnalyticsResponseSchema = z.object({
  submission_count: z.number().int(),
  otp_sent_count: z.number().int(),
  otp_failure_count: z.number().int(),
  rate_limited_count: z.number().int(),
  email_confirmation_failure_count: z.number().int(),
});

export type PublicPortalSettings = z.infer<typeof PublicPortalSettingsSchema>;
export type PublicFormSession = z.infer<typeof PublicFormSessionSchema>;
export type OtpSendRequest = z.infer<typeof OtpSendRequestSchema>;
export type OtpSendResponse = z.infer<typeof OtpSendResponseSchema>;
export type OtpVerifyRequest = z.infer<typeof OtpVerifyRequestSchema>;
export type OtpVerifyResponse = z.infer<typeof OtpVerifyResponseSchema>;
export type PublicSubmissionRequest = z.infer<typeof PublicSubmissionRequestSchema>;
export type PublicSubmissionResponse = z.infer<typeof PublicSubmissionResponseSchema>;
export type PortalConfiguration = z.infer<typeof PortalConfigurationSchema>;
export type PortalConfigurationUpdate = z.infer<typeof PortalConfigurationUpdateSchema>;
export type PortalTemplateListResponse = z.infer<typeof PortalTemplateListResponseSchema>;
export type PortalAnalyticsResponse = z.infer<typeof PortalAnalyticsResponseSchema>;
