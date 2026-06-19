from app.services.pdf.element_renderers.base import ElementHTMLRenderer


class TextRenderer(ElementHTMLRenderer):
    def render(self, element: dict, data: dict | None = None) -> str:
        style = self._base_style(element)
        key = element.get("key", "")

        # When field_values (data) are provided and this element has a matching key,
        # show the submitted value; otherwise fall back to the label text.
        if data is not None and key and data.get(key) is not None:
            display_text = str(data[key])
        else:
            display_text = element.get("label_ar", "") or element.get("label_en", "")

        fmt = element.get("formatting", {})
        layout = fmt.get("lineLayout", {})
        has_insets = (
            layout.get("first_line_left_inset_mm")
            or layout.get("last_line_right_inset_mm")
            or layout.get("max_lines")
        )

        direction = element.get("direction", "auto")
        text_align = "right" if direction == "rtl" else "left"
        if direction == "auto":
            text_align = "right"
        line_direction = "rtl" if text_align == "right" else "ltr"

        if has_insets:
            lines = display_text.split("\n")
            html = self._apply_line_insets(
                lines, element, line_direction=line_direction, line_text_align=text_align
            )
        else:
            html = display_text

        return self._apply_overflow_policy(
            element, html, style, text_content=display_text
        )
