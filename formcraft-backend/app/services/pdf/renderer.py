"""Main PDF render orchestrator using WeasyPrint."""

import logging

from weasyprint import HTML

from app.services.pdf.html_builder import build_html

logger = logging.getLogger(__name__)


def render_template_pdf(
    template: dict,
    overlay_mode: bool = False,
    x_offset_mm: float = 0.0,
    y_offset_mm: float = 0.0,
    field_values: dict | None = None,
) -> bytes:
    """Render a template dict to PDF bytes via WeasyPrint."""
    html_string = build_html(
        template,
        overlay_mode=overlay_mode,
        x_offset_mm=x_offset_mm,
        y_offset_mm=y_offset_mm,
        field_values=field_values or {},
    )
    mode_label = "overlay" if overlay_mode else "full"
    logger.info("Rendering %s PDF for template: %s", mode_label, template.get("name", "unknown"))
    pdf_bytes = HTML(string=html_string).write_pdf()
    logger.info("PDF rendered: %d bytes", len(pdf_bytes))
    return pdf_bytes
