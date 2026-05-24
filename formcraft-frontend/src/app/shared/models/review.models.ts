export interface ElementComment {
  element_key: string;
  comment: string;
}

export interface ReviewQueueItem {
  template_id: string;
  template_name: string;
  category: string;
  status: string;
  version: number;
  designer_id: string;
  designer_name: string | null;
  department_name: string | null;
  submitted_at: string;
  days_waiting: number;
  is_overdue: boolean;
}

export interface ReviewQueueResponse {
  items: ReviewQueueItem[];
  total: number;
  overdue_count: number;
}

export interface GovernanceMetrics {
  pending_count: number;
  approved_awaiting_publish: number;
  avg_turnaround_days: number | null;
  rejection_rate_pct: number | null;
  overdue_count: number;
  total_reviews: number;
  overdue_threshold_days: number;
}

export interface TimelineEvent {
  event: string;
  actor_id: string;
  actor_name: string | null;
  actor_role: string | null;
  timestamp: string;
  comment: string | null;
  element_comments: ElementComment[] | null;
}

export interface TimelineResponse {
  template_id: string;
  template_name: string;
  timeline: TimelineEvent[];
}

export interface ReviewRecord {
  id: string;
  template_id: string;
  reviewer_id: string;
  reviewer_name: string | null;
  action: string;
  comment: string | null;
  element_comments: ElementComment[] | null;
  created_at: string;
}

export interface DefaultReviewer {
  department_id: string;
  reviewer_id: string;
  reviewer_name: string | null;
}
