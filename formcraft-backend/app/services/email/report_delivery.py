import os
from datetime import datetime


class ReportDeliveryService:
    """Handles email delivery of generated reports via Resend."""

    def __init__(self, resend_api_key: str | None = None):
        self.api_key = resend_api_key or os.getenv("RESEND_API_KEY")
        self.from_email = os.getenv("RESEND_FROM_EMAIL", "reports@formcraft.app")

    async def send_report_email(
        self,
        recipients: list[str],
        subject: str,
        body_html: str,
        attachment_bytes: bytes | None = None,
        attachment_filename: str = "report.xlsx",
    ) -> dict:
        """Send a report email with optional attachment via Resend API."""
        import httpx

        if not self.api_key:
            raise RuntimeError("Resend API key is not configured")

        payload = {
            "from": self.from_email,
            "to": recipients,
            "subject": subject,
            "html": body_html,
        }

        if attachment_bytes:
            import base64
            payload["attachments"] = [
                {
                    "filename": attachment_filename,
                    "content": base64.b64encode(attachment_bytes).decode("utf-8"),
                }
            ]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=payload,
            )
            response.raise_for_status()
            return response.json()

    def build_report_email_body(
        self,
        report_name: str,
        period_description: str,
        record_count: int,
    ) -> str:
        """Build a bilingual HTML email body for report delivery."""
        return f"""
        <html dir="rtl">
        <body style="font-family: Arial, sans-serif; direction: rtl;">
            <h2>{report_name}</h2>
            <p>تم إرفاق التقرير المطلوب.</p>
            <p>Your requested report is attached.</p>
            <hr>
            <p><strong>Period / الفترة:</strong> {period_description}</p>
            <p><strong>Records / السجلات:</strong> {record_count}</p>
            <p><em>Generated on / تم الإنشاء بتاريخ:</em> {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}</p>
        </body>
        </html>
        """
