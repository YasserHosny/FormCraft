export interface GovernanceTemplate {
  id: string;
  name: string;
  category: string;
  status: string;
  version: number;
  designer_id: string;
  designer_name: string | null;
  department_id: string | null;
  department_name: string | null;
  quality_score: number | null;
  updated_at: string;
  created_at: string;
}

export interface GovernanceTemplateListResponse {
  items: GovernanceTemplate[];
  total: number;
  page: number;
  page_size: number;
}

export interface BulkActionRequest {
  action: string;
  template_ids: string[];
  dry_run: boolean;
  confirm_published?: boolean;
  new_designer_id?: string;
  new_category?: string;
}

export interface BulkActionPreviewItem {
  template_id: string;
  template_name: string;
  current_status: string;
  warning: string | null;
}

export interface BulkActionResponse {
  action: string;
  dry_run: boolean;
  affected_count: number;
  warnings: string[];
  items: BulkActionPreviewItem[];
}

export interface ComplianceMetric {
  template_id: string;
  template_name: string;
  validator_coverage_pct: number;
  bilingual_label_pct: number;
  help_text_coverage_pct: number;
  tab_order_defined: boolean;
  quality_score: number;
  is_stale: boolean;
  last_modified: string;
}

export interface ComplianceDashboardResponse {
  avg_quality_score: number;
  total_templates: number;
  validator_coverage_pct: number;
  bilingual_coverage_pct: number;
  stale_count: number;
  templates: ComplianceMetric[];
}

export interface RegulatoryAlert {
  event_id: string;
  validator_key: string;
  change_summary: string;
  effective_date: string;
  affected_template_count: number;
}
