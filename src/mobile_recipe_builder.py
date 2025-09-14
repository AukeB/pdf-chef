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
        image_height: int = 150,
    ) -> None:
        """
        Initialize a RecipePDFBuilder for mobile-optimized recipe PDFs.

        Sets up page layout, margins, and loads the recipe JSON file.

        Args:
            output_file_name (str): Name of the PDF file to create.
            recipe_file_path (str): Path to the JSON file with recipe data.
            top_margin (int): Space in points at the top of each page.
            bottom_margin (int): Space in points at the bottom of each page.
            left_margin (int): Space in points on the left side of the page.
            right_margin (int): Space in points on the right side of the page.
            image_height (int): Fixed height for cover images in points.
        """
        self.page = PageBuilder(output_file_name=output_file_name)
        self.recipe_file_path = recipe_file_path
        self.recipe = self._load_json_file(file_path=self.recipe_file_path)

        self.left_margin = left_margin
        self.right_margin = right_margin
        self.section_spacing = section_spacing
        self.spacing_font_correction_factor = spacing_font_correction_factor
        self.max_text_width = (
            self.page.page_width - self.left_margin - self.right_margin
        )

        self.y_current = self.page.page_height

        self.image_height = image_height

    def _load_json_file(self, file_path: str) -> dict:
        """Load a JSON file and return its contents as a dictionary.

        Args:
            file_path (str): Path to the JSON file.

        Returns:
            dict: The parsed JSON content, or an empty dict if file not found.
        """
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return data

    def add_section(self, section_name: str) -> None:
        """
        Add a recipe section by name.

        Args:
            section_name (str): Section type (e.g., "title", "ingredients").
        """
        if section_name == "cover_image":
            self._draw_cover_image(image_path=self.recipe[section_name])

        elif section_name == "title":
            self._draw_text(
                text=self.recipe[section_name],
                font_size=18,
                background_color=(0.87, 0.72, 0.53),
                font_name="Helvetica-Bold",
            )

        elif section_name == "description":
            self._draw_text(
                text=self.recipe[section_name],
                font_size=12,
                background_color=(0.87, 0.85, 0.55),
            )

        elif section_name == "ingredients":
            self._draw_list(
                items=self.recipe[section_name],
                background_color=(0.87, 0.72, 0.53),
            )

        elif section_name == "instructions":
            self.draw_instructions(instructions=self.recipe[section_name])

    def _draw_cover_image(self, image_path: str) -> None:
        """
        Draw a cover image centered on the page with a fixed height.

        Args:
            image_path (str): Path to the image file.
        """
        image = ImageReader(image_path)
        img_width, img_height = image.getSize()

        scale = self.image_height / img_height
        scaled_width = img_width * scale

        x_centered = (self.page.page_width - scaled_width) / 2

        self.page.canvas.drawImage(
            image_path,
            x_centered,
            self.y_current - self.image_height,
            width=scaled_width,
            height=self.image_height,
        )

        self.y_current -= self.image_height
        line_height = self.y_current + 0.52 * self.section_spacing
        self.page.canvas.line(0, line_height, self.page.page_width, line_height)

    def _measure_text_height(
        self,
        text: str,
        font_size: int,
        max_width: float,
        font_name: str | None = None,
        line_spacing_factor: float = 1.2,
    ) -> float:
        """Return the height in points that the text will occupy when wrapped."""
        font_name = font_name or self.page.font_name
        font_size = font_size or self.page.font_size
        spacing = font_size * line_spacing_factor

        words = text.split()
        current_line = ""
        lines_count = 0

        for word in words:
            test_line = f"{current_line} {word}".strip()
            test_width = self.page.canvas.stringWidth(test_line, font_name, font_size)
            if test_width <= max_width:
                current_line = test_line
            else:
                lines_count += 1
                current_line = word
        if current_line:
            lines_count += 1

        return lines_count * spacing

    def _draw_text(
        self,
        text: str,
        font_size: int,
        background_color: tuple,
        font_name: str | None = None,
    ) -> None:
        """
        Draw a title in the document

        Args:
            title (str): The text to draw on the screen
        """
        spacing_font_correction = self.spacing_font_correction_factor * font_size
        height = self._measure_text_height(
            text, font_size, self.max_text_width, font_name
        )

        self.page.canvas.setFillColorRGB(*background_color)
        self.page.canvas.rect(
            0,
            self.y_current
            - height
            - spacing_font_correction
            - 0.5 * self.section_spacing,
            self.page.page_width,
            height + spacing_font_correction + self.section_spacing,
            stroke=0,
            fill=1,
        )
        self.page.canvas.setFillColorRGB(0, 0, 0)

        self.y_current = self.page.draw_text_wrapped(
            x=self.left_margin,
            y=self.y_current - spacing_font_correction,
            text=text,
            max_width=self.max_text_width,
            font_name=font_name,
            font_size=font_size,
        )

        self.page.canvas.line(
            0,
            self.y_current - 0.5 * self.section_spacing,
            self.page.page_width,
            self.y_current - 0.5 * self.section_spacing,
        )
        self.y_current -= self.section_spacing

    def _draw_list(
        self,
        items: list[str],
        background_color: tuple,
        font_size: int = 14,
        bullet: str = "- ",
        bullet_spacing_factor: float = 0.2,
    ) -> None:
        """
        Draw a vertical list of items (e.g., ingredients) on the PDF page with an optional background.

        Each item is prefixed with a bullet and wrapped to fit the page width.
        Updates the current vertical position (`y_current`) after drawing.

        Args:
            items (list[str]): List of strings to render as a vertical list.
            font_size (int): Font size for the list items.
            bullet (str): String to prepend to each item.
            bullet_spacing_factor (float): Extra spacing after each item relative to font size.
            background_color (tuple | None): Optional RGB background color.
        """
        total_height = 0
        spacing_font_correction = self.spacing_font_correction_factor * font_size

        for item in items:
            text = f"{bullet}{item}"
            total_height += self._measure_text_height(
                text, font_size, self.max_text_width
            )
            total_height += font_size * bullet_spacing_factor

        total_height += spacing_font_correction + self.section_spacing

        if background_color:
            self.page.canvas.setFillColorRGB(*background_color)
            self.page.canvas.rect(
                0,
                self.y_current - total_height + 0.5 * self.section_spacing,
                self.page.page_width,
                total_height,
                stroke=0,
                fill=1,
            )
            self.page.canvas.setFillColorRGB(0, 0, 0)  # reset text color

        # Adjust y_current for spacing
        self.y_current -= spacing_font_correction

        # Draw each list item
        for item in items:
            text = f"{bullet}{item}"

            self.y_current = self.page.draw_text_wrapped(
                x=self.left_margin,
                y=self.y_current,
                text=text,
                max_width=self.max_text_width,
                font_size=font_size,
            )

            self.y_current -= font_size * bullet_spacing_factor

        # Draw line after the list
        self.page.canvas.line(
            0,
            self.y_current - 0.5 * self.section_spacing,
            self.page.page_width,
            self.y_current - 0.5 * self.section_spacing,
        )
        self.y_current -= self.section_spacing

    def draw_instructions(self, instructions: list[dict], font_size: int = 12) -> None:
        """
        Draw recipe instructions on the PDF canvas.

        Each section is rendered as an italicized title with its section number,
        followed by numbered steps in the format "section_number.step_number".

        Args:
            instructions (list[dict]): List of instruction sections, each with
                "section_number", "section", and "steps".
            font_size (int): Base font size for the text.
        """
        self.y_current -= self.spacing_font_correction_factor * font_size

        for section in instructions:
            section_number = section["section_number"]
            section_title = section["section"]

            self.y_current = self.page.draw_text_wrapped(
                x=self.left_margin,
                y=self.y_current,
                text=f"{section_number}. {section_title}",
                max_width=self.max_text_width,
                font_size=font_size,
            )

            self.y_current -= font_size * 0.5  # small gap after section title

            for step in section["steps"]:
                step_number = step["step_number"]
                step_text = step["text"]

                numbered_text = f"{section_number}.{step_number} {step_text}"
                self.y_current = self.page.draw_text_wrapped(
                    x=self.left_margin,
                    y=self.y_current,
                    text=numbered_text,
                    max_width=self.max_text_width,
                    font_size=font_size,
                )

                self.y_current -= font_size * 0.4

            self.y_current -= font_size * 0.4

        self.page.canvas.line(0, self.y_current, self.page.page_width, self.y_current)
        self.y_current -= self.section_spacing
        self.page.canvas.line(0, self.y_current, self.page.page_width, self.y_current)

    def build(self) -> None:
        """
        Render all recipe sections and save the PDF.

        Iterates over the recipe dictionary, adds each section to the PDF,
        and finalizes the document.
        """
        for recipe_section, _ in self.recipe.items():
            self.add_section(section_name=recipe_section)

        self.page.save()
