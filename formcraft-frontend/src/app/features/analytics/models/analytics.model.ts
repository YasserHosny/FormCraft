export interface TopErrorItem {
  message: string;
  count: number;
}

export interface FieldAnalyticsItem {
  fieldKey: string;
  errorRate: number;
  topErrors: TopErrorItem[];
  emptyRate: number;
  avgFillTimeMs: number | null;
  warning: boolean;
}

export interface FieldAnalyticsResponse {
  templateId: string;
  templateName: string;
  templateVersion: number;
  period: { from: string | null; to: string | null };
  fields: FieldAnalyticsItem[];
  computedAt: string;
}

export interface OperatorAnalyticsItem {
  operatorId: string;
  operatorName: string;
  formsFilled: number;
  avgFillTimeMs: number | null;
  errorRate: number;
  coachingFlag: boolean;
}

export interface OperatorAnalyticsResponse {
  periodType: string;
  period: { from: string | null; to: string | null };
  operators: OperatorAnalyticsItem[];
  orgAverageErrorRate: number;
  computedAt: string;
}

export interface HeatmapItem {
  hour: number;
  dayOfWeek: number;
  submissionCount: number;
}

export interface BusiestHoursResponse {
  heatmap: HeatmapItem[];
  peakHour: number;
  peakDay: number;
  computedAt: string;
}

export interface ComplianceScorecardResponse {
  orgId: string;
  validatorCoveragePct: number;
  bilingualLabelPct: number;
  qualityScoreAvg: number;
  templatesNeedingAttention: number;
  customerDataAccessSpike: boolean;
  computedAt: string;
  cacheExpiresAt: string;
}

export interface NonCompliantTemplateItem {
  templateId: string;
  templateName: string;
  qualityScore: number;
  missingValidators: string[];
  missingBilingualLabels: string[];
}

export interface TemplatesNeedingAttentionResponse {
  templates: NonCompliantTemplateItem[];
}

export interface FunnelData {
  startedCount: number;
  draftCount: number;
  submittedCount: number;
  printedCount: number;
  conversionRates: Record<string, number>;
}

export interface DepartmentUsageItem {
  departmentId: string;
  departmentName: string;
  submittedCount: number;
}

export interface TemplateUsageResponse {
  templateId: string | null;
  templateName: string | null;
  funnel: FunnelData;
  avgFillTimeMs: number | null;
  byDepartment: DepartmentUsageItem[] | null;
  computedAt: string;
}

export interface VersionAdoptionItem {
  version: number;
  day: string;
  count: number;
  pctOfTotal: number;
}

export interface VersionAdoptionResponse {
  templateId: string;
  templateName: string;
  adoption: VersionAdoptionItem[];
}

export interface ExportRequest {
  reportType: 'field_analytics' | 'operator_analytics' | 'compliance_scorecard' | 'template_usage' | 'busiest_hours';
  templateId: string | null;
  fromDate: string | null;
  toDate: string | null;
  format: 'csv' | 'png' | 'pdf';
}

export interface ExportResponse {
  downloadUrl: string;
  expiresAt: string;
}

// ───────────────────────────────────────────
// 054-analytics-real-data — Dashboard Analytics
// ───────────────────────────────────────────

export interface DashboardFilter {
  period: '7d' | '30d' | '90d' | 'yearly';
  departmentId?: string;
  branchId?: string;
}

export interface DashboardSummaryResponse {
  totalFormsFilled: number;
  totalFormsFilledPrev: number;
  deltaPct: number | null;
  activeTemplates: number;
  totalTemplates: number;
  avgFillTimeMs: number | null;
  avgFillTimePrevMs: number | null;
  fillTimeDeltaPct: number | null;
  uniqueCustomers: number;
  newCustomersThisWeek: number;
  period: string;
  cacheExpiresAt: string;
}

export interface TimeSeriesPoint {
  date: string;
  count: number;
}

export interface SubmissionsOverTimeResponse {
  points: TimeSeriesPoint[];
  peakDate: string | null;
  peakCount: number;
  granularity: 'daily' | 'monthly';
  cacheExpiresAt: string;
}

export interface DepartmentShareItem {
  departmentId: string;
  departmentName: string;
  count: number;
  percentage: number;
}

export interface DepartmentDistributionResponse {
  departments: DepartmentShareItem[];
  total: number;
  cacheExpiresAt: string;
}

export interface TopTemplateItem {
  templateId: string;
  templateName: string;
  templateCode: string;
  count: number;
}

export interface TopTemplatesResponse {
  templates: TopTemplateItem[];
  cacheExpiresAt: string;
}
