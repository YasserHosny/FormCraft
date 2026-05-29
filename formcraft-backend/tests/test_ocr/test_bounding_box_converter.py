"""Unit tests for BoundingBoxConverter."""

import io
import pytest

from app.services.ocr.bounding_box_converter import BoundingBoxConverter


# --- T008: convert_bbox and get_page_dimensions_mm ---


class TestConvertBbox:
    def test_convert_at_96dpi(self, sample_bbox_px):
        converter = BoundingBoxConverter(800, 600, dpi=96)
        result = converter.convert_bbox(sample_bbox_px)
        # 100px at 96dpi = 100/96 * 25.4 = 26.46mm
        assert result["x"] == pytest.approx(26.46, abs=0.1)
        assert result["y"] == pytest.approx(52.92, abs=0.1)
        assert result["width"] == pytest.approx(79.38, abs=0.1)
        assert result["height"] == pytest.approx(13.23, abs=0.1)

    def test_convert_at_300dpi(self, sample_bbox_px):
        converter = BoundingBoxConverter(2400, 1800, dpi=300)
        result = converter.convert_bbox(sample_bbox_px)
        # 100px at 300dpi = 100/300 * 25.4 = 8.47mm
        assert result["x"] == pytest.approx(8.47, abs=0.1)
        assert result["y"] == pytest.approx(16.93, abs=0.1)
        assert result["width"] == pytest.approx(25.4, abs=0.1)
        assert result["height"] == pytest.approx(4.23, abs=0.1)

    def test_convert_at_150dpi(self):
        converter = BoundingBoxConverter(1200, 900, dpi=150)
        bbox = {"x": 150, "y": 300, "width": 450, "height": 75}
        result = converter.convert_bbox(bbox)
        # 150px at 150dpi = 25.4mm
        assert result["x"] == pytest.approx(25.4, abs=0.1)
        assert result["y"] == pytest.approx(50.8, abs=0.1)

    def test_convert_zero_bbox(self):
        converter = BoundingBoxConverter(800, 600, dpi=96)
        result = converter.convert_bbox({"x": 0, "y": 0, "width": 0, "height": 0})
        assert result["x"] == 0.0
        assert result["y"] == 0.0
        assert result["width"] == 0.0
        assert result["height"] == 0.0


class TestPageDimensions:
    def test_page_dimensions_96dpi(self):
        converter = BoundingBoxConverter(800, 600, dpi=96)
        w, h = converter.get_page_dimensions_mm()
        # 800/96 * 25.4 = 211.67mm, 600/96 * 25.4 = 158.75mm
        assert w == pytest.approx(211.67, abs=0.5)
        assert h == pytest.approx(158.75, abs=0.5)

    def test_page_dimensions_300dpi_a4(self):
        # A4 at 300dpi = 2480x3508 pixels
        converter = BoundingBoxConverter(2480, 3508, dpi=300)
        w, h = converter.get_page_dimensions_mm()
        assert w == pytest.approx(210.0, abs=1.0)
        assert h == pytest.approx(297.0, abs=1.0)

    def test_page_dimensions_72dpi(self):
        converter = BoundingBoxConverter(595, 842, dpi=72)
        w, h = converter.get_page_dimensions_mm()
        # Standard PDF page at 72dpi ≈ A4
        assert w == pytest.approx(210.0, abs=1.0)
        assert h == pytest.approx(297.0, abs=1.0)


class TestPxMmConversions:
    def test_px_to_mm(self):
        converter = BoundingBoxConverter(800, 600, dpi=96)
        assert converter.px_to_mm(96) == pytest.approx(25.4, abs=0.01)

    def test_mm_to_px(self):
        converter = BoundingBoxConverter(800, 600, dpi=96)
        assert converter.mm_to_px(25.4) == pytest.approx(96.0, abs=0.01)

    def test_roundtrip(self):
        converter = BoundingBoxConverter(800, 600, dpi=300)
        original_px = 150.0
        mm = converter.px_to_mm(original_px)
        back_to_px = converter.mm_to_px(mm)
        assert back_to_px == pytest.approx(original_px, abs=0.01)


# --- T009: detect_dpi_from_exif ---


# --- T038: Page-dimension-aware coordinate conversion ---


