"""Module for creating recipes in .pdf format optimized for mobile screen format."""

import json

from reportlab.lib.utils import ImageReader
from src.page_builder import PageBuilder
from src.config_manager import Config


class RecipePDFBuilder:
    """Specialized builder for recipe PDFs optimized for mobile screens."""

    def __init__(self, config: Config) -> None:
        """
        Initialize a RecipePDFBuilder for mobile-optimized recipe PDFs.

        Sets up page layout, margins, and loads the recipe JSON file.
        """
        self.config = config
        self.page = PageBuilder(output_file_name=self.config.io.output_file_name)
        self.recipe = self._load_json_file(
            file_path=self.config.io.input_recipe_file_path
        )

        self.y_position = self.page.page_height
        self.section_counter: int = 0
        self.max_line_width = (
            self.page.page_width
            - self.config.document_margins.left
            - self.config.document_margins.right
        )

    def _load_json_file(self, file_path: str) -> dict:
        """Load a JSON file and return its contents as a dictionary."""
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _draw_horizontal_line(self, y, color: tuple | None = None):
        """Draw a horizontal line."""
        if isinstance(color, tuple):
            self.page.canvas.setStrokeColorRGB(*color)

        self.page.canvas.line(0, y, self.page.page_width, y)

    def _draw_cover_image(self, image_path: str) -> None:
        """Draw a cover image centered on the page with a fixed height."""
        image_height = self.config.layout_cover.image_height
        image = ImageReader(image_path)
        initial_image_width, initial_image_height = image.getSize()

        image_scaling_factor = image_height / initial_image_height
        image_width = initial_image_width * image_scaling_factor
        x_image = (self.page.page_width - image_width) / 2
        y_image = self.y_position - image_height

        self.page.canvas.drawImage(
            image_path, x_image, y_image, image_width, image_height
        )

        self.y_position -= image_height
        y_section_divider = self.y_position
        self._draw_horizontal_line(y=y_section_divider)

    def _draw_text_block(
        self,
        text: str,
        font_name: str | None = None,
        font_size: int | None = None,
    ) -> None:
        """
        Draw a styled text block with background and a horizontal divider below.
        """
        font_name = font_name or self.config.font.font_name
        font_size = font_size or self.config.font.font_size
        background_color = self.config.colors.palette[
            self.section_counter % len(self.config.colors.palette)
        ]

        self.y_position = self.page.draw_text(
            x=self.config.document_margins.left,
            y=self.y_position,
            text=text,
            max_line_width=self.max_line_width,
            font_name=font_name,
            font_size=font_size,
            background_color=background_color,
            margin_top=self.config.section_margins.top,
            margin_bottom=self.config.section_margins.bottom,
            font_shift_factor=self.config.font.font_shift_factor,
        )

        self._draw_horizontal_line(y=self.y_position)
        self.section_counter += 1

    def add_section(self, section_name: str) -> None:
        """Add a recipe section by name using a dispatch table."""
        section_handlers = {
            "cover_image": lambda value: self._draw_cover_image(image_path=value),
            "title": lambda value: self._draw_text_block(
                text=value, font_size=18, font_name="Helvetica-Bold"
            ),
        }

        if section_name in ["cover_image", "title"]:
            handler = section_handlers[section_name]

        if section_name == "cover_image":
            handler(self.recipe[section_name])
        elif section_name == "title":
            handler(self.recipe[section_name])
        else:
            pass

    def build(self) -> None:
        """Render all recipe sections and save the PDF in a defined order."""
        for section_name in self.recipe.keys():
            self.add_section(section_name=section_name)

        self.page.save()
