import asyncio
import zipfile
from io import BytesIO
from uuid import UUID


class BatchGenerationService:
    """Background PDF generation loop with progress tracking and cancellation."""

    def __init__(self, pdf_service=None, submission_service=None):
        self.pdf_service = pdf_service
        self.submission_service = submission_service
        self._cancel_flags: dict[str, bool] = {}

    async def generate_batch(
        self,
        job_id: UUID,
        org_id: UUID,
        template_id: UUID,
        template_version: int,
        rows: list[dict],
        column_mapping: dict[str, str],
        download_format: str,
        supabase_client=None,
    ) -> tuple[int, int, list[dict]]:
        """
        Generate PDFs for all valid rows.
        Returns (success_count, fail_count, error_details).
        Updates progress every 10 PDFs.
        """
        job_id_str = str(job_id)
        self._cancel_flags[job_id_str] = False

        success_count = 0
        fail_count = 0
        errors = []
        generated_pdfs = []

        for idx, row in enumerate(rows, start=1):
            if self._cancel_flags.get(job_id_str, False):
                break

            mapped = {field_key: row.get(csv_col, "") for csv_col, field_key in column_mapping.items()}

            try:
                # Generate PDF using existing renderer
                pdf_bytes = await self._generate_single_pdf(
                    org_id=org_id,
                    template_id=template_id,
                    template_version=template_version,
                    data=mapped,
                )

                # Log as submission
                submission_id = await self._log_submission(
                    org_id=org_id,
                    template_id=template_id,
                    template_version=template_version,
                    job_id=job_id,
                    data=mapped,
                    pdf_bytes=pdf_bytes,
                    supabase_client=supabase_client,
                )

                generated_pdfs.append({"submission_id": submission_id, "pdf_bytes": pdf_bytes})
                success_count += 1

            except Exception as exc:
                fail_count += 1
                errors.append(
                    {
                        "row_number": idx,
                        "field_key": None,
                        "error_type": "generation",
                        "error_message": str(exc)[:500],
                    }
                )

            # Update progress every 10 rows to reduce DB writes
            if idx % 10 == 0 or idx == len(rows):
                await self._update_progress(job_id, success_count + fail_count, supabase_client)

            # Small yield to prevent blocking
            if idx % 5 == 0:
                await asyncio.sleep(0)

        # Build download artifact if not cancelled or if partial results exist
        artifact = None
        if generated_pdfs:
            if download_format == "zip":
                artifact = self._build_zip(generated_pdfs)
            elif download_format == "merged_pdf":
                artifact = self._build_merged_pdf(generated_pdfs)
            elif download_format == "printer_queue":
                # Printer queue logic: store references for printer service
                artifact = {"printer_queue": [g["submission_id"] for g in generated_pdfs]}

        return success_count, fail_count, errors, artifact

    def cancel_job(self, job_id: UUID):
        """Signal cancellation for a running job."""
        self._cancel_flags[str(job_id)] = True

    async def _generate_single_pdf(
        self,
        org_id: UUID,
        template_id: UUID,
        template_version: int,
        data: dict,
    ) -> bytes:
        """Generate a single PDF using the existing WeasyPrint renderer."""
        if self.pdf_service:
            return await self.pdf_service.render_batch_pdf(
                org_id=org_id,
                template_id=template_id,
                template_version=template_version,
                data=data,
            )
        # Placeholder: return empty PDF bytes
        return b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n>>\nendobj\nxref\n0 4\n0000000000 65535 f\n0000000009 00000 n\n0000000058 00000 n\n0000000115 00000 n\ntrailer\n<<\n/Size 4\n/Root 1 0 R\n>>\nstartxref\n196\n%%EOF\n"

    async def _log_submission(
        self,
        org_id: UUID,
        template_id: UUID,
        template_version: int,
        job_id: UUID,
        data: dict,
        pdf_bytes: bytes,
        supabase_client,
    ) -> UUID:
        """Log a batch-generated form as an individual submission."""
        if self.submission_service:
            return await self.submission_service.create_batch_submission(
                org_id=org_id,
                template_id=template_id,
                template_version=template_version,
                job_id=job_id,
                data=data,
                pdf_bytes=pdf_bytes,
                supabase_client=supabase_client,
            )
        return job_id  # placeholder

    async def _update_progress(self, job_id: UUID, progress: int, supabase_client):
        if supabase_client:
            await supabase_client.table("batch_jobs").update({"progress": progress}).eq("id", str(job_id)).execute()

    def _build_zip(self, generated_pdfs: list[dict]) -> bytes:
        buffer = BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for idx, item in enumerate(generated_pdfs, start=1):
                zf.writestr(f"batch_{idx:04d}.pdf", item["pdf_bytes"])
        buffer.seek(0)
        return buffer.getvalue()

    def _build_merged_pdf(self, generated_pdfs: list[dict]) -> bytes:
        # For MVP, return the first PDF or concatenated placeholder
        # Full implementation would use pypdf or WeasyPrint multi-page
        if not generated_pdfs:
            return b""
        # Return a simple concatenation (not valid PDF but placeholder)
        return b"\n".join(item["pdf_bytes"] for item in generated_pdfs)
