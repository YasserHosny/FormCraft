/**
 * TypeScript interfaces for Feedback Threading & Replies (Feature 014).
 * Single source of truth for all Angular consumers of this feature.
 * Mirrors the Pydantic schemas in formcraft-backend/app/schemas/reply.py.
 */

export interface ReplyCreateRequest {
  text_content: string;
}

export interface ReplyResponse {
  id: string;
  author_role: 'admin' | 'user';
  author_name: string;
  text_content: string;
  created_at: string;
}

export interface ThreadResponse {
  replies: ReplyResponse[];
  has_earlier: boolean;
}

export interface MyFeedbackItem {
  id: string;
  page_url: string;
  text_content: string;
  status: string;
  submitted_at: string;
  reply_count: number;
  has_unread_admin_reply: boolean;
}

export interface MyFeedbackResponse {
  results: MyFeedbackItem[];
  total: number;
  page: number;
  page_size: number;
}

export interface NotificationResponse {
  id: string;
  feedback_id: string;
  reply_id: string;
  created_at: string;
  delivered_at: string | null;
  read_at: string | null;
}

export interface NotificationsResponse {
  notifications: NotificationResponse[];
  unread_count: number;
}
