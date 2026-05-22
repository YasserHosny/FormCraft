# Feature Specification: AI Smart Control Suggestion

**Feature Branch**: `05-ai-suggestion`
**Created**: 2026-02-21
**Status**: Draft
**Input**: FormCraft PRD Phase 3 – AI Smart Control Suggestion

## User Scenarios & Testing

### User Story 1 - Suggest Control Type on Label Change (Priority: P1)

When a Designer changes a field label in the Design Studio property panel, the system sends the label to the AI suggestion endpoint. The AI returns a suggested control type with confidence score, validation rules, and formatting. The suggestion is displayed in a non-intrusive suggestion chip below the label field. The Designer can accept or dismiss it.

**Why this priority**: Label-triggered suggestion is the primary AI interaction in the Design Studio.

**Independent Test**: Can be tested by changing a label to "رقم الهوية الوطنية" and verifying the suggestion chip shows `national_id` with confidence ≥ 0.8.

**Acceptance Scenarios**:

1. **Given** a text element is selected and the label is changed to "رقم الهوية الوطنية", **When** the AI suggestion endpoint responds, **Then** a suggestion chip appears showing "national_id (95%)" with an Accept and Dismiss button.
2. **Given** the AI suggestion returns, **When** the Designer clicks Accept, **Then** the element's controlType, validation, formatting, and direction are updated to match the suggestion.
3. **Given** the AI suggestion returns, **When** the Designer clicks Dismiss, **Then** the suggestion chip disappears and no changes are applied.
4. **Given** the Designer types rapidly (multiple label changes within 300ms), **When** the debounce timer expires, **Then** only one API call is made with the final label value.

---

### User Story 2 - Suggest Control Type on Field Creation (Priority: P1)

When a Designer drags a new element onto the canvas and enters its initial label, the AI suggestion triggers automatically after the label is set. If the element is dropped without a label, no suggestion fires until a label is entered.

**Why this priority**: Proactive suggestion on creation reduces manual configuration effort.

**Independent Test**: Can be tested by dragging a new element, entering a label, and verifying a suggestion appears.

**Acceptance Scenarios**:

1. **Given** a new text element is dragged onto the canvas, **When** the Designer enters label_ar "تاريخ الميلاد", **Then** the AI suggests controlType "date" with dateFormat "DD/MM/YYYY".
2. **Given** a new element with no label, **When** it is created, **Then** no AI suggestion call is made.

---

### User Story 3 - Suggest Controls on Schema Import (Priority: P2)

When a Designer imports a JSON schema (array of field labels and optional metadata), the AI processes all fields in batch and returns suggestions for each. The Designer reviews all suggestions in a summary dialog before accepting or rejecting each individually.

**Why this priority**: Schema import is a power-user feature for bulk form creation.

**Independent Test**: Can be tested by importing a JSON array of 10 field labels and verifying 10 suggestions are returned.

**Acceptance Scenarios**:

1. **Given** a JSON schema with 5 field labels, **When** the Designer imports it, **Then** a summary dialog shows 5 rows, each with the field label, suggested control type, and confidence.
2. **Given** the summary dialog, **When** the Designer accepts 3 suggestions and rejects 2, **Then** only the 3 accepted fields have their controlType/validation updated.
3. **Given** an import with 50 fields, **When** the batch exceeds the maximum (20 per request), **Then** the system splits into 3 batch requests.

---

### User Story 4 - Deterministic Override (Priority: P1)

When the AI suggests a control type, the system first checks if the field matches a deterministic validator (e.g., Egyptian National ID, Saudi IBAN). If a deterministic match exists, the deterministic rules override the AI suggestion, and the confidence is set to 1.0.

**Why this priority**: Deterministic rules are the source of truth per Constitution Principle IV.

**Independent Test**: Can be tested by sending a label "رقم الهوية الوطنية" with country "EG" and verifying the response uses deterministic validation (14 digits, regex).

**Acceptance Scenarios**:

1. **Given** a field label "رقم الهوية الوطنية" with country "EG", **When** the suggestion endpoint processes it, **Then** the response controlType is "national_id" with confidence 1.0 and validation regex for 14 digits.
2. **Given** a field label "IBAN" with country "SA", **When** the suggestion processes, **Then** validation uses SA IBAN format (SA + 22 alphanumeric) regardless of AI output.
3. **Given** a field label "ملاحظات" (notes) with no deterministic match, **When** the suggestion processes, **Then** the AI suggestion is used as-is.

---

### Edge Cases

- What happens when the LLM returns invalid JSON? → Pydantic validation catches it; fallback to `{ controlType: "text", confidence: 0.5 }`.
- What happens when the LLM returns an unknown controlType? → Pydantic validation rejects it; fallback to "text".
- What happens when the LLM times out (>5 seconds)? → Return fallback suggestion with controlType "text" and confidence 0.0.
- What happens when AWS Bedrock is unavailable? → Return fallback suggestion; log the error; show a warning toast in the UI.
- What happens when the label is empty or whitespace? → No suggestion call is made.
- What happens when the same label is sent multiple times? → Response is cached for 5 minutes to avoid redundant LLM calls.