class TestConvertBboxToPage:
    def test_a4_proportional(self):
        """A4 page with matching aspect ratio — simple proportional scaling."""
        # Image 2100x2970 px → A4 210x297mm = 1px per 0.1mm
        converter = BoundingBoxConverter(2100, 2970, dpi=96)
        bbox = {"x": 100, "y": 200, "width": 300, "height": 50}
        result = converter.convert_bbox_to_page(bbox, 210.0, 297.0)
        assert result["x"] == pytest.approx(10.0, abs=0.1)
        assert result["y"] == pytest.approx(20.0, abs=0.1)
        assert result["width"] == pytest.approx(30.0, abs=0.1)
        assert result["height"] == pytest.approx(5.0, abs=0.1)

    def test_a5_landscape(self):
        """A5 landscape page (210x148mm)."""
        converter = BoundingBoxConverter(2100, 1480, dpi=96)
        bbox = {"x": 0, "y": 0, "width": 2100, "height": 1480}
        result = converter.convert_bbox_to_page(bbox, 210.0, 148.0)
        assert result["x"] == pytest.approx(0.0, abs=0.5)
        assert result["y"] == pytest.approx(0.0, abs=0.5)
        assert result["width"] == pytest.approx(210.0, abs=0.5)
        assert result["height"] == pytest.approx(148.0, abs=0.5)

    def test_mismatched_aspect_wider_image(self):
        """Wide image on tall page — stretch-to-fill (no letterbox)."""
        # Image 1000x500 (2:1 aspect) → Page 210x297 (0.71 aspect)
        converter = BoundingBoxConverter(1000, 500, dpi=96)
        bbox = {"x": 500, "y": 250, "width": 100, "height": 50}
        result = converter.convert_bbox_to_page(bbox, 210.0, 297.0)
        # scale_x = 210/1000 = 0.21, scale_y = 297/500 = 0.594
        # x = 500 * 0.21 = 105.0
        assert result["x"] == pytest.approx(105.0, abs=1.0)
        # y = 250 * 0.594 = 148.5 (no offset)
        assert result["y"] == pytest.approx(148.5, abs=1.0)

    def test_mismatched_aspect_taller_image(self):
        """Tall image on wide page — stretch-to-fill (no pillarbox)."""
        # Image 500x1000 (0.5 aspect) → Page 210x148 (1.42 aspect)
        converter = BoundingBoxConverter(500, 1000, dpi=96)
        bbox = {"x": 0, "y": 0, "width": 500, "height": 1000}
        result = converter.convert_bbox_to_page(bbox, 210.0, 148.0)
        # scale_x = 210/500 = 0.42, scale_y = 148/1000 = 0.148
        # Full image maps to full page
        assert result["x"] == pytest.approx(0.0, abs=0.5)
        assert result["y"] == pytest.approx(0.0, abs=0.5)
        assert result["width"] == pytest.approx(210.0, abs=0.5)
        assert result["height"] == pytest.approx(148.0, abs=0.5)

    def test_page_boundary_clipping(self):
        """Detection extending past page boundary is clipped."""
        converter = BoundingBoxConverter(1000, 1000, dpi=96)
        # Bbox at far edge — would extend past page
        bbox = {"x": 950, "y": 950, "width": 200, "height": 200}
        result = converter.convert_bbox_to_page(bbox, 210.0, 297.0)
        # x + width should not exceed 210, y + height should not exceed 297
        assert result["x"] + result["width"] <= 210.0
        assert result["y"] + result["height"] <= 297.0

    def test_custom_dimensions(self):
        """Custom page size (e.g., cheque 200x90mm)."""
        converter = BoundingBoxConverter(800, 360, dpi=96)
        bbox = {"x": 400, "y": 180, "width": 100, "height": 30}
        result = converter.convert_bbox_to_page(bbox, 200.0, 90.0)
        # Aspect matches: 800/360 = 2.22, 200/90 = 2.22
        assert result["x"] == pytest.approx(100.0, abs=1.0)
        assert result["y"] == pytest.approx(45.0, abs=1.0)


class TestDetectDpiFromExif:
    def test_default_dpi_for_no_exif(self):
        """Images without EXIF should return default 96 DPI."""
        # Create minimal valid PNG with no EXIF
        import struct

        # Minimal 1x1 PNG
        png_header = b"\x89PNG\r\n\x1a\n"
        # IHDR chunk
        ihdr_data = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
        ihdr_crc = struct.pack(">I", 0x69B3F52D)  # Precalculated
        ihdr = struct.pack(">I", 13) + b"IHDR" + ihdr_data + ihdr_crc
        # IEND chunk
        iend = struct.pack(">I", 0) + b"IEND" + struct.pack(">I", 0xAE426082)

        png_bytes = png_header + ihdr + iend

        # This may fail to parse but should return default DPI
        dpi = BoundingBoxConverter.detect_dpi_from_exif(png_bytes)
        assert dpi == 96

    def test_default_dpi_for_invalid_data(self):
        """Invalid image data should return default 96 DPI."""
        dpi = BoundingBoxConverter.detect_dpi_from_exif(b"not an image")
        assert dpi == 96

    def test_default_dpi_for_empty_data(self):
        """Empty data should return default 96 DPI."""
        dpi = BoundingBoxConverter.detect_dpi_from_exif(b"")
        assert dpi == 96

    def test_detect_dpi_from_jpeg_with_dpi(self):
        """JPEG with DPI in EXIF should return that DPI."""
        from PIL import Image

        img = Image.new("RGB", (100, 100), color="white")
        buf = io.BytesIO()
        img.save(buf, format="JPEG", dpi=(300, 300))
        buf.seek(0)

        dpi = BoundingBoxConverter.detect_dpi_from_exif(buf.read())
        assert dpi == 300

    def test_detect_dpi_from_jpeg_default(self):
        """JPEG without explicit DPI info should return default."""
        from PIL import Image

        img = Image.new("RGB", (100, 100), color="white")
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        buf.seek(0)

        dpi = BoundingBoxConverter.detect_dpi_from_exif(buf.read())
        # PIL may or may not include default DPI, accept either
        assert dpi in (72, 96, 300)  # Common defaults
