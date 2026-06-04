import pytest
from pydantic import ValidationError

from app.schemas.element import ElementFormatting, FontSettings, LineLayout


class TestFontSettings:
    def test_valid(self):
        f = FontSettings(family="Noto Sans", size_pt=12, weight="bold", style="italic", color="#333333")
        assert f.family == "Noto Sans"
        assert f.size_pt == 12
        assert f.weight == "bold"
        assert f.style == "italic"
        assert f.color == "#333333"

    def test_defaults(self):
        f = FontSettings()
        assert f.family is None
        assert f.size_pt is None
        assert f.min_size_pt == 6.0

    def test_size_bounds(self):
        with pytest.raises(ValidationError):
            FontSettings(size_pt=0)
        with pytest.raises(ValidationError):
            FontSettings(size_pt=200)

    def test_min_size_bounds(self):
        with pytest.raises(ValidationError):
            FontSettings(min_size_pt=0)
        with pytest.raises(ValidationError):
            FontSettings(min_size_pt=200)


class TestLineLayout:
    def test_valid(self):
        ll = LineLayout(max_lines=3, first_line_left_inset_mm=22.0, last_line_right_inset_mm=26.0)
        assert ll.max_lines == 3
        assert ll.first_line_left_inset_mm == 22.0
        assert ll.last_line_right_inset_mm == 26.0

    def test_defaults(self):
        ll = LineLayout()
        assert ll.max_lines is None
        assert ll.first_line_left_inset_mm is None
        assert ll.last_line_right_inset_mm is None

    def test_max_lines_bounds(self):
        with pytest.raises(ValidationError):
            LineLayout(max_lines=0)
        with pytest.raises(ValidationError):
            LineLayout(max_lines=200)

    def test_inset_non_negative(self):
        with pytest.raises(ValidationError):
            LineLayout(first_line_left_inset_mm=-1)
        with pytest.raises(ValidationError):
            LineLayout(last_line_right_inset_mm=-1)


class TestElementFormatting:
    def test_valid(self):
        ef = ElementFormatting(
            font=FontSettings(family="Courier", size_pt=13),
            line_layout=LineLayout(max_lines=2, first_line_left_inset_mm=22),
            overflow="shrink-to-fit",
        )
        assert ef.font.family == "Courier"
        assert ef.line_layout.max_lines == 2
        assert ef.overflow == "shrink-to-fit"

    def test_defaults(self):
        ef = ElementFormatting()
        assert ef.font is None
        assert ef.line_layout is None
        assert ef.overflow is None

    def test_overflow_literal(self):
        with pytest.raises(ValidationError):
            ElementFormatting(overflow="invalid")
