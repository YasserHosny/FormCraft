# Implementation Plan: Arabic-Specific Validation Library

**Branch**: `07-arabic-validators` | **Date**: 2026-02-21 | **Spec**: [spec.md](./spec.md)

## Summary

Implement stateless, pure-function validators for Egyptian, Saudi, and UAE documents (National ID, IBAN, VAT, Phone, TRN), a ValidatorRegistry for lookup by country+field_type, a LabelMatcher for mapping Arabic field labels to document types, and integration with the AI suggestion pipeline.

## Technical Context

**Language/Version**: Python 3.12
**Primary Dependencies**: re (stdlib), Pydantic v2
**Storage**: None (pure computation, no I/O)
**Testing**: pytest with comprehensive valid/invalid test corpus
**Constraints**: < 1ms per validation, zero external dependencies

## Constitution Check

| Principle | Status | Notes |
|-----------|--------|-------|
| IV. Deterministic | ✅ Pass | All validators are pure functions with regex-based rules |
| V. Test-First | ✅ Pass | Extensive test corpus per validator |
| IX. YAGNI | ✅ Pass | Only EG/SA/AE countries, only specified document types |

## Project Structure

### Backend (formcraft-backend)

```text
app/services/validators/
├── __init__.py                     # ValidatorRegistry class
├── base.py                         # BaseValidator abstract class, ValidationResult model
├── egypt.py                        # EgyptNationalIdValidator, EgyptIbanValidator, EgyptPhoneValidator
├── saudi.py                        # SaudiNationalIdValidator, SaudiIbanValidator, SaudiVatValidator
├── uae.py                          # UaeIbanValidator, UaeTrnValidator
├── label_matcher.py                # LabelMatcher: Arabic/English label → (country, field_type)
└── registry.py                     # ValidatorRegistry: (country, field_type) → Validator

tests/unit/
├── test_egypt_validators.py        # 30+ test cases per validator
├── test_saudi_validators.py
├── test_uae_validators.py
├── test_label_matcher.py           # Label pattern matching accuracy
└── test_registry.py                # Registry lookup + AI pipeline integration
```

### Validator Interface

```python
# base.py
from pydantic import BaseModel

class ValidationResult(BaseModel):
    valid: bool
    error: str | None = None
    normalized: str = ""

class BaseValidator:
    country: str
    field_type: str
    regex_pattern: str

    def validate(self, value: str) -> ValidationResult:
        cleaned = self._clean(value)
        if re.fullmatch(self.regex_pattern, cleaned):
            return ValidationResult(valid=True, normalized=cleaned)
        return ValidationResult(valid=False, error=self.error_message)

    def _clean(self, value: str) -> str:
        return re.sub(r'[\s\-]', '', value)

    @property
    def error_message(self) -> str:
        raise NotImplementedError

    @property
    def regex(self) -> str:
        return self.regex_pattern
```

### Validator Specifications

| Country | Type | Regex | Rules |
|---------|------|-------|-------|
| EG | national_id | `^[23]\d{13}$` | 14 digits, starts with 2 or 3 |
| EG | iban | `^EG\d{27}$` | "EG" + 27 digits, total 29 chars |
| EG | phone | `^(\+?20)?[01]\d{9}$` | +20 prefix optional, 10 digits after |
| SA | national_id | `^[12]\d{9}$` | 10 digits, starts with 1 (citizen) or 2 (iqama) |
| SA | iban | `^SA\d{2}[A-Z0-9]{20}$` | "SA" + 2 check digits + 20 alphanumeric, total 24 |
| SA | vat_number | `^3\d{13}3$` | 15 digits, starts and ends with 3 |
| AE | iban | `^AE\d{2}\d{3}\d{16}$` | "AE" + 2 check + 3 bank + 16 account, total 23 |
| AE | vat_number | `^\d{15}$` | TRN: exactly 15 digits |

### LabelMatcher

```python
# label_matcher.py
LABEL_PATTERNS = {
    "EG": {
        "national_id": ["رقم الهوية", "الرقم القومي", "رقم البطاقة", "national id", "id number"],
        "iban": ["iban", "رقم الحساب الدولي", "آيبان"],
        "phone": ["رقم الهاتف", "رقم الموبايل", "الهاتف", "phone", "mobile"],
    },
    "SA": {
        "national_id": ["رقم الهوية", "رقم الإقامة", "الهوية الوطنية", "national id", "iqama"],
        "iban": ["iban", "رقم الحساب الدولي", "آيبان"],
        "vat_number": ["الرقم الضريبي", "رقم ضريبة القيمة المضافة", "vat", "tax number"],
    },
    "AE": {
        "iban": ["iban", "رقم الحساب الدولي"],
        "vat_number": ["رقم التسجيل الضريبي", "trn", "tax registration"],
    },
}

class LabelMatcher:
    def match(self, label: str, country: str) -> tuple[str, str] | None:
        """Returns (country, field_type) or None if no match."""
        normalized = label.strip().lower()
        for field_type, patterns in LABEL_PATTERNS.get(country, {}).items():
            for pattern in patterns:
                if pattern in normalized:
                    return (country, field_type)
        return None
```

### Integration with AI Suggestion Pipeline

```
# In suggestion.py (spec 05)
label_match = label_matcher.match(request.label, request.country)
if label_match:
    country, field_type = label_match
    validator = registry.get(country, field_type)
    return SuggestionResponse(
        controlType=field_type,
        confidence=1.0,
        validation=ValidationSchema(
            required=True,
            regex=validator.regex,
            ...
        ),
        ...
    )
# else: proceed to LLM
```

## Research Notes

- **IBAN checksum**: Phase 1 validates format only (prefix + length). Full MOD-97 checksum validation can be added in Phase 2 with minimal effort (already a well-known algorithm).
- **Egyptian National ID structure**: First digit = century (2 = 1900s, 3 = 2000s), digits 2-7 = birth date, digit 8 = governorate, digits 9-12 = sequence, digit 13 = gender (odd=male), digit 14 = check digit. Phase 1 validates format; semantic parsing deferred.
- **Label matching strategy**: Simple substring containment, case-insensitive, with normalized Arabic text. No ML/NLP needed. Covers the common patterns listed in the spec.

## Complexity Tracking

No constitution violations.
