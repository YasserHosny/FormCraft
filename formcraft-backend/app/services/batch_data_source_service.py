import csv
import hashlib
import io

import openpyxl


class BatchDataSourceService:
    """Parse and manage batch data sources (CSV, XLSX, clipboard)."""

    ALLOWED_MIME_TYPES = {
        "text/csv",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
    ALLOWED_EXTENSIONS = {".csv", ".xlsx"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

    def detect_encoding(self, content: bytes) -> str:
        """Detect file encoding; default to utf-8-sig."""
        # Simple heuristic: try utf-8-sig first, then windows-1256 for Arabic
        for enc in ("utf-8-sig", "utf-8", "windows-1256"):
            try:
                content.decode(enc)
                return enc
            except UnicodeDecodeError:
                continue
        return "utf-8-sig"

    def parse_csv(self, content: bytes) -> tuple[list[str], list[dict]]:
        """Parse CSV bytes into (headers, rows)."""
        encoding = self.detect_encoding(content)
        text = content.decode(encoding)
        reader = csv.DictReader(io.StringIO(text))
        headers = reader.fieldnames or []
        rows = [row for row in reader]
        return headers, rows

    def parse_xlsx(self, content: bytes) -> tuple[list[str], list[dict]]:
        """Parse XLSX bytes into (headers, rows)."""
        wb = openpyxl.load_workbook(io.BytesIO(content), read_only=True, data_only=True)
        ws = wb.active
        if ws is None:
            return [], []

        rows_iter = ws.iter_rows(values_only=True)
        try:
            headers = [str(h) if h is not None else "" for h in next(rows_iter)]
        except StopIteration:
            return [], []

        rows = []
        for raw_row in rows_iter:
            row = {}
            for idx, header in enumerate(headers):
                val = raw_row[idx] if idx < len(raw_row) else None
                row[header] = str(val) if val is not None else ""
            rows.append(row)
        return headers, rows

    def parse_clipboard(self, text: str) -> tuple[list[str], list[dict]]:
        """Parse clipboard text (tab or comma separated) into (headers, rows)."""
        # Try tab first, then comma
        for delimiter in ("\t", ","):
            reader = csv.DictReader(io.StringIO(text), delimiter=delimiter)
            headers = reader.fieldnames or []
            if headers and len(headers) > 1:
                rows = [row for row in reader]
                return headers, rows
        return [], []

    def compute_checksum(self, content: bytes) -> str:
        return hashlib.sha256(content).hexdigest()

    def validate_upload(
        self,
        file_name: str,
        mime_type: str,
        file_size: int,
        content: bytes,
    ) -> tuple[bool, str]:
        """Validate upload constraints. Returns (ok, error_message)."""
        ext = file_name.lower().split(".")[-1] if "." in file_name else ""
        dot_ext = f".{ext}"

        if dot_ext not in self.ALLOWED_EXTENSIONS:
            return False, f"Extension '{dot_ext}' not allowed. Use .csv or .xlsx."

        if mime_type not in self.ALLOWED_MIME_TYPES:
            return False, f"MIME type '{mime_type}' not allowed."

        if file_size > self.MAX_FILE_SIZE:
            return False, f"File size {file_size} exceeds 10 MB limit."

        return True, ""

    def auto_map_columns(
        self, headers: list[str], template_field_keys: list[str]
    ) -> dict[str, str]:
        """Auto-map CSV/Excel columns to template field keys by normalized header match."""
        mapping = {}
        normalized_fields = {
            self._normalize(k): k for k in template_field_keys
        }
        for header in headers:
            norm = self._normalize(header)
            if norm in normalized_fields:
                mapping[header] = normalized_fields[norm]
            else:
                # Substring match: if header contains field key or vice versa
                for norm_key, original_key in normalized_fields.items():
                    if norm_key in norm or norm in norm_key:
                        mapping[header] = original_key
                        break
        return mapping

    @staticmethod
    def _normalize(text: str) -> str:
        return (
            text.lower()
            .strip()
            .replace(" ", "_")
            .replace("-", "_")
        )
