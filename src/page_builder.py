"""Module for creating documents using the reportlab package"""

import os

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas


class PageBuilder:
    """Utility class for building simple PDFs with custom page sizes using ReportLab"""

    def __init__(
        self,
        output_directory_path: str = "pdfs",
        output_file_name: str = "document.pdf",
        page_width: float = 90 * mm,
        page_height: float = 1000 * mm,
        font_name: str = "Helvetica",
        font_size: int = 16,
        line_spacing_factor: float = 1.2,
    ) -> None:
        """
        Initialize a PageBuilder instance.

        Args:
            output_directory_path (str): Directory where the PDF will be saved.
            output_file_name (str): Name of the PDF file.
            page_width (float): Width of the page in points.
            page_height (float): Height of the page in points.
            font_name (str): Default font name.
            font_size (int): Default font size.
        """
        # Paths
        self.output_directory_path = output_directory_path
        self.output_file_name = output_file_name
        self.output_file_path = os.path.join(
            self.output_directory_path, self.output_file_name
        )
        self._create_directory(directory_path=self.output_directory_path)

        # Page settings
        self.page_width = page_width
        self.page_height = page_height
        self.page_size = (self.page_width, self.page_height)

        # Font settings
        self.font_name = font_name
        self.font_size = font_size

        # Canvas
        self.line_spacing_factor = line_spacing_factor
        self.canvas = self._initialize_document()
        self._set_font()

    def _create_directory(self, directory_path: str) -> None:
        """
        Create the output directory if it does not exist.

        Args:
            directory_path (str): Path of the directory to create.
        """
        os.makedirs(directory_path, exist_ok=True)

    def _initialize_document(
        self,
    ) -> canvas.Canvas:
        """
        Initialize a ReportLab canvas with the configured page size.

        Returns:
            canvas.Canvas: A ReportLab canvas object.
        """
        return canvas.Canvas(self.output_file_path, pagesize=self.page_size)

    def _set_font(self) -> None:
        """Set the default font for the canvas."""
        self.canvas.setFont(self.font_name, self.font_size)


    def _measure_text_block(
        self,
        text: str,
        max_line_width: float,
        font_name: str | None = None,
        font_size: int | None = None,
    ) -> tuple[list[str], float]:
        """
        Measure how the text will wrap and its total height.

        Args:
            text (str): Text to measure.
            max_line_width (float): Max width before wrapping.
            font_name (str | None): Optional font override.
            font_size (int | None): Optional font size override.

        Returns:
            tuple[list[str], float]: 
                - Wrapped lines of text
                - Total text height (in points)
        """
        font_name = font_name or self.font_name
        font_size = font_size or self.font_size
        line_spacing = font_size * self.line_spacing_factor

        self.canvas.setFont(font_name, font_size)

        words = text.split()
        current_line = ""
        lines = []

        for word in words:
            line = f"{current_line} {word}".strip()
            line_width = self.canvas.stringWidth(line, font_name, font_size)

            if line_width <= max_line_width:
                current_line = line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        text_height = len(lines) * line_spacing
        return lines, text_height


    def draw_text(
        self,
        x: float,
        y: float,
        text: str,
        max_line_width: float,
        section_counter: int,
        font_name: str | None = None,
        font_size: int | None = None,
        background_color: tuple | None = None,
        padding_top: float = 0,
        padding_bottom: float = 0,
        spacing_font_correction_factor: float = 0,
        offset_top: float | None = None
    ) -> float:
        """
        Draw text at a given position with word wrapping and optional background.
        """
        font_name = font_name or self.font_name
        font_size = font_size or self.font_size
        line_spacing = font_size * self.line_spacing_factor

        self.canvas.setFont(font_name, font_size)

        font_spacing_correction = spacing_font_correction_factor * font_size
        y_position = y - font_spacing_correction

        lines, text_height = self._measure_text_block(
            text=text,
            max_line_width=max_line_width,
            font_name=font_name,
            font_size=font_size,
        )

        block_height = text_height + padding_top + padding_bottom + font_spacing_correction
        y_block = y_position - padding_top - text_height - padding_bottom

        if offset_top and section_counter == 0:
            block_height += offset_top

        if background_color:
            self.canvas.setFillColorRGB(*background_color)
            self.canvas.rect(
                x=0,
                y=y_block,
                width=self.page_width,
                height=block_height,
                stroke=0,
                fill=1,
            )
            self.canvas.setFillColorRGB(0, 0, 0)

        y_draw = y_position - padding_top
        for line in lines:
            self.canvas.drawString(x, y_draw, line)
            y_draw -= line_spacing
        
        if offset_top and section_counter == 0:
            block_height -= offset_top

        return y - block_height

    def save(self) -> None:
        """Finalize and save the PDF file."""
        self.canvas.save()
