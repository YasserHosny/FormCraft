import re

from pydantic import BaseModel


class ValidationResult(BaseModel):
    valid: bool
    error: str | None = None
    normalized: str = ""


class BaseValidator:
    """Abstract base for all country-specific validators."""

    country: str
    field_type: str
    regex_pattern: str

    def validate(self, value: str) -> ValidationResult:
        cleaned = self._clean(value)
        if re.fullmatch(self.regex_pattern, cleaned):
            return ValidationResult(valid=True, normalized=cleaned)
        return ValidationResult(valid=False, error=self.error_message)

    def _clean(self, value: str) -> str:
        return re.sub(r"[\s\-]", "", value)

    @property
    def error_message(self) -> str:
        raise NotImplementedError
