"""Main PDF render orchestrator using WeasyPrint."""

import logging

from weasyprint import HTML, default_url_fetcher

from app.services.pdf.html_builder import build_html

logger = logging.getLogger(__name__)

# Cap on how long WeasyPrint may wait fetching a single remote resource
# (e.g. a page background image). Without this, an unreachable URL blocks
# the worker indefinitely on the OS-level TCP timeout — and with a single
# uvicorn worker that stalls the entire backend well past the proxy timeout.
_RESOURCE_FETCH_TIMEOUT_S = 10


def _safe_url_fetcher(url: str, timeout: int = _RESOURCE_FETCH_TIMEOUT_S, ssl_context=None):
    """URL fetcher with a hard network timeout and a scheme allowlist.

    Allows http(s) (with timeout), plus local ``data:`` URIs and ``file://``
    (bundled fonts) which resolve instantly. Rejects everything else — notably
    stale ``blob:`` URLs that may be saved as page backgrounds — so WeasyPrint
    skips the resource instead of hanging the worker on an unreachable host.
    """
    if url.startswith(("http://", "https://")):
        return default_url_fetcher(url, timeout=_RESOURCE_FETCH_TIMEOUT_S, ssl_context=ssl_context)
    if url.startswith(("data:", "file:")):
        return default_url_fetcher(url, ssl_context=ssl_context)
    raise ValueError(f"Refusing to fetch unsupported URL scheme: {url[:32]}")


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
    pdf_bytes = HTML(string=html_string, url_fetcher=_safe_url_fetcher).write_pdf()
    logger.info("PDF rendered: %d bytes", len(pdf_bytes))
    return pdf_bytes
