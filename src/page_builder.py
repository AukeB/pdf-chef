"""Module for creating documents using the reportlab package"""

import os

from pathlib import Path
from typing import Tuple
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm

from src.config_manager import Config


class PageBuilder:
    """Utility class for building simple PDFs with custom page sizes using ReportLab"""

    def __init__(self, config: Config) -> None:
        """
        Initialize a PageBuilder instance.
        """
        # Variables
        self.config = config
        self.output_file_path = self.config.io.output_file_path
        self.max_line_width = (
            self.config.page.width * mm
            - self.config.document_margins.left
            - self.config.document_margins.right
        )

        # Actions
        self._create_output_directory()
        self.canvas = self._initialize_document()
        self._set_font()

    def _create_output_directory(self) -> None:
        """
        Create the output directory if it does not exist.

        Args:
            directory_path (str): Path of the directory to create.
        """
        output_directory_path = Path(self.output_file_path).parent
        os.makedirs(output_directory_path, exist_ok=True)

    def _initialize_document(
        self,
    ) -> canvas.Canvas:
        """
        Initialize a ReportLab canvas with the configured page size.

        Returns:
            canvas.Canvas: A ReportLab canvas object.
        """
        page_size = (self.config.page.width * mm, self.config.page.height * mm)
        return canvas.Canvas(self.output_file_path, pagesize=page_size)

    def _set_font(
        self, font_name: str | None = None, font_size: int | None = None
    ) -> None:
        """Set the default font for the canvas."""
        font_name = font_name or self.config.font.font_name
        font_size = font_size or self.config.font.font_size

        self.canvas.setFont(font_name, font_size)

    def _measure_text_block(
        self,
        text: str,
        font_name: str | None = None,
        font_size: int | None = None,
    ) -> tuple[list[str], float]:
        """
        Measure how the text will wrap and its total height.

        Args:
            text (str): Text to measure.
            font_name (str | None): Optional font override.
            font_size (int | None): Optional font size override.

        Returns:
            tuple[list[str], float]:
                - Wrapped lines of text
                - Total text height (in points)
        """
        font_name = font_name or self.config.font.font_name
        font_size = font_size or self.config.font.font_size

        line_height = font_size * self.config.font.line_height_factor

        self.canvas.setFont(font_name, font_size)

        words = text.split()
        current_line = ""
        lines = []

        for word in words:
            line = f"{current_line} {word}".strip()
            line_width = self.canvas.stringWidth(line, font_name, font_size)

            if line_width <= self.max_line_width:
                current_line = line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        text_height = len(lines) * line_height

        return lines, text_height

    def draw_text(
        self,
        text: str,
        x: float,
        y: float,
        background_color: Tuple[float, float, float],
        max_line_width: float | None = None,
        font_name: str | None = None,
        font_size: int | None = None,
        line_height_factor: float | None = None,
        margin_top: float | None = None,
        margin_bottom: float | None = None,
        font_shift_factor: float | None = None,
    ) -> float:
        """
        Draw text at a given position with word wrapping and optional background.
        """
        max_line_width = max_line_width or self.max_line_width
        font_name = font_name or self.config.font.font_name
        font_size = font_size or self.config.font.font_size
        line_height_factor = line_height_factor or self.config.font.line_height_factor
        margin_top = margin_top or self.config.section_margins.top
        margin_bottom = margin_bottom or self.config.section_margins.bottom
        font_shift_factor = font_shift_factor or self.config.font.font_shift_factor

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

        return y - block_height

    def draw_horizontal_line(
        self, y: float, line_color: Tuple[float, float, float] | None = None
    ) -> None:
        line_color = line_color or self.config.colors.line_color

        self.canvas.setStrokeColorRGB(*line_color)
        self.canvas.line(0, y, self.config.page.width * mm, y)

    def save(self) -> None:
        """Finalize and save the PDF file."""
        self.canvas.save()
