from app.services.validators.base import BaseValidator


class EgyptNationalIdValidator(BaseValidator):
    country = "EG"
    field_type = "national_id"
    regex_pattern = r"[23]\d{13}"

    @property
    def error_message(self) -> str:
        return "Egyptian National ID must be 14 digits starting with 2 or 3"


class EgyptIbanValidator(BaseValidator):
    country = "EG"
    field_type = "iban"
    regex_pattern = r"EG\d{27}"

    @property
    def error_message(self) -> str:
        return "Egyptian IBAN must be 'EG' followed by 27 digits (29 chars total)"


class EgyptPhoneValidator(BaseValidator):
    country = "EG"
    field_type = "phone"
    regex_pattern = r"(\+?20)?0?1\d{8,9}"

    @property
    def error_message(self) -> str:
        return "Egyptian phone must start with 01 (10-11 digits), optionally prefixed with +20"
