from app.services.validators.base import BaseValidator


class SaudiNationalIdValidator(BaseValidator):
    country = "SA"
    field_type = "national_id"
    regex_pattern = r"[12]\d{9}"

    @property
    def error_message(self) -> str:
        return "Saudi National ID must be 10 digits starting with 1 (citizen) or 2 (iqama)"


class SaudiIbanValidator(BaseValidator):
    country = "SA"
    field_type = "iban"
    regex_pattern = r"SA\d{2}[A-Z0-9]{20}"

    @property
    def error_message(self) -> str:
        return "Saudi IBAN must be 'SA' + 2 check digits + 20 alphanumeric (24 chars total)"


class SaudiVatValidator(BaseValidator):
    country = "SA"
    field_type = "vat_number"
    regex_pattern = r"3\d{13}3"

    @property
    def error_message(self) -> str:
        return "Saudi VAT must be 15 digits starting and ending with 3"
