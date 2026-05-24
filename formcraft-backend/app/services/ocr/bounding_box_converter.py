"""Convert OCR bounding boxes from pixel coordinates to millimeters."""

import logging
from typing import TypedDict

logger = logging.getLogger(__name__)


class BBox(TypedDict):
    """Bounding box in mm coordinates."""

    x: float
    y: float
    width: float
    height: float


class BoundingBoxConverter:
    """Converts pixel coordinates to mm based on DPI and page dimensions."""

    # Standard conversion constants
    MM_PER_INCH = 25.4
    DEFAULT_DPI = 96  # Screen DPI; adjust based on actual scan resolution

    def __init__(self, image_width_px: int, image_height_px: int, dpi: int = DEFAULT_DPI):
        """
        Initialize converter.

        Args:
            image_width_px: Image width in pixels
            image_height_px: Image height in pixels
            dpi: Dots per inch (resolution)
        """
        self.image_width_px = image_width_px
        self.image_height_px = image_height_px
        self.dpi = dpi

        # Calculate page dimensions in mm
        self.page_width_mm = (image_width_px / dpi) * self.MM_PER_INCH
        self.page_height_mm = (image_height_px / dpi) * self.MM_PER_INCH

        logger.info(
            f"Initialized converter: {image_width_px}x{image_height_px}px @ {dpi}dpi "
            f"→ {self.page_width_mm:.2f}x{self.page_height_mm:.2f}mm"
        )

    def px_to_mm(self, px: float) -> float:
        """Convert pixels to millimeters."""
        return (px / self.dpi) * self.MM_PER_INCH

    def mm_to_px(self, mm: float) -> float:
        """Convert millimeters to pixels."""
        return (mm / self.MM_PER_INCH) * self.dpi

    def convert_bbox(self, bbox_px: dict) -> BBox:
        """
        Convert bounding box from pixels to mm, clipped to page bounds.

        Args:
            bbox_px: {x, y, width, height} in pixels

        Returns:
            {x, y, width, height} in mm
        """
        x = round(self.px_to_mm(bbox_px["x"]), 2)
        y = round(self.px_to_mm(bbox_px["y"]), 2)
        w = round(self.px_to_mm(bbox_px["width"]), 2)
        h = round(self.px_to_mm(bbox_px["height"]), 2)

        # T052: Clip to page bounds
        x = max(0.0, min(x, self.page_width_mm))
        y = max(0.0, min(y, self.page_height_mm))
        if x + w > self.page_width_mm:
            w = round(self.page_width_mm - x, 2)
        if y + h > self.page_height_mm:
            h = round(self.page_height_mm - y, 2)

        return BBox(
            x=x,
            y=y,
            width=max(w, 0.0),
            height=max(h, 0.0),
        )

    def convert_bbox_to_page(
        self,
        bbox_px: dict,
        target_width_mm: float,
        target_height_mm: float,
    ) -> BBox:
        """Convert bounding box from pixels to mm, scaled to a target page size.

        Instead of using DPI-based conversion, this scales pixel coordinates
        directly to the target page dimensions.  When the image aspect ratio
        differs from the page aspect ratio the image is letterboxed /
        pillarboxed (centred) and coordinates are adjusted accordingly.

        Args:
            bbox_px: {x, y, width, height} in pixels
            target_width_mm: Target page width in millimetres
            target_height_mm: Target page height in millimetres

        Returns:
            {x, y, width, height} in mm, clipped to page bounds
        """
        img_aspect = self.image_width_px / self.image_height_px
        page_aspect = target_width_mm / target_height_mm

        if abs(img_aspect - page_aspect) < 0.01:
            # Aspect ratios match — simple proportional scaling
            scale_x = target_width_mm / self.image_width_px
            scale_y = target_height_mm / self.image_height_px
            offset_x = 0.0
            offset_y = 0.0
        elif img_aspect > page_aspect:
            # Image is wider — fit width, letterbox vertically
            scale_x = target_width_mm / self.image_width_px
            scale_y = scale_x  # uniform scale
            rendered_height = self.image_height_px * scale_y
            offset_x = 0.0
            offset_y = (target_height_mm - rendered_height) / 2
        else:
            # Image is taller — fit height, pillarbox horizontally
            scale_y = target_height_mm / self.image_height_px
            scale_x = scale_y  # uniform scale
            rendered_width = self.image_width_px * scale_x
            offset_x = (target_width_mm - rendered_width) / 2
            offset_y = 0.0

        x = bbox_px["x"] * scale_x + offset_x
        y = bbox_px["y"] * scale_y + offset_y
        w = bbox_px["width"] * scale_x
        h = bbox_px["height"] * scale_y

        # Clip to page bounds
        x = max(0.0, min(x, target_width_mm))
        y = max(0.0, min(y, target_height_mm))
        if x + w > target_width_mm:
            w = target_width_mm - x
        if y + h > target_height_mm:
            h = target_height_mm - y

        return BBox(
            x=round(x, 2),
            y=round(y, 2),
            width=round(max(w, 0), 2),
            height=round(max(h, 0), 2),
        )

    def get_page_dimensions_mm(self) -> tuple[float, float]:
        """Get page dimensions in mm."""
        return (round(self.page_width_mm, 2), round(self.page_height_mm, 2))

    @classmethod
    def detect_dpi_from_exif(cls, image_bytes: bytes) -> int:
        """
        Attempt to detect DPI from image EXIF data.

        Args:
            image_bytes: Image file content

        Returns:
            DPI value or DEFAULT_DPI if not found
        """
        try:
            from PIL import Image
            import io

            img = Image.open(io.BytesIO(image_bytes))
            dpi = img.info.get("dpi")

            if dpi:
                # PIL returns tuple (x_dpi, y_dpi)
                if isinstance(dpi, tuple):
                    dpi_value = int(dpi[0])
                else:
                    dpi_value = int(dpi)

                logger.info(f"Detected DPI from EXIF: {dpi_value}")
                return dpi_value

        except Exception as e:
            logger.warning(f"Failed to detect DPI from EXIF: {e}")

        logger.info(f"Using default DPI: {cls.DEFAULT_DPI}")
        return cls.DEFAULT_DPI
