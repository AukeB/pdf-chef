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
        top_margin: int = 20,
        bottom_margin: int = 20,
        side_margin: int = 20,
    ) -> None:
        """
        Initialize a RecipePDFBuilder for mobile-optimized recipe PDFs.

        Args:
            output_file_name (str): Name of the PDF file to create.
            top_margin (int): Space in points to leave at the top of each page.
            bottom_margin (int): Space in points to leave at the bottom of each page.
            line_spacing (int): Vertical space in points between lines of text.
        """
        self.page = PageBuilder(output_file_name=output_file_name)
        self.recipe_file_path = recipe_file_path
        self.recipe = self._load_json_file(file_path=self.recipe_file_path)

        self.top_margin = top_margin
        self.bottom_margin = bottom_margin
        self.side_margin = side_margin
        self.max_text_width = self.page.page_width - 2 * self.side_margin
        self.y_current = self.page.page_height - self.top_margin

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

    def _check_space(self, required_height: float) -> None:
        """Check if the section fits on the current page; start new page if not."""
        if self.y_current - required_height < self.bottom_margin:
            self.page.canvas.showPage()
            self.y_current = self.page.page_height - self.top_margin
            self.page._set_font()

    def add_section(self, name: str, **kwargs) -> None:
        """
        Add a recipe section by name.

        Args:
            name (str): Section type (e.g., "title", "ingredients").
            **kwargs: Content depending on section type.
        """
        if name == "cover_image":
            self._draw_cover_image(self.recipe[name])
        elif name == "title":
            self._draw_title(self.recipe[name])
        elif name == "ingredients":
            self._draw_list(self.recipe[name])

    def _draw_cover_image(self, image_path: str, fixed_height: float = 80) -> None:
        """
        Draw a cover image centered on the page with a fixed height.

        Args:
            image_path (str): Path to the image file.
            fixed_height (float): Height of the image in points.
        """
        image = ImageReader(image_path)
        img_width, img_height = image.getSize()

        scale = fixed_height / img_height
        scaled_width = img_width * scale
        scaled_height = fixed_height

        x_centered = max(0, (self.page.page_width - scaled_width) / 2)

        self.page.canvas.drawImage(
            image_path,
            x_centered,
            self.y_current - scaled_height,
            width=scaled_width,
            height=scaled_height,
            preserveAspectRatio=True,
            mask="auto",
        )

        self.y_current -= scaled_height

    def _draw_title(self, text: str) -> None:
        self.y_current = self.page.draw_text_wrapped(
            x=self.side_margin,
            y=self.y_current,
            text=text,
            max_width=self.max_text_width,
            font_name="Helvetica-Bold",
            font_size=18,
        )

    def _draw_list(
        self,
        items: list[str],
        font_size: int = 14,
        bullet: str = "- ",
        bullet_spacing_factor: float = 0.2,
    ) -> None:
        """Draw a list of items (e.g., ingredients) on the PDF page.

        Args:
            items (list[str]): List of strings to render as a vertical list.
        """
        for item in items:
            text = f"{bullet}{item}"

            self.y_current = self.page.draw_text_wrapped(
                x=self.side_margin,
                y=self.y_current,
                text=text,
                max_width=self.max_text_width,
                font_size=font_size,
            )

            self.y_current -= font_size * bullet_spacing_factor

    def build(self) -> None:
        """ """
        for recipe_section, _ in self.recipe.items():
            self.add_section(name=recipe_section)

        self.page.save()
