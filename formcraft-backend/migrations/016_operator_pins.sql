-- Operator Dashboard: Pins and Notification Dismissals
-- Feature 015: operator-dashboard

CREATE TABLE operator_pins (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operator_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (operator_id, template_id)
);

CREATE INDEX idx_operator_pins_operator ON operator_pins(operator_id);

ALTER TABLE operator_pins ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own pins"
ON operator_pins
FOR ALL
USING (operator_id = auth.uid())
WITH CHECK (operator_id = auth.uid());

CREATE TABLE notification_dismissals (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    operator_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    dismissed_version INT NOT NULL,
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (operator_id, template_id, dismissed_version)
);

CREATE INDEX idx_notification_dismissals_operator ON notification_dismissals(operator_id);

ALTER TABLE notification_dismissals ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own dismissals"
ON notification_dismissals
FOR ALL
USING (operator_id = auth.uid())
WITH CHECK (operator_id = auth.uid());