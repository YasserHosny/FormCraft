-- F045: Batch OCR onboarding

CREATE TABLE IF NOT EXISTS ocr_import_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'processing', 'needs_review', 'completed', 'failed', 'cancelled')),
    confidence_threshold NUMERIC(4,3) NOT NULL DEFAULT 0.850 CHECK (confidence_threshold >= 0 AND confidence_threshold <= 1),
    total_items INTEGER NOT NULL DEFAULT 0 CHECK (total_items >= 0 AND total_items <= 200),
    processed_items INTEGER NOT NULL DEFAULT 0 CHECK (processed_items >= 0),
    accepted_items INTEGER NOT NULL DEFAULT 0 CHECK (accepted_items >= 0),
    failed_items INTEGER NOT NULL DEFAULT 0 CHECK (failed_items >= 0),
    duplicate_items INTEGER NOT NULL DEFAULT 0 CHECK (duplicate_items >= 0),
    created_by UUID REFERENCES profiles(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ocr_import_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID NOT NULL REFERENCES ocr_import_batches(id) ON DELETE CASCADE,
    org_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    storage_path TEXT,
    mime_type TEXT NOT NULL,
    file_size_bytes BIGINT NOT NULL CHECK (file_size_bytes >= 0),
    checksum TEXT,
    status TEXT NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'processing', 'needs_review', 'accepted', 'rejected', 'failed', 'duplicate', 'converted')),
    likely_type TEXT,
    category TEXT,
    language TEXT,
    page_count INTEGER NOT NULL DEFAULT 1 CHECK (page_count >= 1),
    confidence NUMERIC(4,3) CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),
    detection_set JSONB NOT NULL DEFAULT '{}'::jsonb,
    existing_detection_id UUID REFERENCES form_detections(id) ON DELETE SET NULL,
    retry_count INTEGER NOT NULL DEFAULT 0 CHECK (retry_count >= 0),
    last_error TEXT,
    converted_template_id UUID REFERENCES templates(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ocr_review_decisions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID NOT NULL REFERENCES ocr_import_batches(id) ON DELETE CASCADE,
    item_id UUID REFERENCES ocr_import_items(id) ON DELETE CASCADE,
    decided_by UUID REFERENCES profiles(id),
    action TEXT NOT NULL CHECK (action IN ('accept', 'reject', 'edit', 'defer', 'merge', 'retry', 'bulk_accept')),
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ocr_duplicate_candidates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID NOT NULL REFERENCES ocr_import_batches(id) ON DELETE CASCADE,
    item_id UUID NOT NULL REFERENCES ocr_import_items(id) ON DELETE CASCADE,
    duplicate_item_id UUID REFERENCES ocr_import_items(id) ON DELETE CASCADE,
    existing_template_id UUID REFERENCES templates(id) ON DELETE SET NULL,
    similarity_score NUMERIC(4,3) NOT NULL CHECK (similarity_score >= 0 AND similarity_score <= 1),
    evidence JSONB NOT NULL DEFAULT '{}'::jsonb,
    decision TEXT NOT NULL DEFAULT 'pending' CHECK (decision IN ('pending', 'keep_one', 'keep_both', 'merge', 'exclude')),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_ocr_import_batches_org_status ON ocr_import_batches(org_id, status);
CREATE INDEX IF NOT EXISTS idx_ocr_import_items_batch_status ON ocr_import_items(batch_id, status);
CREATE INDEX IF NOT EXISTS idx_ocr_import_items_org_checksum ON ocr_import_items(org_id, checksum);
CREATE INDEX IF NOT EXISTS idx_ocr_review_decisions_item ON ocr_review_decisions(item_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_ocr_duplicate_candidates_batch_decision ON ocr_duplicate_candidates(batch_id, decision);

ALTER TABLE ocr_import_batches ENABLE ROW LEVEL SECURITY;
ALTER TABLE ocr_import_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE ocr_review_decisions ENABLE ROW LEVEL SECURITY;
ALTER TABLE ocr_duplicate_candidates ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS ocr_import_batches_org_access ON ocr_import_batches
    FOR ALL USING (org_id IN (SELECT org_id FROM profiles WHERE id = auth.uid()));

CREATE POLICY IF NOT EXISTS ocr_import_items_org_access ON ocr_import_items
    FOR ALL USING (org_id IN (SELECT org_id FROM profiles WHERE id = auth.uid()));

CREATE POLICY IF NOT EXISTS ocr_review_decisions_org_access ON ocr_review_decisions
    FOR ALL USING (batch_id IN (
        SELECT id FROM ocr_import_batches WHERE org_id IN (SELECT org_id FROM profiles WHERE id = auth.uid())
    ));

CREATE POLICY IF NOT EXISTS ocr_duplicate_candidates_org_access ON ocr_duplicate_candidates
    FOR ALL USING (batch_id IN (
        SELECT id FROM ocr_import_batches WHERE org_id IN (SELECT org_id FROM profiles WHERE id = auth.uid())
    ));

GRANT SELECT, INSERT, UPDATE, DELETE ON ocr_import_batches TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ocr_import_items TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ocr_review_decisions TO authenticated;
GRANT SELECT, INSERT, UPDATE, DELETE ON ocr_duplicate_candidates TO authenticated;
