-- Migration 031: Notification Center
-- Feature: 029-notification-center
-- Date: 2026-05-25

-- Create notifications table
CREATE TABLE IF NOT EXISTS notifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    recipient_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    type TEXT NOT NULL,
    title_ar TEXT NOT NULL,
    title_en TEXT NOT NULL,
    body_ar TEXT,
    body_en TEXT,
    action_url TEXT,
    source_id UUID,
    source_type TEXT,
    is_announcement BOOLEAN NOT NULL DEFAULT false,
    read_at TIMESTAMPTZ,
    email_status TEXT NOT NULL DEFAULT 'pending',
    email_sent_at TIMESTAMPTZ,
    email_error TEXT,
    email_retry_count INTEGER NOT NULL DEFAULT 0,
    created_by UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Create notification_preferences table
CREATE TABLE IF NOT EXISTS notification_preferences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    notification_type TEXT NOT NULL,
    in_app_enabled BOOLEAN NOT NULL DEFAULT true,
    email_enabled BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, org_id, notification_type)
);

-- Enable RLS on both tables
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE notification_preferences ENABLE ROW LEVEL SECURITY;

-- RLS policies for notifications (recipient sees own, admin sees org)
CREATE POLICY notifications_recipient_isolation ON notifications
    FOR ALL
    USING (
        recipient_id = current_setting('app.current_user_id', true)::UUID
        OR EXISTS (
            SELECT 1 FROM profiles
            WHERE id = current_setting('app.current_user_id', true)::UUID
            AND role = 'admin'
            AND org_id = notifications.org_id
        )
    );

-- RLS policies for notification_preferences
CREATE POLICY notification_preferences_user_isolation ON notification_preferences
    FOR ALL
    USING (user_id = current_setting('app.current_user_id', true)::UUID)
    WITH CHECK (user_id = current_setting('app.current_user_id', true)::UUID);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_notifications_recipient_read ON notifications(recipient_id, read_at);
CREATE INDEX IF NOT EXISTS idx_notifications_recipient_created ON notifications(recipient_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_notifications_org_type ON notifications(org_id, type);
CREATE INDEX IF NOT EXISTS idx_notifications_email_status ON notifications(email_status, email_retry_count);
CREATE INDEX IF NOT EXISTS idx_notification_preferences_user ON notification_preferences(user_id, org_id);

-- Migrate org settings from flat to per-type structure
UPDATE organizations
SET settings = jsonb_set(
    COALESCE(settings, '{}'),
    '{notification_preferences,defaults}',
    jsonb_build_object(
        'template_submitted_for_review', jsonb_build_object('in_app', true, 'email', true),
        'template_approved', jsonb_build_object('in_app', true, 'email', true),
        'template_rejected', jsonb_build_object('in_app', true, 'email', true),
        'template_published', jsonb_build_object('in_app', true, 'email', false),
        'template_withdrawn', jsonb_build_object('in_app', true, 'email', false),
        'template_feedback_received', jsonb_build_object('in_app', true, 'email', true),
        'template_feedback_resolved', jsonb_build_object('in_app', true, 'email', false),
        'draft_expiring', jsonb_build_object('in_app', true, 'email', true),
        'system_announcement', jsonb_build_object('in_app', true, 'email', true)
    )
)
WHERE settings->'notification_preferences'->>'email' IS NOT NULL
   OR settings->'notification_preferences'->>'in_app' IS NOT NULL;
