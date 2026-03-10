LABEL_PATTERNS: dict[str, dict[str, list[str]]] = {
    "EG": {
        "national_id": [
            "رقم الهوية",
            "الرقم القومي",
            "رقم البطاقة",
            "national id",
            "id number",
        ],
        "iban": ["iban", "رقم الحساب الدولي", "آيبان"],
        "phone": ["رقم الهاتف", "رقم الموبايل", "الهاتف", "phone", "mobile"],
    },
    "SA": {
        "national_id": [
            "رقم الهوية",
            "رقم الإقامة",
            "الهوية الوطنية",
            "national id",
            "iqama",
        ],
        "iban": ["iban", "رقم الحساب الدولي", "آيبان"],
        "vat_number": [
            "الرقم الضريبي",
            "رقم ضريبة القيمة المضافة",
            "vat",
            "tax number",
        ],
    },
    "AE": {
        "iban": ["iban", "رقم الحساب الدولي"],
        "vat_number": ["رقم التسجيل الضريبي", "trn", "tax registration"],
    },
}


class LabelMatcher:
    """Maps Arabic/English field labels to (country, field_type) tuples."""

    def match(self, label: str, country: str) -> tuple[str, str] | None:
        """Returns (country, field_type) or None if no match."""
        normalized = label.strip().lower()
        for field_type, patterns in LABEL_PATTERNS.get(country, {}).items():
            for pattern in patterns:
                if pattern in normalized:
                    return (country, field_type)
        return None
