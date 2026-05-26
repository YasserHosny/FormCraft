export interface RetentionPolicy {
  id: string;
  org_id: string;
  name: { ar: string; en: string };
  data_class: string;
  scope_json: Record<string, unknown>;
  action: 'archive' | 'purge' | 'mask' | 'retain';
  period_days: number;
  legal_basis: string | null;
  approval_required: boolean;
  effective_date: string;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface RetentionJob {
  id: string;
  policy_id: string;
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed';
  started_at: string | null;
  completed_at: string | null;
  batch_size: number;
  checkpoint_cursor: string | null;
  evaluated_count: number;
  actioned_count: number;
  error_count: number;
  error_log: any[];
  skipped_records: any[];
  manifest_id: string | null;
  resumed_from_job_id: string | null;
  created_at: string;
  updated_at: string;
}

export interface LegalHold {
  id: string;
  org_id: string;
  hold_type: 'investigation' | 'dispute' | 'regulatory';
  scope_type: 'submission' | 'customer' | 'template' | 'export' | 'audit_evidence';
  scope_id: string;
  reason: string;
  expiry_date: string | null;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface ArchiveManifest {
  id: string;
  job_id: string;
  record_count: number;
  schema_location: string;
  cold_storage_uri: string | null;
  sha256_hash: string;
  integrity_status: 'verified' | 'failed' | 'pending';
  restore_conditions: Record<string, unknown>;
  created_at: string;
}

export interface PrivacyRequest {
  id: string;
  org_id: string;
  request_type: 'export' | 'delete' | 'mask' | 'restrict';
  scope_type: 'customer' | 'submission';
  scope_id: string;
  status: 'pending' | 'approved' | 'rejected' | 'completed' | 'failed';
  conflict_hold_id: string | null;
  resolution: Record<string, unknown> | null;
  created_by: string;
  created_at: string;
  updated_at: string;
}

export interface PreviewResult {
  affected_count: number;
  date_range: { oldest: string; newest: string };
  affected_forms: string[];
  blocked_records: number;
  blocked_reason: string;
  downstream_references: Record<string, number>;
}
