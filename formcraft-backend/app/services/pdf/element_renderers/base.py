from abc import ABC, abstractmethod

from app.services.pdf.fonts import resolve_font_family


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
    ) -> str:
        """Apply clip / visible / shrink-to-fit overflow policy.

        Returns the final <div style="...">{html}</div> string.
        """
        fmt = element.get("formatting", {})
        policy = fmt.get("overflow")
        if not policy:
            # Default per edge-case #4
            policy = "shrink-to-fit" if element.get("type") == "tafqeet" else "clip"

        if policy == "visible":
            style = style.replace("overflow: hidden;", "overflow: visible;")
            return f'<div style="{style}">{html}</div>'

        if policy == "clip":
            return f'<div style="{style}">{html}</div>'

        # shrink-to-fit: reduce font-size iteratively
        if policy == "shrink-to-fit":
            font = fmt.get("font", {})
            min_size = font.get("min_size_pt", 6.0)
            current_size = font.get("size_pt", 10)
            if current_size > min_size:
                style = style.replace(f"font-size: {current_size}pt;", f"font-size: {min_size}pt;")
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
