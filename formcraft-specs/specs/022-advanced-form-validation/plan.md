# Implementation Plan: Advanced Form Validation & Conditional Logic

**Date**: 2026-05-17  
**Feature Branch**: `021-advanced-form-validation`  
**Depends on**: Feature 016 (Form Filler reactive forms), Feature 020 (expanded element types)

## Architecture Overview

This feature adds a ConditionEngine that evaluates element visibility, dynamic required status, and computed values. The engine is implemented twice: in Python for server-side submission validation, and in TypeScript for real-time form interaction.

```
┌──────────────────────────────────────────────────────────────────┐
│                     Design Studio                                  │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │ ConditionBuilderComponent (visible_when, required_when)      ││
│  │ ExpressionEditorComponent (computed_value)                   ││
│  │ DefaultValuePicker + PlaceholderInput                        ││
│  └──────────────────────────────────────────────────────────────┘│
├───────────────────────────────���──────────────────────────────────┤
│                     Form Desk (Operator)                           │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │ ConditionEngineService (TypeScript)                          ││
│  │  ├── DependencyGraph (built once on load)                   ││
│  │  ├── VisibilityEvaluator (reactive per field change)        ││
│  │  ├── RequiredEvaluator (reactive)                           ││
│  │  ├── ComputedValueEvaluator (reactive)                      │��
│  │  └── DefaultValueResolver (on load)                         ││
│  └──────────���───────────────────────────────���───────────────────┘│
├──────────────────────────────────────────────────────────────────┤
│                     Backend                                        │
│  ┌──────────────────────────────────────────────────────────────┐│
│  │ ConditionEngine (Python)                                     ││
│  │  ├── evaluate_visibility(data, elements) → visible_keys     ││
│  │  ├── evaluate_required(data, elements, visible_keys)        ││
│  │  ├── validate_submission(data, elements) → errors           ││
│  │  └── strip_hidden_values(data, visible_keys) → clean_data  ││
│  │                                                              ││
│  │ DependencyValidator                                          ││
│  │  └── detect_cycles(elements) → cycle[] | None               ││
│  └───────────────────────────────────���──────────────────────────┘│
├──────────────────────────────────────────────────────────────────┤
│                     Database                                       │
│  elements: +visible_when, +required_when, +computed_value,       │
│            +default_value, +placeholder_text                      │
└─���─────────────────────────────��──────────────────────────────────┘
```

## Technology Stack

- **Backend**: Python 3.12, `ast` module (safe expression parsing), FastAPI
- **Frontend**: Angular 17, RxJS (reactive evaluation), Reactive Forms
- **No new dependencies** — expression parser hand-written, dependency graph via DFS

## Implementation Phases

### Phase 1: Database Migration

Add 5 nullable columns to elements table.

### Phase 2: Backend ConditionEngine

Python implementation: visibility evaluation, required evaluation, expression parser, submission stripping, dependency cycle detection.

### Phase 3: Backend Integration

Wire ConditionEngine into submission service. Add dependency validation endpoint.

### Phase 4: Frontend ConditionEngine Service

TypeScript implementation: dependency graph construction, reactive visibility/required evaluation, computed value evaluation, default value resolution.

### Phase 5: Frontend - Design Studio Condition Builder

UI for configuring visible_when, required_when (condition builder), computed_value (expression editor), default_value, placeholder_text.

### Phase 6: Frontend - Form Desk Integration

Wire ConditionEngineService into form filler: show/hide elements, toggle required, auto-compute values, apply defaults, show placeholders.

### Phase 7: End-to-End Validation

Test cascading conditions, computed values, submission stripping, draft preservation.

## Technical Constraints

1. **No eval()** — expression parser uses AST whitelist (Python) and recursive descent (TypeScript)
2. **Dual implementation** — backend and frontend must produce identical evaluation results for same inputs
3. **Performance** — dependency graph built once; per-change evaluation is O(k) where k = direct dependents
4. **Backwards compatible** — all 5 new columns are nullable; existing elements unaffected
5. **Draft vs submission difference** — drafts save all; submissions strip hidden values

## Risk Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Frontend/backend condition evaluation divergence | Submit fails unexpectedly | Shared test cases; same operator semantics documented |
| Complex cascading conditions cause performance issue | UI freeze | Limit cascade depth to 10 levels; warn designer at 5+ depth |
| Expression parser security | Code injection | Whitelist AST nodes; no function calls allowed |
| Circular dependency not caught | Infinite loop | DFS cycle detection on every condition save; hard limit on evaluation iterations |
