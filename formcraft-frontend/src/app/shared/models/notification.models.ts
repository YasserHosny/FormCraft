export interface Notification {
  id: string;
  type: string;
  title_ar: string;
  title_en: string;
  body_ar: string | null;
  body_en: string | null;
  action_url: string | null;
  source_id: string | null;
  source_type: string | null;
  is_announcement: boolean;
  read_at: string | null;
  created_by: string | null;
  created_at: string;
}

export interface NotificationsListResponse {
  notifications: Notification[];
  total: number;
  page: number;
  page_size: number;
}

export interface UnreadCountResponse {
  unread_count: number;
}

export interface NotificationPreference {
  notification_type: string;
  in_app_enabled: boolean;
  email_enabled: boolean;
  is_default: boolean;
}

export interface PreferencesListResponse {
  preferences: NotificationPreference[];
}

export interface PreferenceUpdate {
  notification_type: string;
  in_app_enabled: boolean;
  email_enabled: boolean;
}

export interface AnnouncementCreate {
  title_ar: string;
  title_en: string;
  body_ar: string | null;
  body_en: string | null;
  target_audience: string;
  target_role: string | null;
  target_department_id: string | null;
}

export interface AnnouncementResponse {
  announcement_id: string;
  recipients_count: number;
  created_at: string;
}

export type NotificationType =
  | 'template_submitted_for_review'
  | 'template_approved'
  | 'template_rejected'
  | 'template_published'
  | 'template_withdrawn'
  | 'template_feedback_received'
  | 'template_feedback_resolved'
  | 'draft_expiring'
  | 'system_announcement';
