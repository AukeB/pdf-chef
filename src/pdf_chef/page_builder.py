"""Module for creating PDF documents using the ReportLab package."""

from typing import Tuple
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader, PdfWriter

from pdf_chef.config_manager import Config
from pdf_chef.constants import WORKING_PAGE_HEIGHT_MM
from pdf_chef.text_segment import TextSegment
from pdf_chef.utils.utils_file_system import ensure_directory


class PageBuilder:
    """Build simple PDFs with custom page sizes using ReportLab.

    Wraps a ReportLab canvas and provides helpers for drawing images, text
    blocks with word wrapping and optional backgrounds, and horizontal dividers,
    all driven by a shared configuration object.
    """

    def __init__(self, config: Config) -> None:
        """Initialize a PageBuilder instance.

        Prepares the output directory, creates the ReportLab canvas at the
        configured page size, and sets the default font.

        Args:
            config (Config): Validated configuration controlling page layout,
                margins, fonts, and colors.
        """

        # Variables
        self.config = config
        self.output_file_path = self.config.io.output_file_path
        self.page_height = WORKING_PAGE_HEIGHT_MM * mm
        self.max_line_width = (
            self.config.page.width * mm
            - self.config.document_margins.left
            - self.config.document_margins.right
        )

        # Actions
        ensure_directory(self.output_file_path)
        self.canvas = self._initialize_document()
        self._set_font()

    def _initialize_document(
        self,
    ) -> canvas.Canvas:
        """Initialize a ReportLab canvas with the configured page size.

        Returns:
            canvas.Canvas: A ReportLab canvas object.
        """

        page_size = (self.config.page.width * mm, self.page_height)
        return canvas.Canvas(self.output_file_path, pagesize=page_size)

    def _set_font(
        self, font_name: str | None = None, font_size: int | None = None
    ) -> None:
        """Set the active font for the canvas.

        Args:
            font_name (str | None): Optional font name override. Falls back to
                the configured font name when omitted.
            font_size (int | None): Optional font size override. Falls back to
                the configured font size when omitted.
        """

        font_name = font_name or self.config.typography.default.font_name
        font_size = font_size or self.config.typography.default.font_size

        self.canvas.setFont(font_name, font_size)

    def draw_horizontal_line(
        self, y: float, line_color: Tuple[float, float, float] | None = None
    ) -> None:
        """Draw a full-width horizontal line at a given vertical position.

        Args:
            y (float): Vertical position of the line, in points.
            line_color (Tuple[float, float, float] | None): Optional normalized
                RGB stroke color. Falls back to the configured line color.
        """

        line_color = line_color or self.config.colors.line_color

        self.canvas.setStrokeColorRGB(*line_color)
        self.canvas.line(0, y, self.config.page.width * mm, y)

    def draw_image(self, image_path: str | None, y_pos: float) -> float:
        """Draw a cover image centered on the page with a fixed height.

        The image is scaled to the configured cover height while preserving its
        aspect ratio, and a horizontal divider is drawn beneath it. When no
        image is available, a full-width placeholder rectangle filled with the
        configured placeholder color is drawn instead.

        Args:
            image_path (str | None): Path to the image file to draw, or ``None``
                to draw a placeholder rectangle.
            y_pos (float): Vertical position of the top of the image, in points.

        Returns:
            float: The vertical position of the divider drawn below the image,
                in points.
        """

        image_height = self.config.layout_cover.image_height
        y_section_divider = y_pos - image_height

        if image_path is None:
            self.canvas.setFillColorRGB(*self.config.layout_cover.placeholder_color)
            self.canvas.rect(
                x=0,
                y=y_section_divider,
                width=self.config.page.width * mm,
                height=image_height,
                stroke=0,
                fill=1,
            )

            self.canvas.setFillColorRGB(0, 0, 0)
            self.draw_horizontal_line(y=y_section_divider)
            return y_section_divider

        image = ImageReader(image_path)
        initial_image_width, initial_image_height = image.getSize()

        image_scaling_factor = image_height / initial_image_height
        image_width = initial_image_width * image_scaling_factor
        x_image = (self.config.page.width * mm - image_width) / 2
        y_image = y_pos - image_height

        self.canvas.drawImage(image_path, x_image, y_image, image_width, image_height)

        self.draw_horizontal_line(y=y_section_divider)

        return y_section_divider

    def _measure_text_block(
        self,
        text: str,
        font_name: str | None = None,
        font_size: int | None = None,
        max_line_width: float | None = None,
    ) -> tuple[list[str], float]:
        """Measure how the text will wrap and its total height.

        Args:
            text (str): Text to measure.
            font_name (str | None): Optional font override.
            font_size (int | None): Optional font size override.
            max_line_width (float | None): Optional maximum line width override.

        Returns:
            tuple[list[str], float]: The wrapped lines of text and the total
                text height in points.
        """

        font_name = font_name or self.config.typography.default.font_name
        font_size = font_size or self.config.typography.default.font_size
        max_line_width = max_line_width or self.max_line_width

        line_height = font_size * self.config.typography.default.line_height_factor

        self.canvas.setFont(font_name, font_size)

        if "\n" in text:
            words = text.splitlines(keepends=True)
            words[-1] += "\n"
        else:
            words = text.split()

        current_line = ""
        lines = []

        for word in words:
            line = f"{current_line} {word}".strip()
            line_width = self.canvas.stringWidth(line, font_name, font_size)

            if line_width > max_line_width or "\n" in word and current_line != "":
                lines.append(current_line)
                current_line = word
            elif line_width <= max_line_width:
                current_line = line

        if current_line:
            lines.append(current_line)

        lines = [line.rstrip("\n") for line in lines]

        text_height = len(lines) * line_height
        return lines, text_height

    def draw_text_block(
        self,
        text: str | list[str],
        x: float,
        y: float,
        background_color: Tuple[float, float, float] | None,
        max_line_width: float | None = None,
        font_name: str | None = None,
        font_size: int | None = None,
        line_height_factor: float | None = None,
        margin_top: float | None = None,
        margin_bottom: float | None = None,
        font_shift_factor: float | None = None,
    ) -> float:
        """Draw a wrapped text block with an optional background and divider.

        Args:
            text (str | list[str]): Text to draw. Lists are joined with newlines
                before wrapping.
            x (float): Horizontal position of the text, in points.
            y (float): Vertical position of the top of the block, in points.
            background_color (Tuple[float, float, float]): Normalized RGB
                background color. When falsy, no background is drawn.
            max_line_width (float | None): Optional maximum line width override.
            font_name (str | None): Optional font name override.
            font_size (int | None): Optional font size override.
            line_height_factor (float | None): Optional line height factor
                override.
            margin_top (float | None): Optional top margin override.
            margin_bottom (float | None): Optional bottom margin override.
            font_shift_factor (float | None): Optional font shift factor
                override used to correct vertical text placement.

        Returns:
            float: The vertical position of the divider drawn below the block,
                in points.
        """

        max_line_width = max_line_width or self.max_line_width
        font_name = font_name or self.config.typography.default.font_name
        font_size = font_size or self.config.typography.default.font_size
        line_height_factor = (
            line_height_factor or self.config.typography.default.line_height_factor
        )
        margin_top = margin_top or self.config.section_margins.top
        margin_bottom = margin_bottom or self.config.section_margins.bottom
        font_shift_factor = (
            font_shift_factor or self.config.typography.default.font_shift_factor
        )

        if isinstance(text, list):
            text = "\n".join(text)

        line_height = font_size * line_height_factor
        self.canvas.setFont(font_name, font_size)

        font_spacing_correction = font_shift_factor * font_size
        y_position = y - font_spacing_correction

        lines, text_height = self._measure_text_block(
            text=text,
            font_name=font_name,
            font_size=font_size,
        )

        block_height = (
            text_height + margin_top + margin_bottom + font_spacing_correction
        )
        y_block = y_position - margin_top - text_height - margin_bottom

        if background_color:
            self.canvas.setFillColorRGB(*background_color)
            self.canvas.rect(
                x=0,
                y=y_block,
                width=self.config.page.width * mm,
                height=block_height,
                stroke=0,
                fill=1,
            )
            self.canvas.setFillColorRGB(0, 0, 0)

        y_draw = y_position - margin_top

        for line in lines:
            self.canvas.drawString(x, y_draw, line)
            y_draw -= line_height

        y_section_divider = y - block_height

        self.draw_horizontal_line(y=y_section_divider)

        return y_section_divider

    def draw_structured_block(
        self,
        segments: list[TextSegment],
        x: float,
        y: float,
        background_color: Tuple[float, float, float],
        font_name: str | None = None,
        font_size: int | None = None,
        line_height_factor: float | None = None,
        margin_top: float | None = None,
        margin_bottom: float | None = None,
        font_shift_factor: float | None = None,
    ) -> float:
        """Draw a block of indented text segments sharing one background.

        Each segment is wrapped within the width remaining after its indent and
        can request extra vertical space above itself. The whole block gets a
        single background and a single divider below it.

        Args:
            segments (list[TextSegment]): Ordered text segments to draw.
            x (float): Base horizontal position of the text, in points.
            y (float): Vertical position of the top of the block, in points.
            background_color (Tuple[float, float, float]): Normalized RGB
                background color. When falsy, no background is drawn.
            font_name (str | None): Optional font name override.
            font_size (int | None): Optional font size override.
            line_height_factor (float | None): Optional line height factor
                override.
            margin_top (float | None): Optional top margin override.
            margin_bottom (float | None): Optional bottom margin override.
            font_shift_factor (float | None): Optional font shift factor
                override used to correct vertical text placement.

        Returns:
            float: The vertical position of the divider drawn below the block,
                in points.
        """

        font_name = font_name or self.config.typography.default.font_name
        font_size = font_size or self.config.typography.default.font_size
        line_height_factor = (
            line_height_factor or self.config.typography.default.line_height_factor
        )
        margin_top = margin_top or self.config.section_margins.top
        margin_bottom = margin_bottom or self.config.section_margins.bottom
        font_shift_factor = (
            font_shift_factor or self.config.typography.default.font_shift_factor
        )

        self.canvas.setFont(font_name, font_size)

        font_spacing_correction = font_shift_factor * font_size
        y_position = y - font_spacing_correction

        wrapped_segments: list[tuple[float, float, list[str], str, int, float]] = []
        content_height = 0.0

        for segment in segments:
            segment_font_name = segment.font_name or font_name
            segment_font_size = segment.font_size or font_size
            segment_line_height = segment_font_size * line_height_factor
            lines, _ = self._measure_text_block(
                text=segment.text,
                font_name=segment_font_name,
                font_size=segment_font_size,
                max_line_width=self.max_line_width - segment.indent,
            )
            wrapped_segments.append(
                (
                    segment.indent,
                    segment.space_before,
                    lines,
                    segment_font_name,
                    segment_font_size,
                    segment_line_height,
                )
            )
            content_height += segment.space_before + len(lines) * segment_line_height

        block_height = (
            content_height + margin_top + margin_bottom + font_spacing_correction
        )
        y_block = y_position - margin_top - content_height - margin_bottom

        if background_color:
            self.canvas.setFillColorRGB(*background_color)
            self.canvas.rect(
                x=0,
                y=y_block,
                width=self.config.page.width * mm,
                height=block_height,
                stroke=0,
                fill=1,
            )
            self.canvas.setFillColorRGB(0, 0, 0)

        y_draw = y_position - margin_top

        for (
            indent,
            space_before,
            lines,
            segment_font_name,
            segment_font_size,
            segment_line_height,
        ) in wrapped_segments:
            y_draw -= space_before
            self.canvas.setFont(segment_font_name, segment_font_size)
            for line in lines:
                self.canvas.drawString(x + indent, y_draw, line)
                y_draw -= segment_line_height

        y_section_divider = y - block_height

        self.draw_horizontal_line(y=y_section_divider)

        return y_section_divider

    def fill_background(self, color: Tuple[float, float, float]) -> None:
        """Fill the entire working canvas with a solid background color.

        Should be called before drawing any content on a page so the background
        sits behind all other elements.

        Args:
            color (Tuple[float, float, float]): Normalized RGB fill color.
        """

        self.canvas.setFillColorRGB(*color)
        self.canvas.rect(
            0, 0, self.config.page.width * mm, self.page_height, stroke=0, fill=1
        )
        self.canvas.setFillColorRGB(0, 0, 0)

    def draw_inline_link_right(
        self,
        text: str,
        destination: str,
        y: float,
        font_name: str,
        font_size: int,
    ) -> None:
        """Draw a right-aligned clickable link without advancing the y position.

        The text is right-aligned to the right margin of the content area and
        drawn at the exact y given. Used to overlay a link inside an existing
        block (e.g. the lower-right corner of the title block).

        Args:
            text (str): Link text to draw.
            destination (str): Named PDF destination the link navigates to.
            y (float): Vertical baseline position for the text, in points.
            font_name (str): Font to use.
            font_size (int): Font size in points.
        """

        self.canvas.setFont(font_name, font_size)
        text_width = self.canvas.stringWidth(text, font_name, font_size)
        x = (
            self.config.page.width * mm
            - self.config.document_margins.right
            - text_width
        )
        self.canvas.drawString(x, y, text)
        underline_y = y - font_size * 0.12
        self.canvas.line(x, underline_y, x + text_width, underline_y)
        self.canvas.linkAbsolute(
            "",
            destination,
            (x, underline_y - 2, x + text_width, y + font_size * 0.8),
            thickness=0,
        )

    def bookmark(self, name: str) -> None:
        """Create a named destination at the top of the current page.

        The destination uses a horizontal-fit view so navigating to it scrolls
        to the top of the page at the full page width.

        Args:
            name (str): Unique identifier for this destination.
        """

        self.canvas.bookmarkPage(name, fit="FitH", top=self.page_height)

    def draw_link_text(
        self,
        text: str,
        destination: str,
        x: float,
        y: float,
        font_name: str,
        font_size: int,
    ) -> float:
        """Draw word-wrapped, underlined, clickable text pointing to a
        destination.

        Each wrapped line is individually underlined. A single invisible link
        annotation covers the entire wrapped area.

        Args:
            text (str): Text to draw and make clickable.
            destination (str): Named PDF destination the link navigates to.
            x (float): Horizontal position of the text, in points.
            y (float): Vertical position of the first text baseline, in points.
            font_name (str): Font to use.
            font_size (int): Font size in points.

        Returns:
            float: Vertical position below the last drawn line, in points.
        """

        lines, _ = self._measure_text_block(text, font_name, font_size)
        line_height = font_size * self.config.typography.default.line_height_factor

        self.canvas.setFont(font_name, font_size)
        y_draw = y
        for line in lines:
            self.canvas.drawString(x, y_draw, line)
            line_width = self.canvas.stringWidth(line, font_name, font_size)
            underline_y = y_draw - font_size * 0.12
            self.canvas.line(x, underline_y, x + line_width, underline_y)
            y_draw -= line_height

        # One invisible link rect covering all lines.
        self.canvas.linkAbsolute(
            "",
            destination,
            (x, y_draw, x + self.max_line_width, y + font_size * 0.8),
            thickness=0,
        )

        return y_draw

    def save(self, content_bottom_ys: list[float] | None = None) -> None:
        """Finalize and save the PDF file.

        When ``content_bottom_ys`` is provided, the empty space below the drawn
        content on each page is cropped away by raising that page's bottom edge
        to the given position, producing pages sized to fit their content.

        Args:
            content_bottom_ys (list[float] | None): Vertical position of the
                bottom of the drawn content for each page, in points, ordered by
                page. When omitted, the full working page height is kept.
        """

        self.canvas.save()

        if content_bottom_ys is not None:
            self._crop_bottom_whitespace(content_bottom_ys=content_bottom_ys)

    def new_page(self) -> None:
        """Finalize the current page and start a fresh one.

        Resets the active font so subsequent drawing on the new page uses the
        configured default.
        """

        self.canvas.showPage()
        self._set_font()

    def _crop_bottom_whitespace(self, content_bottom_ys: list[float]) -> None:
        """Crop the empty space below the content on each page.

        Args:
            content_bottom_ys (list[float]): Vertical position of the bottom of
                the drawn content for each page, in points, ordered by page.
                Everything below each position is removed from that page.
        """

        reader = PdfReader(self.output_file_path)
        writer = PdfWriter()

        for page, content_bottom_y in zip(reader.pages, content_bottom_ys):
            page.mediabox.bottom = content_bottom_y
            writer.add_page(page)

        with open(self.output_file_path, "wb") as f:
            writer.write(f)
