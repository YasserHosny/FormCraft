import logging
import re
from datetime import datetime, timezone
from uuid import UUID

from fastapi import HTTPException, status
from supabase import Client

from app.models.submission import Submission
from app.services.condition_engine import ConditionEngine
from app.services.validators.registry import ValidatorRegistry
from app.services.validators.egypt import EgyptNationalIdValidator, EgyptIbanValidator, EgyptPhoneValidator
from app.services.validators.saudi import SaudiNationalIdValidator, SaudiIbanValidator, SaudiVatValidator
from app.services.validators.uae import UaeIbanValidator, UaeTrnValidator

logger = logging.getLogger(__name__)

_validator_registry = ValidatorRegistry()
_validator_registry.register(EgyptNationalIdValidator())
_validator_registry.register(EgyptIbanValidator())
_validator_registry.register(EgyptPhoneValidator())
_validator_registry.register(SaudiNationalIdValidator())
_validator_registry.register(SaudiIbanValidator())
_validator_registry.register(SaudiVatValidator())
_validator_registry.register(UaeIbanValidator())
_validator_registry.register(UaeTrnValidator())


_condition_engine = ConditionEngine()


class SubmissionService:
    """Submission creation with reference number generation and audit logging."""

    def __init__(self, client: Client):
        self.client = client

    async def create_submission(
        self,
        template_id: UUID,
        template_version: int,
        field_values: dict,
        operator_id: UUID,
        org_id: UUID,
        branch_id: UUID | None = None,
    ) -> Submission:
        template_data = self._validate_template(template_id, template_version)
        elements = self._get_template_elements(template_id, template_version)
        country = template_data.get("country", "SA")

        visible_keys = _condition_engine.evaluate_visibility(elements, field_values)
        clean_values = _condition_engine.strip_hidden_values(field_values, visible_keys)

        required_keys = _condition_engine.evaluate_required(elements, clean_values, visible_keys)
        cond_errors = []
        for key in required_keys:
            val = clean_values.get(key)
            if val is None or val == "":
                cond_errors.append({
                    "field": key,
                    "code": "required",
                    "message": f"Field '{key}' is required",
                })

        # Only validate visible elements — hidden fields should not trigger required errors
        visible_elements = [e for e in elements if e.get("key", "") in visible_keys]
        errors = self._validate_field_values(clean_values, visible_elements, country)
        errors.extend(cond_errors)
        if errors:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={"message": "Validation failed", "errors": errors},
            )

        reference_number = self._generate_reference_number(org_id)

        data = {
            "template_id": str(template_id),
            "template_version": template_version,
            "operator_id": str(operator_id),
            "org_id": str(org_id),
            "field_values": clean_values,
            "reference_number": reference_number,
            "status": "printed",
        }
        if branch_id:
            data["branch_id"] = str(branch_id)

        result = self.client.table("submissions").insert(data).execute()
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create submission",
            )

        return Submission(**result.data[0])

    def _validate_template(self, template_id: UUID, template_version: int) -> dict:
        try:
            result = (
                self.client.table("templates")
                .select("id, version, status, country")
                .eq("id", str(template_id))
                .single()
                .execute()
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found or not published",
            )

        if not result.data or result.data.get("status") != "published":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found or not published",
            )

        return result.data

    def _get_template_elements(self, template_id: UUID, template_version: int) -> list[dict]:
        try:
            result = (
                self.client.table("element_renderers")
                .select("key, type, required, validation, formatting, properties, visible_when, required_when, computed_value")
                .eq("template_id", str(template_id))
                .execute()
            )
            return result.data if result.data else []
        except Exception:
            return []

    def _validate_field_values(
        self, field_values: dict, elements: list[dict], country: str
    ) -> list[dict]:
        errors = []
        country_validators = _validator_registry.list_all_for_country(country)

        for elem in elements:
            key = elem.get("key", "")
            elem_type = elem.get("type", "")
            required = elem.get("required", False)
            validation = elem.get("validation") or {}
            value = field_values.get(key)

            if required and (value is None or value == ""):
                errors.append({
                    "field": key,
                    "code": "required",
                    "message": f"Field '{key}' is required",
                })
                continue

            if value is None or value == "":
                continue

            if validation.get("pattern") and isinstance(value, str):
                pattern = validation["pattern"]
                if not re.fullmatch(pattern, value):
                    errors.append({
                        "field": key,
                        "code": "pattern",
                        "message": f"Field '{key}' does not match required pattern",
                    })

            if validation.get("minLength") and isinstance(value, str):
                if len(value) < validation["minLength"]:
                    errors.append({
                        "field": key,
                        "code": "min_length",
                        "message": f"Field '{key}' must be at least {validation['minLength']} characters",
                    })

            if validation.get("maxLength") and isinstance(value, str):
                if len(value) > validation["maxLength"]:
                    errors.append({
                        "field": key,
                        "code": "max_length",
                        "message": f"Field '{key}' must be at most {validation['maxLength']} characters",
                    })

            if validation.get("min") is not None and isinstance(value, (int, float)):
                if value < validation["min"]:
                    errors.append({
                        "field": key,
                        "code": "min_value",
                        "message": f"Field '{key}' must be at least {validation['min']}",
                    })

            if validation.get("max") is not None and isinstance(value, (int, float)):
                if value > validation["max"]:
                    errors.append({
                        "field": key,
                        "code": "max_value",
                        "message": f"Field '{key}' must be at most {validation['max']}",
                    })

            country_validator = country_validators.get(elem_type)
            if country_validator and isinstance(value, str):
                result = country_validator.validate(value)
                if not result.valid:
                    errors.append({
                        "field": key,
                        "code": "country_validation",
                        "message": result.error or f"Field '{key}' failed country-specific validation",
                    })

            if elem_type == "signature" and value is not None:
                errors.extend(self._validate_signature(key, value, required))

            if elem_type == "table" and value is not None:
                errors.extend(self._validate_table(key, value, elem))

        return errors

    def _generate_reference_number(self, org_id: UUID) -> str:
        try:
            result = self.client.rpc(
                "generate_submission_ref", {"p_org_id": str(org_id)}
            ).execute()
            if result.data:
                return result.data
        except Exception:
            pass

        now = datetime.now(timezone.utc)
        month_str = now.strftime("%Y-%m")
        return f"FC-{month_str}-{now.strftime('%H%M%S')}"

    def _validate_signature(self, key: str, value: dict | str, required: bool) -> list[dict]:
        errors = []
        if isinstance(value, dict):
            # Accept pending-upload markers — large signatures uploaded post-submission
            if value.get("__pending_upload") and value.get("dataUrl"):
                data_url = value["dataUrl"]
                if not data_url.startswith("data:image/png;base64,"):
                    errors.append({"field": key, "code": "invalid_signature", "message": f"Field '{key}' must be a valid PNG image"})
                return errors
            sig_type = value.get("type", "inline")
            if sig_type == "inline":
                data = value.get("data", "")
                if not data or not data.startswith("data:image/png;base64,"):
                    errors.append({"field": key, "code": "invalid_signature", "message": f"Field '{key}' must be a valid PNG image"})
                elif len(data) > 500000:
                    errors.append({"field": key, "code": "signature_too_large", "message": f"Field '{key}' signature data exceeds 500KB limit"})
            elif sig_type == "storage":
                path = value.get("path", "")
                if not path:
                    errors.append({"field": key, "code": "invalid_signature", "message": f"Field '{key}' storage path missing"})
        elif isinstance(value, str):
            if not value.startswith("data:image/png;base64,"):
                errors.append({"field": key, "code": "invalid_signature", "message": f"Field '{key}' must be a valid PNG image"})
        elif required:
            errors.append({"field": key, "code": "required", "message": f"Signature '{key}' is required"})
        return errors

    def _validate_table(self, key: str, value: list, elem: dict) -> list[dict]:
        errors = []
        if not isinstance(value, list):
            errors.append({"field": key, "code": "invalid_table", "message": f"Field '{key}' must be an array of rows"})
            return errors

        props = elem.get("properties", {})
        min_rows = props.get("min_rows", 0)
        required = elem.get("required", False)

        if required and len(value) < min_rows:
            errors.append({"field": key, "code": "min_rows", "message": f"Field '{key}' requires at least {min_rows} rows"})

        columns = props.get("columns", [])
        col_types = {c["key"]: c.get("type", "text") for c in columns if "key" in c}
        required_cols = [c["key"] for c in columns if c.get("required", False) and "key" in c]

        for row_idx, row in enumerate(value):
            if not isinstance(row, dict):
                errors.append({"field": f"{key}[{row_idx}]", "code": "invalid_row", "message": f"Row {row_idx + 1} must be an object"})
                continue
            for col_key in required_cols:
                if not row.get(col_key):
                    errors.append({"field": f"{key}[{row_idx}].{col_key}", "code": "required", "message": f"Column '{col_key}' is required in row {row_idx + 1}"})
            for col_key, col_val in row.items():
                col_type = col_types.get(col_key, "text")
                if col_type == "number" and col_val is not None and col_val != "":
                    try:
                        float(col_val)
                    except (ValueError, TypeError):
                        errors.append({"field": f"{key}[{row_idx}].{col_key}", "code": "invalid_type", "message": f"Column '{col_key}' must be numeric in row {row_idx + 1}"})
                elif col_type == "date" and col_val is not None and col_val != "":
                    import re as _re
                    if not _re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(col_val)):
                        errors.append({"field": f"{key}[{row_idx}].{col_key}", "code": "invalid_type", "message": f"Column '{col_key}' must be a date (YYYY-MM-DD) in row {row_idx + 1}"})
        return errors

    async def list_submissions(
        self,
        operator_id: UUID | None = None,
        org_id: UUID | None = None,
        search: str | None = None,
        template_id: UUID | None = None,
        status_filter: str | None = None,
        date_from: str | None = None,
        date_to: str | None = None,
        page: int = 1,
        limit: int = 25,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
        scope: str = "own",
    ) -> tuple[list[dict], int]:
        query = self.client.table("submissions").select(
            "id, reference_number, template_id, template_version, status, field_values, operator_id, org_id, created_at, templates(name)",
            count="exact",
        )

        if scope == "own" and operator_id:
            query = query.eq("operator_id", str(operator_id))
        elif org_id:
            query = query.eq("org_id", str(org_id))

        if search:
            query = query.or_(
                f"reference_number.eq.{search}"
            )

        if template_id:
            query = query.eq("template_id", str(template_id))

        if status_filter:
            query = query.eq("status", status_filter)

        if date_from:
            query = query.gte("created_at", date_from)

        if date_to:
            query = query.lte("created_at", date_to)

        offset = (page - 1) * limit
        desc = sort_dir.lower() == "desc"
        sort_col = "created_at" if sort_by == "created_at" else "reference_number"
        query = query.order(sort_col, desc=desc).range(offset, offset + limit - 1)

        result = query.execute()
        items = []
        for row in (result.data or []):
            template_name = ""
            templates = row.pop("templates", None)
            if templates:
                if isinstance(templates, dict):
                    template_name = templates.get("name", "")
                elif isinstance(templates, list) and len(templates) > 0:
                    template_name = templates[0].get("name", "")

            elements = self._get_template_elements(row["template_id"], row.get("template_version", 1))
            key_summary = self._compute_key_summary(row.get("field_values", {}), elements)

            items.append({
                "id": row["id"],
                "reference_number": row["reference_number"],
                "template_id": row["template_id"],
                "template_name": template_name,
                "template_version": row["template_version"],
                "status": row.get("status", "printed"),
                "created_at": row["created_at"],
                "key_summary": key_summary,
            })

        return items, result.count or 0

    async def get_submission(self, submission_id: UUID, org_id: UUID) -> dict | None:
        result = (
            self.client.table("submissions")
            .select("*, templates(name), profiles!submissions_operator_id_fkey(full_name)")
            .eq("id", str(submission_id))
            .eq("org_id", str(org_id))
            .single()
            .execute()
        )

        if not result.data:
            return None

        row = dict(result.data)
        row["template_name"] = ""
        templates = row.pop("templates", None)
        if templates:
            if isinstance(templates, dict):
                row["template_name"] = templates.get("name", "")
            elif isinstance(templates, list) and len(templates) > 0:
                row["template_name"] = templates[0].get("name", "")

        row["operator_name"] = ""
        profiles = row.pop("profiles", None)
        if profiles:
            if isinstance(profiles, dict):
                row["operator_name"] = profiles.get("full_name", "")
            elif isinstance(profiles, str):
                row["operator_name"] = profiles

        return row

    def _compute_key_summary(self, field_values: dict, elements: list[dict]) -> list[str]:
        if not field_values:
            return []
        if not elements:
            values = list(field_values.values())[:3]
            return [str(v) for v in values if v is not None and v != ""]

        sorted_elements = sorted(elements, key=lambda e: e.get("sort_order", 0))
        summary = []
        for elem in sorted_elements:
            key = elem.get("key", "")
            val = field_values.get(key)
            if val is not None and val != "":
                summary.append(str(val))
                if len(summary) >= 3:
                    break
        return summary

    async def export_submission(self, submission_id: UUID, fmt: str = "json") -> dict | bytes:
        row = (
            self.client.table("submissions")
            .select("*, templates(name)")
            .eq("id", str(submission_id))
            .single()
            .execute()
        )
        if not row.data:
            raise HTTPException(status_code=404, detail="Submission not found")

        data = dict(row.data)
        template_name = ""
        templates = data.pop("templates", None)
        if templates:
            if isinstance(templates, dict):
                template_name = templates.get("name", "")
            elif isinstance(templates, list) and len(templates) > 0:
                template_name = templates[0].get("name", "")

        export_data = {
            "reference_number": data["reference_number"],
            "template_name": template_name,
            "template_version": data["template_version"],
            "submitted_at": str(data["created_at"]),
            "operator_id": str(data["operator_id"]),
            "field_values": data.get("field_values", {}),
        }

        if fmt == "csv":
            from app.schemas.submission import generate_csv
            return generate_csv(
                data.get("field_values", {}),
                data["reference_number"],
                template_name,
                str(data["created_at"]),
            )

        return export_data

    async def list_submissions_legacy(
        self,
        operator_id: UUID,
        page: int = 1,
        limit: int = 20,
    ) -> tuple[list[Submission], int]:
        offset = (page - 1) * limit
        result = (
            self.client.table("submissions")
            .select("id, reference_number, template_id, template_version, operator_id, field_values, created_at", count="exact")
            .eq("operator_id", str(operator_id))
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )
        submissions = [Submission(**row) for row in result.data]
        return submissions, result.count or 0