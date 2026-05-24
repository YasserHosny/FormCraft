# Quickstart: Form Import & OCR Detection

## Prerequisites

1. Azure Document Intelligence resource (free tier: 500 pages/month)
2. Backend running on `localhost:8000`
3. Frontend running on `localhost:4200`
4. Migration 028 applied to Supabase

## Setup

### 1. Azure Credentials

Add to `formcraft-backend/.env`:
```
AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT=https://YOUR_RESOURCE.cognitiveservices.azure.com/
AZURE_DOCUMENT_INTELLIGENCE_KEY=your_api_key
```

### 2. Dependencies

```bash
cd formcraft-backend
pip install azure-ai-formrecognizer==3.3.0 Pillow==10.2.0
```

### 3. Migration

Apply `migrations/028_form_detections.sql` via Supabase SQL editor.

## Quick Test

### API Test (curl)

```bash
# Upload a form image
curl -X POST http://localhost:8000/api/forms/import/{template_id} \
  -H "Authorization: Bearer YOUR_JWT" \
  -F "file=@path/to/cheque.jpg" \
  -F "page_index=0"

# Get detections
curl http://localhost:8000/api/forms/{template_id}/detections \
  -H "Authorization: Bearer YOUR_JWT"

# Accept detections
curl -X POST http://localhost:8000/api/forms/{template_id}/detections/{detection_id}/accept \
  -H "Authorization: Bearer YOUR_JWT" \
  -H "Content-Type: application/json" \
  -d '{"detection_ids": [0, 1, 2]}'
```

### UI Flow

1. Open Design Studio for any template
2. Click "Import Form" in the toolbar
3. Upload a JPEG/PNG image of a form
4. Review detected fields (colored overlays on canvas)
5. Accept/reject individual detections or use bulk actions
6. Save template — accepted detections become real elements
