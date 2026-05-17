from abc import ABC, abstractmethod


class ElementHTMLRenderer(ABC):
    """Abstract base for element-to-HTML renderers."""

    @abstractmethod
    def render(self, element: dict, data: dict | None = None) -> str:
        """Return an HTML fragment for the element, absolutely positioned."""
        ...

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

        return (
            f"position: absolute; "
            f"left: {left}mm; "
            f"top: {top}mm; "
            f"width: {element['width_mm']}mm; "
            f"height: {element['height_mm']}mm; "
            f"direction: {direction}; "
            f"text-align: {text_align}; "
            f"box-sizing: border-box; "
            f"overflow: hidden; "
            f"font-family: 'Noto Naskh Arabic', 'Noto Sans', sans-serif; "
            f"font-size: 10pt; "
        )
