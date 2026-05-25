import hashlib
import json



class BatchValidationService:
    """Validate batch rows against template rules and detect duplicates."""

    def __init__(self, template_service=None, validator_service=None):
        self.template_service = template_service
        self.validator_service = validator_service

    def validate_rows(
        self,
        rows: list[dict],
        column_mapping: dict[str, str],
        template_fields: dict[str, dict],
        duplicate_strategy: str = "warn",
    ) -> tuple[list[dict], int]:
        """
        Validate all rows and return list of row results plus duplicate count.
        Each result: {"row_number": int, "status": "valid"|"invalid"|"duplicate", "field_errors": {}}.
        """
        results = []
        seen_hashes = set()
        duplicate_count = 0

        for idx, row in enumerate(rows, start=1):
            mapped = self._apply_mapping(row, column_mapping)
            row_hash = self._hash_row(mapped)

            is_duplicate = row_hash in seen_hashes
            if is_duplicate:
                duplicate_count += 1
                if duplicate_strategy == "skip":
                    results.append(
                        {
                            "row_number": idx,
                            "status": "duplicate",
                            "field_errors": {"_duplicate": "Duplicate row detected"},
                        }
                    )
                    continue
                elif duplicate_strategy == "warn":
                    # Still validate but flag as duplicate
                    pass

            seen_hashes.add(row_hash)

            field_errors = self._validate_mapped_row(mapped, template_fields)
            if field_errors:
                status = "invalid"
            elif is_duplicate and duplicate_strategy == "warn":
                status = "duplicate"
            else:
                status = "valid"

            results.append(
                {
                    "row_number": idx,
                    "status": status,
                    "field_errors": field_errors,
                }
            )

        return results, duplicate_count

    def revalidate_mapping(
        self,
        column_mapping: dict[str, str],
        current_template_fields: dict[str, dict],
    ) -> tuple[bool, str]:
        """
        Re-validate that all mapped fields still exist in the template.
        Returns (ok, error_message).
        """
        for csv_col, field_key in column_mapping.items():
            if field_key not in current_template_fields:
                return False, f"Mapped field '{field_key}' no longer exists in template."
            # Optional: check if field type changed
        return True, ""

    def _apply_mapping(self, row: dict, column_mapping: dict[str, str]) -> dict[str, str]:
        """Apply column mapping to a raw row."""
        mapped = {}
        for csv_col, field_key in column_mapping.items():
            mapped[field_key] = row.get(csv_col, "")
        return mapped

    def _hash_row(self, mapped: dict[str, str]) -> str:
        """Hash a mapped row for duplicate detection."""
        canonical = json.dumps(mapped, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _validate_mapped_row(
        self, mapped: dict[str, str], template_fields: dict[str, dict]
    ) -> dict[str, str]:
        """Validate a single mapped row against template field rules."""
        errors = {}
        for field_key, value in mapped.items():
            field_config = template_fields.get(field_key, {})
            required = field_config.get("required", False)
            if required and not value.strip():
                errors[field_key] = "Required field is empty"
                continue

            validation = field_config.get("validation", {})
            if validation:
                min_len = validation.get("min_length")
                max_len = validation.get("max_length")
                pattern = validation.get("pattern")

                if min_len is not None and len(value) < min_len:
                    errors[field_key] = f"Minimum length is {min_len}"
                elif max_len is not None and len(value) > max_len:
                    errors[field_key] = f"Maximum length is {max_len}"
                elif pattern and value:
                    import re

                    if not re.match(pattern, value):
                        errors[field_key] = "Value does not match required format"
        return errors
