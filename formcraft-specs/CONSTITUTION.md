# FormCraft Constitution

## Core Principles

### I. Arabic-First, RTL-Native

Every UI component, layout, and PDF output must work correctly in RTL as the primary direction. LTR is the secondary mode. Mixed-direction content (Arabic + English in the same field or label) must render correctly in inputs, canvas elements, and PDF output. All new components must be tested in both RTL and LTR before merge.

### II. Pixel-Perfect Print Fidelity

All canvas positioning uses absolute coordinates in millimeters (mm). No auto-scaling, no responsive reflow in print output. PDF output must match the canvas design 1:1 at the specified page dimensions. Arabic glyph shaping (via arabic-reshaper + python-bidi) is mandatory for all text rendering in PDF. Font embedding is required — no system font fallback in PDF.

### III. AI Suggestion, Never Auto-Apply

AI provides field control suggestions with confidence scores (0.0–1.0). Suggestions are NEVER auto-applied to the canvas or form schema. The user must explicitly accept or reject each suggestion. AI scope is strictly limited to Design Studio control type suggestions via `POST /ai/suggest-control`. No AI chat, no conversational workflows, no OCR, no layout AI, no bulk automation.

### IV. Deterministic Over Probabilistic

Country-specific validation rules (national ID, IBAN, VAT, phone, CR number, TRN) are hard-coded deterministic validators. These validators always override AI suggestions when a matching field type is detected. The validator library is the source of truth for field format rules — AI suggestions that conflict with deterministic rules are discarded.

### V. Test-First Development

TDD is mandatory: write tests → tests fail → implement → tests pass. Red-Green-Refactor cycle strictly enforced. Every API endpoint must have contract tests. Every validator must have unit tests covering valid, invalid, and edge-case inputs. Integration tests must cover the critical path: create template → apply AI suggestion → render PDF.

### VI. Normalized Data Model

Templates, Pages, and Elements are stored as normalized entities with foreign key relationships. No embedded/nested documents. All schema changes require versioned migrations via Supabase CLI. Every entity has `created_at`, `updated_at`, and `created_by` audit fields.

### VII. Translation-Key Architecture

Zero hardcoded UI strings in templates or components. All user-facing text uses i18n translation keys resolved at runtime. Language preference is stored per user in the database. UI layout must mirror correctly (flex direction, margins, paddings, icon positions) when switching between RTL and LTR. Mixed Arabic-English rendering in form inputs must be handled with proper `dir="auto"` attributes.

### VIII. Security and Auditability

JWT-based authentication via Supabase Auth. Role-based access control with four roles: Admin, Designer, Operator, Viewer. Row-Level Security (RLS) policies enforced at the database level. Full audit trail for: template CRUD operations, AI suggestion requests, AI suggestion accept/reject actions, user role changes. All API endpoints require authentication. Rate limiting on AI suggestion endpoint.

### IX. Simplicity and YAGNI

Phase 1 builds only what is specified. No SSO. No OCR. No AI chat assistant. No layout AI. No bulk automation. No real-time collaboration. No version diffing UI. Features are added only when specified in an approved spec. Premature abstraction is avoided — extract patterns only after the third occurrence.

## Technology Constraints

| Layer | Technology | Locked |
|-------|-----------|--------|
| Frontend Framework | Angular (latest LTS) | Yes |
| UI Component Library | Angular Material | Yes |
| Canvas Engine | Pure Konva.js | Yes |
| Backend Framework | Python FastAPI | Yes |
| Database / Auth | Supabase Cloud | Yes |
| PDF Rendering | WeasyPrint | Yes |
| AI Provider | AWS Bedrock (abstracted via LLMProvider interface) | No — provider swappable |
| Frontend Validation | Zod | Yes |
| Backend Validation | Pydantic | Yes |
| Hosting | Bunny Magic Containers | Yes |
| CI/CD | Bunny built-in CI | Yes |
| Repository Strategy | Polyrepo (frontend + backend + specs) | Yes |

## Development Workflow

1. **Spec first** — No implementation begins without an approved `spec.md`.
2. **Plan second** — Each spec gets a `plan.md` with technical decisions and file structure.
3. **Tasks third** — Each plan is broken into a `tasks.md` with phased, dependency-ordered tasks.
4. **Branch per task** — Each task gets its own branch, named `[spec-number]-[task-id]-[short-description]`.
5. **Tests before code** — Test files are created and failing before implementation begins.
6. **Review against spec** — PRs are reviewed against the spec's acceptance scenarios.

## API Contract Discipline

- Frontend (Zod) and Backend (Pydantic) schemas must stay in sync.
- Any API contract change requires updating both repos.
- Contract tests in the backend verify response shapes match documented schemas.
- Breaking API changes require a spec amendment and version bump.

## Governance

- This Constitution supersedes all other development practices.
- Amendments require: documented rationale, impact assessment, migration plan if breaking.
- All code reviews must verify compliance with these principles.
- Complexity that violates these principles must be justified in writing.

**Version**: 1.0.0 | **Ratified**: 2026-02-21 | **Last Amended**: 2026-02-21
