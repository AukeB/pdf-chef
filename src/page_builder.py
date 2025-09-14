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
        page_height: float = 160 * mm,
        font_name: str = "Helvetica",
        font_size: int = 16,
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

    def draw_text(
        self,
        x: float,
        y: float,
        text: str,
        font_name: str | None = None,
        font_size: int | None = None,
    ) -> None:
        """
        Draw text at a given position.

        Args:
            x (float): X coordinate in points.
            y (float): Y coordinate in points.
            text (str): Text to draw.
            font_name (str | None): Optional font override.
            font_size (int | None): Optional font size override.
        """
        if font_name or font_size:
            self.canvas.setFont(
                font_name or self.font_name, font_size or self.font_size
            )

        self.canvas.drawString(x, y, text)

    def draw_text_wrapped(
        self,
        x: float,
        y: float,
        text: str,
        max_width: float,
        font_name: str | None = None,
        font_size: int | None = None,
        line_spacing: float | None = None,
    ) -> float:
        """
        Draw text at a given position with word wrapping if it exceeds max_width.

        Args:
            x (float): X coordinate in points.
            y (float): Y coordinate in points (top of text).
            text (str): Text to draw.
            max_width (float): Maximum width in points before wrapping.
            font_name (str | None): Optional font override.
            font_size (int | None): Optional font size override.
            line_spacing (float | None): Optional line spacing override.

        Returns:
            float: The new Y position after drawing the wrapped text.
        """
        font_name = font_name or self.font_name
        font_size = font_size or self.font_size
        spacing = line_spacing or (font_size * 1.2)

        self.canvas.setFont(font_name, font_size)

        words = text.split()
        current_line = ""
        y_current = y

        for word in words:
            test_line = f"{current_line} {word}".strip()
            test_width = self.canvas.stringWidth(test_line, font_name, font_size)

            if test_width <= max_width:
                current_line = test_line
            else:
                self.canvas.drawString(x, y_current, current_line)
                y_current -= spacing
                current_line = word

        if current_line:
            self.canvas.drawString(x, y_current, current_line)
            y_current -= spacing

        return y_current

    def save(self) -> None:
        """Finalize and save the PDF file."""
        self.canvas.save()
