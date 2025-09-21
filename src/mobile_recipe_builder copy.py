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
        self.spacing_font_correction_factor = spacing_font_correction_factor
        self.max_line_width = (
            self.page.page_width - self.left_margin - self.right_margin
        )

        self.y_position = self.page.page_height
        self.cover_image_offset_factor = cover_image_offset_factor
        self.image_height = image_height

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
        self.y_position -= self.cover_image_offset_factor * self.section_spacing

    def add_section(self, section_name: str) -> None:
        """Add a recipe section by name."""
        text = self.recipe[section_name]

        if section_name == "cover_image":
            self._draw_cover_image(image_path=self.recipe[section_name])

        elif section_name == "title":
            self._draw_text(text=text, font_size=18, font_name="Helvetica-Bold")
            self._draw_text(text=text, font_size=4, font_name="Helvetica-Bold")
            self._draw_text(text=text, font_size=12, font_name="Helvetica-Bold")

        # elif section_name == "description":
        #     self._draw_text(
        #         text=self.recipe[section_name],
        #         font_size=12,
        #         background_color=(0.87, 0.85, 0.55),
        #     )

        # elif section_name == "ingredients":
        #     self._draw_list(
        #         items=self.recipe[section_name],
        #         background_color=(0.87, 0.72, 0.53),
        #     )

        # elif section_name == "instructions":
        #     self.draw_instructions(instructions=self.recipe[section_name])

    def _draw_background(
        self,
        y: float,
        text_height: float,
    ) -> None:
        """Draw a background"""
        self.page.canvas.setFillColorRGB(0.87, 0.85, 0.55)

        self.page.canvas.rect(
            x=0,
            y=y,
            width=self.page.page_width,
            height=text_height,
            stroke=0,
            fill=1
        )

        self.page.canvas.setFillColorRGB(0, 0, 0)


    def _draw_text(
        self,
        text: str,
        font_size: int,
        font_name: str | None = None,
    ) -> None:
        """ """
        self.y_position -= 0.5 * self.section_spacing
        spacing_font_correction = self.spacing_font_correction_factor * font_size   
        self.y_position -= spacing_font_correction

        height = self.page.draw_text(
            x=self.left_margin,
            y=self.y_position,
            text=text,
            max_line_width=self.max_line_width,
            font_name=font_name,
            font_size=font_size,
            measure_only=True
        )

        y_background = self.y_position - height - 0.5 * self.section_spacing
        background_height = height + self.section_spacing + spacing_font_correction
        
        self._draw_background(y=y_background, text_height=background_height)

        self.y_position = self.page.draw_text(
            x=self.left_margin,
            y=self.y_position,
            text=text,
            max_line_width=self.max_line_width,
            font_name=font_name,
            font_size=font_size,
        )

        self.y_position -= 0.5 * self.section_spacing
        self._draw_horizontal_line(y=self.y_position)

    def _draw_text_old(
        self,
        text: str,
        font_size: int,
        background_color: tuple,
        font_name: str | None = None,
    ) -> None:
        """Draw a text block with background and spacing."""
        spacing_font_correction = self.spacing_font_correction_factor * font_size

        # Measure height using measure_only=True
        section_height = self.page.draw_text(
            x=self.left_margin,
            y=self.y_position,
            text=text,
            max_line_width=self.max_line_width,
            font_name=font_name,
            font_size=font_size,
            measure_only=True,
        )
        
        #self._draw_horizontal_line(y=)
        self.page.canvas.line(
            0,
            self.y_position - 0.5 * self.section_spacing,
            self.page.page_width,
            self.y_position - 0.5 * self.section_spacing,
        )

        y_section = self.y_position - section_height

        # Background rectangle
        #self.page.canvas.setFillColorRGB(*background_color)
        # self.page.canvas.rect(
        #     0,
        #     self.y_position
        #     - height
        #     - spacing_font_correction
        #     - 0.5 * self.section_spacing,
        #     self.page.page_width,
        #     height + spacing_font_correction + self.section_spacing,
        #     stroke=0,
        #     fill=1,
        # )
        #self.page.canvas.setFillColorRGB(0, 0, 0)

        # Draw text for real
        self.y_position = self.page.draw_text(
            x=self.left_margin,
            y=self.y_position - spacing_font_correction,
            text=text,
            max_line_width=self.max_line_width,
            font_name=font_name,
            font_size=font_size,
        )

        # Separator line
        self.page.canvas.line(
            0,
            self.y_position - 0.5 * self.section_spacing,
            self.page.page_width,
            self.y_position - 0.5 * self.section_spacing,
        )
        self.y_position -= self.section_spacing

    def _draw_list(
        self,
        items: list[str],
        background_color: tuple,
        font_size: int = 14,
        bullet: str = "- ",
        bullet_spacing_factor: float = 0.2,
    ) -> None:
        """Draw a vertical list of items with optional background."""
        spacing_font_correction = self.spacing_font_correction_factor * font_size
        total_height = spacing_font_correction + self.section_spacing

        # Measure height of all items
        for item in items:
            text = f"{bullet}{item}"
            end_y = self.page.draw_text(
                x=self.left_margin,
                y=self.y_position,
                text=text,
                max_line_width=self.max_line_width,
                font_size=font_size,
                measure_only=True,
            )
            total_height += (
                self.y_position - end_y
            ) + font_size * bullet_spacing_factor

        # Background rectangle
        if background_color:
            self.page.canvas.setFillColorRGB(*background_color)
            self.page.canvas.rect(
                0,
                self.y_position - total_height + 0.5 * self.section_spacing,
                self.page.page_width,
                total_height,
                stroke=0,
                fill=1,
            )
            self.page.canvas.setFillColorRGB(0, 0, 0)

        # Draw items
        self.y_position -= spacing_font_correction
        for item in items:
            text = f"{bullet}{item}"
            self.y_position = self.page.draw_text(
                x=self.left_margin,
                y=self.y_position,
                text=text,
                max_line_width=self.max_line_width,
                font_size=font_size,
            )
            self.y_position -= font_size * bullet_spacing_factor

        # Separator line
        self.page.canvas.line(
            0,
            self.y_position - 0.5 * self.section_spacing,
            self.page.page_width,
            self.y_position - 0.5 * self.section_spacing,
        )
        self.y_position -= self.section_spacing

    def draw_instructions(self, instructions: list[dict], font_size: int = 12) -> None:
        """Draw recipe instructions with numbered sections and steps."""
        self.y_position -= self.spacing_font_correction_factor * font_size

        for section in instructions:
            section_number = section["section_number"]
            section_title = section["section"]

            self.y_position = self.page.draw_text(
                x=self.left_margin,
                y=self.y_position,
                text=f"{section_number}. {section_title}",
                max_line_width=self.max_line_width,
                font_size=font_size,
            )
            self.y_position -= font_size * 0.5

            for step in section["steps"]:
                step_number = step["step_number"]
                step_text = step["text"]

                numbered_text = f"{section_number}.{step_number} {step_text}"
                self.y_position = self.page.draw_text(
                    x=self.left_margin,
                    y=self.y_position,
                    text=numbered_text,
                    max_line_width=self.max_line_width,
                    font_size=font_size,
                )
                self.y_position -= font_size * 0.4

            self.y_position -= font_size * 0.4

        self.page.canvas.line(0, self.y_position, self.page.page_width, self.y_position)
        self.y_position -= self.section_spacing
        self.page.canvas.line(0, self.y_position, self.page.page_width, self.y_position)

    def build(self) -> None:
        """Render all recipe sections and save the PDF."""
        for section_name in self.recipe.keys():
            self.add_section(section_name)
        self.page.save()
