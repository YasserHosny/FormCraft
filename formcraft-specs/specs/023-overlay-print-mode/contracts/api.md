# API Contracts: Overlay Print Mode

**Date**: 2026-05-17

## Endpoints

### Template Print Settings

#### `GET /api/templates/:id/print-settings`

Get print settings for a template.

**Auth**: Designer, Admin, Branch Manager  
**Response 200**:
```json
{
  "template_id": "uuid",
  "print_mode": "overlay",
  "updated_at": "2026-05-17T10:00:00Z"
}
```

**Response 404**: No settings configured (defaults to "full")

---

#### `PUT /api/templates/:id/print-settings`

Create or update print settings.

**Auth**: Designer, Admin  
**Request**:
```json
{
  "print_mode": "overlay"
}
```

**Response 200**:
```json
{
  "template_id": "uuid",
  "print_mode": "overlay",
  "updated_at": "2026-05-17T10:00:00Z"
}
```

**Errors**: 422 (invalid mode), 403

---

### Printer Profiles

#### `POST /api/printer-profiles`

Create a printer profile.

**Auth**: Admin  
**Request**:
```json
{
  "name": "HP LaserJet Tray 2",
  "description": "Second floor printer, tray 2",
  "x_offset_mm": 1.5,
  "y_offset_mm": -0.5,
  "is_default": false
}
```

**Response 201**:
```json
{
  "id": "uuid",
  "name": "HP LaserJet Tray 2",
  "description": "Second floor printer, tray 2",
  "x_offset_mm": 1.5,
  "y_offset_mm": -0.5,
  "is_default": false,
  "is_active": true,
  "created_at": "2026-05-17T10:00:00Z"
}
```

**Errors**: 422, 409 (default already exists), 403

---

#### `GET /api/printer-profiles`

List all active printer profiles for the org.

**Auth**: Any authenticated  
**Query Params**:
- `include_inactive` (boolean, default false)

**Response 200**:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "HP LaserJet Tray 2",
      "x_offset_mm": 1.5,
      "y_offset_mm": -0.5,
      "is_default": false,
      "is_active": true
    }
  ],
  "total": 3
}
```

---

#### `PATCH /api/printer-profiles/:id`

Update a printer profile.

**Auth**: Admin  
**Request** (partial):
```json
{
  "x_offset_mm": 2.0,
  "y_offset_mm": -1.0
}
```

**Response 200**: Updated profile object  
**Errors**: 422, 404, 403

---

#### `DELETE /api/printer-profiles/:id`

Soft-delete a printer profile (set is_active=false).

**Auth**: Admin  
**Response 200**: `{ "id": "uuid", "is_active": false }`  
**Errors**: 404, 403

---

#### `POST /api/printer-profiles/:id/set-default`

Set a profile as the org default.

**Auth**: Admin  
**Response 200**: `{ "id": "uuid", "is_default": true }`  
(Previous default is unset automatically)

---

#### `POST /api/printer-profiles/:id/calibration-page`

Generate calibration test page PDF.

**Auth**: Admin  
**Response 200**: `Content-Type: application/pdf`

PDF contains crosshair markers at known positions with measurement grid.

---

### PDF Generation (Modified)

#### `POST /api/submissions/:id/pdf`

Extended with optional printer profile selection.

**Auth**: Operator, Admin, Branch Manager  
**Request** (extended):
```json
{
  "printer_profile_id": "uuid-or-null",
  "print_mode_override": null
}
```

- `printer_profile_id`: Optional. If provided, applies offset. If null, uses org default (if exists) or zero offset.
- `print_mode_override`: Optional. Overrides template setting for this generation only.

**Response 200** (single PDF mode — full or overlay):
```json
{
  "pdf_url": "https://storage.../submission_uuid.pdf",
  "print_mode": "overlay",
  "printer_profile_id": "uuid",
  "x_offset_mm": 1.5,
  "y_offset_mm": -0.5
}
```

**Response 200** (both mode):
```json
{
  "full_pdf_url": "https://storage.../submission_uuid_full.pdf",
  "overlay_pdf_url": "https://storage.../submission_uuid_overlay.pdf",
  "print_mode": "both",
  "printer_profile_id": "uuid",
  "x_offset_mm": 1.5,
  "y_offset_mm": -0.5
}
```

## Error Response Format

Standard FormCraft format:
```json
{
  "detail": "Human-readable error message",
  "errors": [{ "field": "x_offset_mm", "message": "Offset must be between -50 and 50" }]
}
```
