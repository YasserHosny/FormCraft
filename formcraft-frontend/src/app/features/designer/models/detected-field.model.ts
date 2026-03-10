export interface DetectedField {
  text: string;
  bbox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  confidence: number;
  suggested_type: string;
  status: 'pending' | 'accepted' | 'rejected';
}

export interface DetectionResponse {
  id: string;
  template_id: string;
  page_index: number;
  detected_fields: DetectedField[];
  page_dimensions: {
    width: number;
    height: number;
  };
  created_at: string;
}
