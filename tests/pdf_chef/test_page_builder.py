from pathlib import Path

import pytest
from pypdf import PdfReader
from reportlab.lib.units import mm

from pdf_chef.config.config_model import ConfigModel
from pdf_chef.constants import WORKING_PAGE_HEIGHT_MM
from pdf_chef.page_builder import PageBuilder
from pdf_chef.text_segment import TextSegment


# Testing the "PageBuilder.__init__" method.


def test_init_creates_output_directory(config: ConfigModel) -> None:
    """The folder that will hold the output PDF is created."""

    PageBuilder(config=config)

    assert Path(config.io.output_file_path).parent.is_dir()


# Testing the "_measure_text_block" method from the "PageBuilder" class.


def test_measure_text_block_short_text_is_one_line(config: ConfigModel) -> None:
    """Text that fits within the line width is kept on a single line."""

    page = PageBuilder(config=config)

    lines, text_height = page._measure_text_block(text="Kort")

    assert lines == ["Kort"]
    assert text_height == pytest.approx(16 * 1.2)


def test_measure_text_block_wraps_long_text(config: ConfigModel) -> None:
    """Text wider than the maximum line width is wrapped without losing words."""

    page = PageBuilder(config=config)
    text = "een zin met meerdere woorden die niet op een regel past"

    lines, _ = page._measure_text_block(text=text, max_line_width=60)

    assert len(lines) > 1
    assert " ".join(lines) == text


def test_measure_text_block_keeps_explicit_newlines(config: ConfigModel) -> None:
    """Explicit newlines start a new line, even when the text is short."""

    page = PageBuilder(config=config)

    lines, _ = page._measure_text_block(text="regel een\nregel twee")

    assert lines == ["regel een", "regel twee"]


def test_measure_text_block_empty_text_has_no_lines(config: ConfigModel) -> None:
    """Empty text produces no lines and no height."""

    page = PageBuilder(config=config)

    lines, text_height = page._measure_text_block(text="")

    assert lines == []
    assert text_height == 0


# Testing the "draw_text_block" method from the "PageBuilder" class.


def test_draw_text_block_returns_position_below_start(config: ConfigModel) -> None:
    """The returned divider position is lower than the starting position."""

    page = PageBuilder(config=config)

    y_section_divider = page.draw_text_block(
        text="Test", x=20, y=500, background_color=None
    )

    assert y_section_divider < 500


def test_draw_text_block_joins_list_lines(config: ConfigModel) -> None:
    """A list of lines is drawn as one block, one line per item."""

    page = PageBuilder(config=config)

    single_line_bottom = page.draw_text_block(
        text="een", x=20, y=500, background_color=None
    )
    list_bottom = page.draw_text_block(
        text=["een", "twee"], x=20, y=500, background_color=None
    )

    assert list_bottom < single_line_bottom


# Testing the "draw_structured_block" method from the "PageBuilder" class.


def test_draw_structured_block_without_background_returns_divider(
    config: ConfigModel,
) -> None:
    """A structured block without a background still returns its divider."""

    page = PageBuilder(config=config)
    segments = [TextSegment(text="Stap een", indent=12.0, space_before=4.0)]

    y_section_divider = page.draw_structured_block(
        segments=segments, x=20, y=500, background_color=None
    )

    assert y_section_divider < 500


# Testing the "save" method from the "PageBuilder" class.


def test_save_keeps_full_height_without_content_bottoms(config: ConfigModel) -> None:
    """Without crop positions the working page height is kept."""

    page = PageBuilder(config=config)
    page.new_page()
    page.save()

    reader = PdfReader(config.io.output_file_path)
    mediabox = reader.pages[0].mediabox

    assert float(mediabox.top) == pytest.approx(WORKING_PAGE_HEIGHT_MM * mm)


def test_save_crops_bottom_to_content(config: ConfigModel) -> None:
    """The page bottom is raised to the given content bottom position."""

    page = PageBuilder(config=config)
    page.save(content_bottom_ys=[300.0])

    reader = PdfReader(config.io.output_file_path)
    mediabox = reader.pages[0].mediabox

    assert float(mediabox.bottom) == pytest.approx(300.0)
