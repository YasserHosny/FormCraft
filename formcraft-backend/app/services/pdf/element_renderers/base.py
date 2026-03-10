from abc import ABC, abstractmethod


class ElementHTMLRenderer(ABC):
    """Abstract base for element-to-HTML renderers."""

    @abstractmethod
    def render(self, element: dict, data: dict | None = None) -> str:
        """Return an HTML fragment for the element, absolutely positioned."""
        ...

    def _base_style(self, element: dict) -> str:
        """Common CSS for absolute positioning in mm."""
        direction = element.get("direction", "auto")
        text_align = "right" if direction == "rtl" else "left"
        if direction == "auto":
            text_align = "right"  # Arabic-first default

        return (
            f"position: absolute; "
            f"left: {element['x_mm']}mm; "
            f"top: {element['y_mm']}mm; "
            f"width: {element['width_mm']}mm; "
            f"height: {element['height_mm']}mm; "
            f"direction: {direction}; "
            f"text-align: {text_align}; "
            f"box-sizing: border-box; "
            f"overflow: hidden; "
            f"font-family: 'Noto Naskh Arabic', 'Noto Sans', sans-serif; "
            f"font-size: 10pt; "
        )
