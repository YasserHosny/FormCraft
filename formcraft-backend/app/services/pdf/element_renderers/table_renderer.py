from app.services.pdf.element_renderers.base import ElementHTMLRenderer


class TableRenderer(ElementHTMLRenderer):
    def render(self, element: dict, data: dict | None = None) -> str:
        style = self._base_style(element)
        props = element.get("properties", {})
        columns = props.get("columns", [])
        show_header = props.get("show_header", True)
        show_borders = props.get("show_borders", True)
        show_footer = props.get("show_footer", True)

        border_css = "border: 1pt solid #333;" if show_borders else "border: none;"

        rows = data if isinstance(data, list) else []

        dir_attr = 'dir="rtl"' if element.get("direction", "auto") in ("rtl", "auto") else ""

        col_widths = [f"{c.get('width_mm', 40)}mm" for c in columns] if columns else []
        colgroup = "<colgroup>"
        for w in col_widths:
            colgroup += f'<col style="width: {w};">'
        colgroup += "</colgroup>"

        header_html = ""
        if show_header and columns:
            header_cells = ""
            for col in columns:
                header_text = col.get("header_ar", "") or col.get("header_en", "")
                header_cells += f"<th style='{border_css} padding: 2pt 4pt; font-weight: bold; font-size: 9pt;'>{header_text}</th>"
            header_html = f"<thead><tr>{header_cells}</tr></thead>"

        body_html = ""
        for row in rows:
            cells = ""
            for col in columns:
                key = col.get("key", "")
                val = row.get(key, "") if isinstance(row, dict) else ""
                val_str = str(val) if val is not None else ""
                cells += f"<td style='{border_css} padding: 2pt 4pt; font-size: 9pt;'>{val_str}</td>"
            body_html += f"<tr>{cells}</tr>"
        body_html = f"<tbody>{body_html}</tbody>" if body_html else "<tbody></tbody>"

        footer_html = ""
        if show_footer and columns:
            sum_cols = [c for c in columns if c.get("auto_sum", False)]
            if sum_cols and rows:
                footer_cells = ""
                cell_idx = 0
                for col in columns:
                    if col.get("auto_sum", False):
                        total = sum(
                            float(row.get(col["key"], 0) or 0)
                            for row in rows
                            if isinstance(row, dict)
                        )
                        total = round(total, 2)
                        footer_cells += f"<td style='{border_css} padding: 2pt 4pt; font-weight: bold; font-size: 9pt;'>{total}</td>"
                    elif cell_idx == 0:
                        footer_cells += f"<td style='{border_css} padding: 2pt 4pt; font-weight: bold; font-size: 9pt;'>Σ</td>"
                    else:
                        footer_cells += f"<td style='{border_css} padding: 2pt 4pt; font-size: 9pt;'>&nbsp;</td>"
                    cell_idx += 1
                footer_html = f"<tfoot><tr>{footer_cells}</tr></tfoot>"

        table_html = (
            f"<table {dir_attr} style='width: 100%; border-collapse: collapse; "
            f"page-break-inside: avoid;'>"
            f"{colgroup}{header_html}{body_html}{footer_html}</table>"
        )

        return f'<div style="{style} overflow: auto;">{table_html}</div>'