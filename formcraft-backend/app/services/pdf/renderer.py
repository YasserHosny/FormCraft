"""Main PDF render orchestrator using WeasyPrint."""

import logging

from weasyprint import HTML

from app.services.pdf.html_builder import build_html

logger = logging.getLogger(__name__)


def render_template_pdf(template: dict) -> bytes:
    """Render a template dict to PDF bytes via WeasyPrint."""
    html_string = build_html(template)
    logger.info("Rendering PDF for template: %s", template.get("name", "unknown"))
    pdf_bytes = HTML(string=html_string).write_pdf()
    logger.info("PDF rendered: %d bytes", len(pdf_bytes))
    return pdf_bytes
