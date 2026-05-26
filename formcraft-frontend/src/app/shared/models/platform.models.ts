export interface OrganizationSummary {
  id: string;
  name_ar: string;
  name_en?: string;
  subscription_tier: string;
  status: string;
  active_users_count: number;
  templates_count: number;
  submissions_this_month: number;
  created_at: string;
}

export interface OrganizationCreate {
  name_ar: string;
  name_en?: string;
  default_language?: string;
  default_country?: string;
  default_currency?: string;
  subscription_tier?: string;
  domain?: string;
}

export interface OrganizationUpdate {
  name_ar?: string;
  name_en?: string;
  default_language?: string;
  default_country?: string;
  default_currency?: string;
  subscription_tier?: string;
  domain?: string;
  logo_url?: string;
  branding?: Record<string, unknown>;
}

export interface OrganizationDetail extends OrganizationSummary {
  default_language: string;
  default_country: string;
  default_currency: string;
  domain?: string;
  logo_url?: string;
  branding?: Record<string, unknown>;
  total_submissions: number;
  storage_usage?: string;
  updated_at: string;
}

export interface FirstAdminInvite {
  email: string;
}

export interface TierLimitAlert {
  org_id: string;
  org_name: string;
  tier: string;
  limit_type: string;
  current_usage: number;
  limit_value: number;
  threshold_pct: number;
}

export interface SubmissionVolumePoint {
  month: string;
  count: number;
}

export interface PlatformMetrics {
  total_orgs: number;
  total_users: number;
  total_submissions: number;
  orgs_by_tier: Record<string, number>;
  submission_volume_trend: SubmissionVolumePoint[];
  recently_created_orgs: OrganizationSummary[];
  tier_limit_alerts: TierLimitAlert[];
}

export interface PaginatedOrganizations {
  items: OrganizationSummary[];
  total: number;
  page: number;
  page_size: number;
}
