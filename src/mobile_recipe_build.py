"""Module for creating recipes in .pdf format optimized for mobile screen format."""

import json

from reportlab.lib.units import mm

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
        self.page = PageBuilder(config=self.config)
        self.y_position = self.config.page.height * mm
        self.section_counter: int = 0
        self.recipe = self._load_json_file(
            file_path=self.config.io.input_recipe_file_path
        )

    def _load_json_file(self, file_path: str) -> dict:
        """Load a JSON file and return its contents as a dictionary."""
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _draw_cover_image(self, image_path: str) -> None:
        """ """
        self.y_position = self.page.draw_image(
            image_path=image_path, y_pos=self.y_position
        )

    def _draw_text_block(
        self,
        text: str,
        font_name: str | None = None,
        font_size: int | None = None,
    ) -> None:
        """
        Draw a styled text block with background and a horizontal divider below.
        """
        background_color = self.config.colors.background_color_palette[
            self.section_counter % len(self.config.colors.background_color_palette)
        ]

        self.y_position = self.page.draw_text_block(
            text=text,
            x=self.config.document_margins.left,
            y=self.y_position,
            background_color=background_color,
            font_name=font_name,
            font_size=font_size,
        )

        self.section_counter += 1

    def add_section(self, section_name: str) -> None:
        """Add a recipe section by name using a dispatch table."""
        section_handlers = {
            "cover_image": lambda value: self._draw_cover_image(image_path=value),
            "title": lambda value: self._draw_text_block(
                text=value, font_size=18, font_name="Helvetica-Bold"
            ),
            "description": lambda value: self._draw_text_block(text=value),
        }

        if section_name in ["cover_image", "title", "description"]:
            handler = section_handlers[section_name]
            handler(self.recipe[section_name])

    def build(self) -> None:
        """Render all recipe sections and save the PDF in a defined order."""
        for section_name in self.recipe.keys():
            self.add_section(section_name=section_name)

        self.page.save()
