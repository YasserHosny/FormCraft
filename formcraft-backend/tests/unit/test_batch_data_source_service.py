
from app.services.batch_data_source_service import BatchDataSourceService


class TestBatchDataSourceService:
    def test_parse_csv(self):
        content = b"name,amount\nAlice,100\nBob,200"
        svc = BatchDataSourceService()
        headers, rows = svc.parse_csv(content)
        assert headers == ["name", "amount"]
        assert len(rows) == 2
        assert rows[0]["name"] == "Alice"

    def test_parse_clipboard_tab(self):
        text = "name\tamount\nAlice\t100\nBob\t200"
        svc = BatchDataSourceService()
        headers, rows = svc.parse_clipboard(text)
        assert headers == ["name", "amount"]
        assert len(rows) == 2

    def test_auto_map_columns(self):
        svc = BatchDataSourceService()
        mapping = svc.auto_map_columns(
            ["customer_name", "account_number"],
            ["customer_name", "account_number", "amount"],
        )
        assert mapping["customer_name"] == "customer_name"
        assert mapping["account_number"] == "account_number"

    def test_validate_upload_passes(self):
        svc = BatchDataSourceService()
        ok, msg = svc.validate_upload("data.csv", "text/csv", 1024, b"a,b\n1,2")
        assert ok is True
        assert msg == ""

    def test_validate_upload_rejects_large_file(self):
        svc = BatchDataSourceService()
        ok, msg = svc.validate_upload("data.csv", "text/csv", 20 * 1024 * 1024, b"x")
        assert ok is False
        assert "exceeds" in msg

    def test_validate_upload_rejects_bad_extension(self):
        svc = BatchDataSourceService()
        ok, msg = svc.validate_upload("data.pdf", "application/pdf", 1024, b"x")
        assert ok is False
        assert "Extension" in msg
