# Tasks: Arabic-Specific Validation Library

**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

Format: `[ID] [Priority] [Story] Description`

## Phase 1: Base Infrastructure

- [ ] **T07-001** P1 Setup — Create `app/services/validators/base.py` — BaseValidator abstract class, ValidationResult Pydantic model, `_clean()` method (strip whitespace/dashes)

## Phase 2: Country Validators

- [ ] **T07-010** P1 S1 — Create `app/services/validators/egypt.py` — EgyptNationalIdValidator (14 digits, starts with 2|3), EgyptIbanValidator (EG + 27 chars), EgyptPhoneValidator (+20 prefix, 10 digits, local format normalization)
- [ ] **T07-011** P1 S2 — Create `app/services/validators/saudi.py` — SaudiNationalIdValidator (10 digits, starts 1|2), SaudiIbanValidator (SA + 22 alphanumeric), SaudiVatValidator (15 digits, starts 3, ends 3)
- [ ] **T07-012** P1 S3 — Create `app/services/validators/uae.py` — UaeIbanValidator (AE + 21 chars), UaeTrnValidator (15 digits)

## Phase 3: Registry & Label Matcher

- [ ] **T07-020** P1 S4 — Create `app/services/validators/registry.py` — ValidatorRegistry: registers all validators, lookup by (country, field_type), returns validator instance or None
- [ ] **T07-021** P1 S4 — Create `app/services/validators/label_matcher.py` — LabelMatcher: maps Arabic/English label patterns to (country, field_type) tuples using substring containment matching
- [ ] **T07-022** P1 S4 — Create `app/services/validators/__init__.py` — Initialize registry with all validators, export registry and label_matcher instances

## Phase 4: Integration with AI Suggestion

- [ ] **T07-030** P1 S4 — Update `app/services/ai/suggestion.py` — Insert validator registry check after cache check and before LLM call, return deterministic result with confidence 1.0 on match

## Phase 5: Tests

- [ ] **T07-040** P1 S1 — Write `tests/unit/test_egypt_validators.py` — 30+ test cases: valid IDs, invalid IDs (wrong length, wrong prefix, non-numeric), valid/invalid IBAN, valid/invalid phone (local + international formats)
- [ ] **T07-041** P1 S2 — Write `tests/unit/test_saudi_validators.py` — 30+ test cases: citizen ID (starts 1), iqama (starts 2), invalid (starts 3), IBAN, VAT (starts/ends with 3)
- [ ] **T07-042** P1 S3 — Write `tests/unit/test_uae_validators.py` — 20+ test cases: IBAN, TRN valid/invalid
- [ ] **T07-043** P1 S4 — Write `tests/unit/test_label_matcher.py` — Arabic labels match correct types, English labels match, unknown labels return None, case insensitivity
- [ ] **T07-044** P1 S4 — Write `tests/unit/test_registry.py` — Registry lookup returns correct validator, missing (country, type) returns None
- [ ] **T07-045** P1 S4 — Write `tests/integration/test_deterministic_pipeline.py` — Full flow: label → label_matcher → registry → validator → suggestion response with confidence 1.0

## Dependencies & Execution Order

```
T07-001 (base, first)
T07-010, T07-011, T07-012 (parallel: country validators)
T07-010-012 → T07-020 → T07-021 → T07-022 (registry + matcher after validators)
T07-022 → T07-030 (integration after registry ready)
T07-040, T07-041, T07-042 (parallel: country tests)
T07-043, T07-044 → T07-045 (unit tests → integration test)
```

## Parallel Opportunities

- All three country validator files (T07-010, T07-011, T07-012) in parallel
- All three country test files (T07-040, T07-041, T07-042) in parallel
- Registry (T07-020) and label matcher (T07-021) can be developed in parallel
