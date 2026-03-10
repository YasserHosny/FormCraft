from app.services.validators.base import BaseValidator


class UaeIbanValidator(BaseValidator):
    country = "AE"
    field_type = "iban"
    regex_pattern = r"AE\d{21}"

    @property
    def error_message(self) -> str:
        return "UAE IBAN must be 'AE' + 21 digits (23 chars total)"


class UaeTrnValidator(BaseValidator):
    country = "AE"
    field_type = "vat_number"
    regex_pattern = r"\d{15}"

    @property
    def error_message(self) -> str:
        return "UAE TRN must be exactly 15 digits"
