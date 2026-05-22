# Tasks: Advanced Form Validation & Conditional Logic

**Input**: Design documents from `/specs/021-advanced-form-validation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/
**Depends on**: Feature 016 (Form Filler reactive forms), Feature 020 (expanded element types)

## Phase 1: Database Migration

**Purpose**: Add conditional logic columns to elements table

- [X] T001 [P] Create migration `formcraft-backend/migrations/024_advanced_form_validation.sql` — ADD COLUMN visible_when JSONB, required_when JSONB, computed_value TEXT, default_value TEXT, placeholder_text JSONB (all nullable) to elements table with COMMENT statements
- [X] T002 [P] Update element Pydantic schemas in `formcraft-backend/app/schemas/` — add visible_when, required_when, computed_value, default_value, placeholder_text as Optional fields to ElementCreate, ElementUpdate, ElementResponse
- [X] T003 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/ar.json` — conditions.*, computed.*, defaults.*, placeholders.* keys
- [X] T004 [P] Add i18n keys to `formcraft-frontend/src/assets/i18n/en.json` — same keys in English

---

## Phase 2: Backend ConditionEngine

**Purpose**: Python implementation of condition evaluation, expression parsing, and dependency validation

- [X] T005 Create `formcraft-backend/app/services/condition_engine.py` — ConditionEngine class with methods: evaluate_condition(condition_obj, form_data) → bool, evaluate_visibility(elements, form_data) → set[visible_keys], evaluate_required(elements, form_data, visible_keys) → set[required_keys]
- [X] T006 Add operator implementations in ConditionEngine — equals (case-sensitive), not_equals, contains (case-insensitive), greater_than, less_than, is_empty, is_not_empty; handle type coercion for numeric comparisons
- [X] T007 Create expression parser in ConditionEngine — parse_expression(expr_string) using ast.parse() with whitelist (Num, BinOp, Name, UnaryOp); evaluate_expression(expr_string, values_dict) → float; handle division by zero (return 0)
- [X] T008 Create `formcraft-backend/app/services/dependency_validator.py` — build_dependency_graph(elements) → adjacency list; detect_cycles(graph) → cycle_path | None using iterative DFS
- [X] T009 Add strip_hidden_values(form_data, visible_keys) to ConditionEngine — returns new dict with only visible field values

**Checkpoint**: Backend can evaluate conditions, parse expressions safely, detect cycles, and strip hidden values.

---

## Phase 3: Backend Integration

**Purpose**: Wire ConditionEngine into submission and element save flows

- [X] T010 Integrate ConditionEngine into submission service — on submission: evaluate visibility → strip hidden → evaluate required → validate required fields have values → store clean data
- [X] T011 Add dependency validation to element save — on element create/update with visible_when/required_when/computed_value: validate referenced fields exist, run cycle detection on full template; reject with 422 if cycle found
- [X] T012 Add `POST /api/templates/:id/validate-dependencies` endpoint — returns {valid, dependency_count, max_depth} or {valid: false, cycle: [...]}

**Checkpoint**: Submissions correctly strip hidden values and enforce conditional required. Circular dependencies rejected at design time.

---

## Phase 4: Frontend ConditionEngine Service

**Purpose**: TypeScript reactive condition evaluation for Form Desk

- [X] T013 Create `formcraft-frontend/src/app/features/desk/services/condition-engine.service.ts` — ConditionEngineService class: buildDependencyGraph(elements), evaluateCondition(condition, formData), evaluateVisibility(elements, formData) → Set<string>
- [X] T014 Add reactive evaluation — subscribe to form.valueChanges, on each change: identify affected dependents from graph, re-evaluate visibility/required for only those elements, emit visibilityChanged and requiredChanged observables
- [X] T015 Add computed value evaluator — recursive-descent expression parser (supports +, -, *, /, (), field references, numeric literals); on source field change, recompute and patch form control value
- [X] T016 Add default value resolver — on form load: iterate elements with default_value, resolve tokens ({{today}} → new Date(), {{user_name}} → auth service), set initial form control values
- [X] T017 Add cascade evaluation — when visibility changes for element A, check if A is referenced by other conditions; if so, re-evaluate those dependents recursively (max depth 10)

**Checkpoint**: Frontend evaluates conditions reactively with O(k) per field change. Computed values update live.

---

## Phase 5: Frontend - Design Studio Condition Builder

**Purpose**: UI for designers to configure conditions, expressions, defaults, placeholders

- [X] T018 Create ConditionBuilderComponent `formcraft-frontend/src/app/features/studio/components/condition-builder/` — reusable component: source field dropdown (other elements on template), operator dropdown, value input (type-aware); supports multiple conditions (AND); used by both visible_when and required_when panels
- [X] T019 Create ExpressionEditorComponent `formcraft-frontend/src/app/features/studio/components/expression-editor/` — text input with element key autocomplete, syntax validation (calls validate-dependencies endpoint), preview of computed result with sample values
- [X] T020 Add default_value and placeholder_text fields to element properties panel — default_value: text input with token picker ({{today}}, {{user_name}}, etc.); placeholder_text: ar/en text inputs
- [X] T021 Add condition summary display to element properties — show "Visible when: marital_status = married" and "Required when: loan_amount > 50000" as human-readable chips with edit/remove actions

**Checkpoint**: Designer can configure all conditional logic via intuitive UI. Dependency validation runs on save.

---

## Phase 6: Frontend - Form Desk Integration

**Purpose**: Wire ConditionEngineService into form filler for real-time behavior

- [X] T022 Integrate visibility into form filler — subscribe to ConditionEngineService.visibilityChanged; show/hide elements with CSS transition (opacity + height); when hidden, remove from tab order
- [X] T023 Integrate conditional required — subscribe to requiredChanged; dynamically add/remove Validators.required on form controls; toggle asterisk indicator
- [X] T024 Integrate computed values — for elements with computed_value, render as read-only with "calculated" badge; patch value from ComputedValueEvaluator on dependency changes
- [X] T025 Integrate defaults and placeholders — on form init, apply resolved defaults; set placeholder attribute from placeholder_text based on current locale
- [X] T026 Handle draft save — save ALL form values (including hidden fields) to draft; on draft load, restore all values then re-evaluate conditions

**Checkpoint**: Form Desk dynamically shows/hides fields, toggles required, auto-computes values, and applies defaults/placeholders.

---

## Phase 7: End-to-End Validation

**Purpose**: Verify the complete condition pipeline

- [X] T027 Test cascading visibility — A shows B, B shows C; hide A → verify B and C both hidden; show A → verify cascade restores
- [X] T028 Test computed values — configure total = qty * price; change qty and price; verify total updates; verify total included in submission
- [X] T029 Test submission stripping — fill hidden field → submit → verify hidden field NOT in stored submission data
- [X] T030 Test draft preservation — fill field → hide it → save draft → reload draft → show it → verify value preserved
- [X] T031 Test circular dependency detection — try to create A visible_when B, B visible_when A → verify 422 error with cycle path

**Checkpoint**: Complete conditional logic working end-to-end with correct draft/submission behavior.