## Requirements

### Functional Requirements

- **FR-001**: System MUST expose `POST /api/ai/suggest-control` endpoint.
- **FR-002**: Request body MUST include: `label` (string), `language` (ar/en), `country` (EG/SA/AE), `industry` (string, optional), `sampleValues` (string[], optional).
- **FR-003**: Response MUST conform to the SuggestionResponse Pydantic schema (see below).
- **FR-004**: System MUST validate LLM response against Pydantic schema before returning.
- **FR-005**: Invalid LLM responses MUST fall back to `{ controlType: "text", confidence: 0.5 }`.
- **FR-006**: LLM calls MUST timeout after 5 seconds; timeout returns fallback.
- **FR-007**: System MUST check deterministic validators before returning AI suggestion; deterministic match overrides AI.
- **FR-008**: System MUST cache suggestion responses by label+language+country key for 5 minutes.
- **FR-009**: Frontend MUST debounce label changes by 300ms before calling the suggestion endpoint.
- **FR-010**: Frontend MUST display suggestions as non-modal chips with Accept/Dismiss actions.
- **FR-011**: Suggestions MUST NEVER be auto-applied. User must explicitly accept.
- **FR-012**: System MUST log all suggestion requests and responses to the audit trail.
- **FR-013**: System MUST log whether each suggestion was accepted or dismissed.
- **FR-014**: Batch import MUST split into chunks of max 20 fields per API call.
- **FR-015**: Allowed controlType values: text, number, date, currency, dropdown, radio, checkbox, phone, email, national_id, iban, vat_number, cr_number, barcode, qr, image.
- **FR-016**: System MUST use the strict LLM system prompt defined in the PRD (deterministic JSON-only classification engine).

### LLM System Prompt

```
You are a deterministic Form Field Classification Engine.

Your task:
Given a field label and context, return ONLY structured JSON.

Do not include explanations.
Do not include markdown.
Do not include extra text.

Allowed control types:
text, number, date, currency, dropdown, radio, checkbox, phone, email, national_id, iban, vat_number, cr_number, barcode, qr, image

Return JSON matching this exact schema:
{
  "controlType": "",
  "confidence": 0.0-1.0,
  "validation": {
    "required": boolean,
    "regex": string | null,
    "minLength": number | null,
    "maxLength": number | null,
    "numericOnly": boolean
  },
  "formatting": {
    "dateFormat": string | null,
    "decimalPlaces": number | null,
    "currencyCode": string | null,
    "uppercase": boolean
  },
  "direction": "rtl" | "ltr" | "auto"
}

Country context: Egypt, Saudi Arabia, UAE possible.
Arabic field names must be interpreted semantically.
If unsure, default to: controlType: "text", confidence: 0.5
Return only valid JSON.
```

### SuggestionResponse Schema

```python
class ValidationSchema(BaseModel):
    required: bool = False
    regex: str | None = None
    minLength: int | None = None
    maxLength: int | None = None
    numericOnly: bool = False

class FormattingSchema(BaseModel):
    dateFormat: str | None = None
    decimalPlaces: int | None = None
    currencyCode: str | None = None
    uppercase: bool = False

class SuggestionResponse(BaseModel):
    controlType: Literal[
        "text", "number", "date", "currency", "dropdown", "radio",
        "checkbox", "phone", "email", "national_id", "iban",
        "vat_number", "cr_number", "barcode", "qr", "image"
    ]
    confidence: float = Field(ge=0.0, le=1.0)
    validation: ValidationSchema
    formatting: FormattingSchema
    direction: Literal["rtl", "ltr", "auto"]
```

### Key Entities

- **SuggestionRequest**: label, language, country, industry, sampleValues
- **SuggestionResponse**: controlType, confidence, validation, formatting, direction
- **SuggestionAuditLog**: request payload, response payload, accepted (boolean), user_id, element_id, timestamp

## Success Criteria

### Measurable Outcomes

- **SC-001**: AI suggestion endpoint responds within 3 seconds (p95) including LLM latency.
- **SC-002**: Fallback to "text" is triggered within 100ms when LLM times out or returns invalid response.
- **SC-003**: Deterministic validators correctly override AI suggestions for all known field types (EG/SA/UAE national ID, IBAN, VAT, phone).
- **SC-004**: Cache hit rate exceeds 30% after initial usage period (common labels are reused).
- **SC-005**: 100% of suggestion events (request, response, accept/dismiss) are captured in audit log.
- **SC-006**: Zero auto-applied suggestions (verified by code review and integration test).
