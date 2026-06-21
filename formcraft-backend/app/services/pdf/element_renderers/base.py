from abc import ABC, abstractmethod

from app.services.pdf.fonts import resolve_font_family

# Typographic constants for the deterministic shrink-to-fit capacity estimate.
_PT_PER_MM = 2.834645669  # 1 mm = 2.834645669 pt
_AVG_CHAR_WIDTH_RATIO = 0.55  # avg glyph advance as a fraction of font size (pt)
_LINE_HEIGHT_RATIO = 1.3  # line box height as a fraction of font size (pt)
_SHRINK_STEP_PT = 0.5  # font-size decrement per shrink iteration


def _fits_at_size(
    text_length: int,
    size_pt: float,
    width_mm: float,
    height_mm: float,
    max_lines: int | None = None,
) -> bool:
    """Deterministic estimate of whether *text_length* chars fit in the box.

    Uses a simple monospace-ish capacity heuristic (chars-per-line * lines).
    Same inputs always yield the same result (NFR-03). Empty text always fits.
    """
    if text_length <= 0:
        return True
    if size_pt <= 0 or width_mm <= 0 or height_mm <= 0:
        return True  # cannot measure — don't shrink

    char_width_mm = (size_pt * _AVG_CHAR_WIDTH_RATIO) / _PT_PER_MM
    line_height_mm = (size_pt * _LINE_HEIGHT_RATIO) / _PT_PER_MM

    # A single line taller than the box never fits (Edge Case #1).
    if line_height_mm > height_mm:
        return False

    chars_per_line = max(1, int(width_mm / char_width_mm))
    geometric_lines = max(1, int(height_mm / line_height_mm))
    available_lines = (
        min(geometric_lines, max_lines) if max_lines else geometric_lines
    )
    capacity = chars_per_line * available_lines
    return text_length <= capacity


