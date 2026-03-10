from app.services.validators.base import BaseValidator


class ValidatorRegistry:
    """Registry mapping (country, field_type) → Validator instance."""

    def __init__(self):
        self._validators: dict[tuple[str, str], BaseValidator] = {}

    def register(self, validator: BaseValidator) -> None:
        key = (validator.country, validator.field_type)
        self._validators[key] = validator

    def get(self, country: str, field_type: str) -> BaseValidator | None:
        return self._validators.get((country, field_type))

    def list_all(self) -> list[tuple[str, str]]:
        return list(self._validators.keys())
