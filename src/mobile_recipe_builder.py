"""Module for creating recipes in .pdf format optimized for mobile screen format."""

import json

from reportlab.lib.utils import ImageReader
from src.page_builder import PageBuilder


class RecipePDFBuilder:
    """Specialized builder for recipe PDFs optimized for mobile screens."""

    def __init__(
        self,
        output_file_name: str = "recipes.pdf",
        recipe_file_path: str = "recipes/pompoen_risotto.json",
        left_margin: int = 20,
        right_margin: int = 20,
        section_spacing: int = 20,
        spacing_font_correction_factor: float = 1.8,
        cover_image_offset_factor: float = 0.52,
        image_height: int = 150,
    ) -> None:
        """
        Initialize a RecipePDFBuilder for mobile-optimized recipe PDFs.

        Sets up page layout, margins, and loads the recipe JSON file.
        """
        self.page = PageBuilder(output_file_name=output_file_name)
        self.recipe_file_path = recipe_file_path
        self.recipe = self._load_json_file(file_path=self.recipe_file_path)

        self.left_margin = left_margin
        self.right_margin = right_margin
        self.section_spacing = section_spacing
        self.section_padding_top = 0.5 * self.section_spacing
        self.section_padding_bottom = 0.5 * self.section_spacing
        self.spacing_font_correction_factor = spacing_font_correction_factor
        self.max_line_width = (
            self.page.page_width - self.left_margin - self.right_margin
        )

        self.y_position = self.page.page_height
        self.cover_image_offset_factor = cover_image_offset_factor
        self.cover_image_offset = self.cover_image_offset_factor * self.section_spacing
        self.image_height = image_height

        self.section_counter: int = 0
        self.background_colors: list[tuple[float, float, float]] = [
            (0.87, 0.85, 0.55),
            (0.87, 0.72, 0.53)
        ]

    def _load_json_file(self, file_path: str) -> dict:
        """Load a JSON file and return its contents as a dictionary."""
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _draw_horizontal_line(self, y, color: tuple | None = None):
        """Draw a horizontal line."""
        if isinstance(color, tuple):
            self.page.canvas.setStrokeColorRGB(*color)
        self.page.canvas.line(0, y, self.page.page_width, y)
        if isinstance(color, tuple):
            self.page.canvas.setStrokeColorRGB(0, 0, 0)

    def _draw_cover_image(self, image_path: str) -> None:
        """Draw a cover image centered on the page with a fixed height."""
        image = ImageReader(image_path)
        image_width, image_height = image.getSize()

        image_scaling_factor = self.image_height / image_height
        image_width = image_width * image_scaling_factor
        x_image = (self.page.page_width - image_width) / 2
        y_image = self.y_position - self.image_height

        self.page.canvas.drawImage(
            image_path, x_image, y_image, image_width, self.image_height
        )

        self.y_position -= self.image_height
        y_section_divider = self.y_position
        self._draw_horizontal_line(y=y_section_divider)
        self.y_position -= self.cover_image_offset

    def add_section(self, section_name: str) -> None:
        """Add a recipe section by name."""
        text = self.recipe[section_name]

        if section_name == "cover_image":
            self._draw_cover_image(image_path=self.recipe[section_name])

        elif section_name == "title":
            # Drawing multiple times for testing purposes.
            self._draw_text_block(text=text, font_size=18, font_name="Helvetica-Bold")
            self._draw_text_block(text=text, font_size=4, font_name="Helvetica-Bold")
            self._draw_text_block(text=text, font_size=12, font_name="Helvetica-Bold")

    def _draw_text_block(
        self,
        text: str,
        font_size: int,
        font_name: str | None = None,
    ) -> None:
        """
        Draw a styled text block with background and a horizontal divider below.
        """
        background_color = self.background_colors[self.section_counter % 2]

        self.y_position = self.page.draw_text(
            x=self.left_margin,
            y=self.y_position,
            text=text,
            max_line_width=self.max_line_width,
            section_counter=self.section_counter,
            font_name=font_name,
            font_size=font_size,
            background_color=background_color,
            padding_top=self.section_padding_top,
            padding_bottom=self.section_padding_bottom,
            spacing_font_correction_factor=self.spacing_font_correction_factor,
            offset_top=self.cover_image_offset,
        )

        self._draw_horizontal_line(y=self.y_position)
        self.section_counter += 1

    def build(self) -> None:
        """Render all recipe sections and save the PDF."""
        for section_name in self.recipe.keys():
            self.add_section(section_name)
        self.page.save()