class ElementHTMLRenderer(ABC):
    """Abstract base for element-to-HTML renderers."""

    @abstractmethod
    def render(self, element: dict, data: dict | None = None) -> str:
        """Return an HTML fragment for the element, absolutely positioned."""
        ...

    def _apply_line_insets(
        self,
        lines: list[str],
        element: dict,
        line_direction: str = "rtl",
        line_text_align: str = "right",
    ) -> str:
        """Wrap text lines in <p> tags with per-line padding for insets.

        Returns the inner HTML (without the outer <div>) for the lines.
        """
        fmt = element.get("formatting", {})
        layout = fmt.get("lineLayout", {})
        first_left = layout.get("first_line_left_inset_mm", 0) or 0
        last_right = layout.get("last_line_right_inset_mm", 0) or 0
        max_lines = layout.get("max_lines")

        width_mm = element.get("width_mm", 0)
        # Clamp insets so usable width stays >= 1mm
        if first_left + last_right >= width_mm:
            first_left = min(first_left, max(width_mm - last_right - 1, 0))
            last_right = min(last_right, max(width_mm - first_left - 1, 0))

        if max_lines is not None:
            lines = lines[:max_lines]

        html_parts = []
        for idx, line in enumerate(lines):
            style_parts = [f"margin:0; direction:{line_direction}; text-align:{line_text_align};"]
            if idx == 0 and first_left:
                style_parts.append(f"padding-left:{first_left}mm; box-sizing:border-box;")
            if idx == len(lines) - 1 and last_right:
                style_parts.append(f"padding-right:{last_right}mm; box-sizing:border-box;")
            style = " ".join(style_parts)
            html_parts.append(f'<p style="{style}">{line}</p>')

        return "".join(html_parts)

    def _apply_overflow_policy(
        self,
        element: dict,
        html: str,
        style: str,
        text_content: str = "",
    ) -> str:
        """Apply clip / visible / shrink-to-fit overflow policy.

        ``text_content`` is the plain (markup-free) text used to measure whether
        the content overflows the box. Returns the final
        ``<div style="...">{html}</div>`` string.
        """
        fmt = element.get("formatting", {})
        policy = fmt.get("overflow")
        if not policy:
            # Default: tafqeet overflows visibly (Q2 clarification); all others clip.
            policy = "visible" if element.get("type") == "tafqeet" else "clip"

        if policy == "visible":
            style = style.replace("overflow: hidden;", "overflow: visible;")
            return f'<div style="{style}">{html}</div>'

        if policy == "clip":
            return f'<div style="{style}">{html}</div>'

        # shrink-to-fit: only reduce font-size when the content actually
        # overflows, and never below the configured minimum (FR-08). Short
        # content that already fits keeps its configured size, preserving
        # backward compatibility for existing elements (FR-14).
        if policy == "shrink-to-fit":
            font = fmt.get("font", {})
            min_size = float(font.get("min_size_pt", 6.0))
            # Match the exact raw token _base_style emitted (int or float form).
            current_raw = font.get("size_pt", 10)
            current_size = float(current_raw)

            # Measure against the markup-free character count (newlines do not
            # consume horizontal space).
            total_length = len(text_content.replace("\n", ""))

            layout = fmt.get("lineLayout", {}) or {}
            max_lines = layout.get("max_lines")
            width_mm = element.get("width_mm", 0)
            height_mm = element.get("height_mm", 0)

            fitted_size = current_size
            # Deterministic iterative reduction (NFR-03).
            while fitted_size > min_size and not _fits_at_size(
                total_length,
                fitted_size,
                width_mm,
                height_mm,
                max_lines,
            ):
                fitted_size = round(fitted_size - _SHRINK_STEP_PT, 3)
            # Floor at min_size, but never enlarge beyond the configured size
            # (shrink-to-fit only ever reduces).
            fitted_size = min(current_size, max(fitted_size, min_size))

            if fitted_size != current_size:
                fitted_str = f"{fitted_size:g}"  # 6.0 -> "6", 7.5 -> "7.5"
                style = style.replace(
                    f"font-size: {current_raw}pt;",
                    f"font-size: {fitted_str}pt;",
                )
            return f'<div style="{style}">{html}</div>'

        return f'<div style="{style}">{html}</div>'

    def _base_style(
        self, element: dict, x_offset: float = 0.0, y_offset: float = 0.0
    ) -> str:
        """Common CSS for absolute positioning in mm with optional offset."""
        direction = element.get("direction", "auto")
        text_align = "right" if direction == "rtl" else "left"
        if direction == "auto":
            text_align = "right"

        left = element["x_mm"] + x_offset
        top = element["y_mm"] + y_offset

        fmt = element.get("formatting", {})
        font = fmt.get("font", {})

        family = resolve_font_family(font.get("family"))
        # Build font-family stack: requested family + bundled fallbacks, avoiding dupes
        bundled = {"Noto Naskh Arabic", "Noto Sans"}
        if family in bundled:
            font_family = f"'{family}', 'Noto Sans', sans-serif" if family == "Noto Naskh Arabic" else f"'{family}', 'Noto Naskh Arabic', sans-serif"
        else:
            font_family = f"'{family}', 'Noto Naskh Arabic', 'Noto Sans', sans-serif"
        size_pt = font.get("size_pt", 10)
        weight = font.get("weight", "normal")
        style = font.get("style", "normal")
        color = font.get("color")

        css = (
            f"position: absolute; "
            f"float: none; "
            f"left: {left}mm; "
            f"top: {top}mm; "
            f"width: {element['width_mm']}mm; "
            f"height: {element['height_mm']}mm; "
            f"direction: {direction}; "
            f"text-align: {text_align}; "
            f"box-sizing: border-box; "
            f"overflow: hidden; "
            f"font-family: {font_family}; "
            f"font-size: {size_pt}pt; "
            f"font-weight: {weight}; "
            f"font-style: {style}; "
        )
        if color:
            css += f"color: {color}; "
        return css
