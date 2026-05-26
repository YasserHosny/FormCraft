
from app.services.batch_validation_service import BatchValidationService


class TestBatchValidationService:
    def test_validate_rows_all_valid(self):
        svc = BatchValidationService()
        rows = [
            {"name": "Alice", "amount": "100"},
            {"name": "Bob", "amount": "200"},
        ]
        mapping = {"name": "customer_name", "amount": "amount"}
        fields = {
            "customer_name": {"required": True, "validation": {}},
            "amount": {"required": True, "validation": {}},
        }
        results, dup_count = svc.validate_rows(rows, mapping, fields)
        assert len(results) == 2
        assert all(r["status"] == "valid" for r in results)
        assert dup_count == 0

    def test_validate_rows_detects_duplicate(self):
        svc = BatchValidationService()
        rows = [
            {"name": "Alice", "amount": "100"},
            {"name": "Alice", "amount": "100"},
        ]
        mapping = {"name": "customer_name", "amount": "amount"}
        fields = {
            "customer_name": {"required": True, "validation": {}},
            "amount": {"required": True, "validation": {}},
        }
        results, dup_count = svc.validate_rows(rows, mapping, fields, duplicate_strategy="warn")
        assert dup_count == 1
        assert results[1]["status"] == "duplicate"

    def test_validate_rows_skips_duplicate(self):
        svc = BatchValidationService()
        rows = [
            {"name": "Alice", "amount": "100"},
            {"name": "Alice", "amount": "100"},
        ]
        mapping = {"name": "customer_name", "amount": "amount"}
        fields = {
            "customer_name": {"required": True, "validation": {}},
            "amount": {"required": True, "validation": {}},
        }
        results, dup_count = svc.validate_rows(rows, mapping, fields, duplicate_strategy="skip")
        assert dup_count == 1
        assert results[1]["status"] == "duplicate"

    def test_revalidate_mapping_passes(self):
        svc = BatchValidationService()
        mapping = {"col1": "field_a"}
        fields = {"field_a": {}}
        ok, msg = svc.revalidate_mapping(mapping, fields)
        assert ok is True

    def test_revalidate_mapping_fails(self):
        svc = BatchValidationService()
        mapping = {"col1": "field_b"}
        fields = {"field_a": {}}
        ok, msg = svc.revalidate_mapping(mapping, fields)
        assert ok is False
        assert "no longer exists" in msg
