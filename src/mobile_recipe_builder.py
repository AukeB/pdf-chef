"""Module for creating recipes in .pdf format optimized for mobile screen format."""

import json

from src.page_builder import PageBuilder


class RecipePDFBuilder:
    """Specialized builder for recipe PDFs optimized for mobile screens."""

    def __init__(
        self,
        output_file_name: str = "recipes.pdf",
        recipe_file_path: str = "recipes/pompoen_risotto.json",
        top_margin: int = 20,
        bottom_margin: int = 20,
        line_spacing: int = 15,
    ) -> None:
        """Initialize a RecipePDFBuilder for mobile-optimized recipe PDFs.

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
        self.line_spacing = line_spacing
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
        if name == "title":
            self._draw_title(kwargs["text"])
        # elif name == "description":
        #     self._draw_paragraph(kwargs["text"])
        # elif name == "stats":
        #     self._draw_stats(kwargs["stats"])
        # elif name == "ingredients":
        #     self._draw_list(kwargs["items"], title="Ingredients")
        # elif name == "instructions":
        #     self._draw_list(kwargs["steps"], title="Instructions")

    def _draw_title(self, text: str) -> None:
        self._check_space(40)
        self.page.draw_text(
            20, self.y_current, text, font_name="Helvetica-Bold", font_size=18
        )
        self.y_current -= 40

    # def _draw_paragraph(self, text: str) -> None:
    #     # Rough estimate: each line ~15 pts
    #     lines = text.split("\n")
    #     required_height = len(lines) * self.line_spacing
    #     self._check_space(required_height)
    #     for line in lines:
    #         self.page.draw_text(20, self.y_current, line)
    #         self.y_current -= self.line_spacing
    #     self.y_current -= self.line_spacing  # extra space after paragraph

    # def _draw_stats(self, stats: dict) -> None:
    #     line = " | ".join([f"{k}: {v}" for k, v in stats.items()])
    #     self._check_space(20)
    #     self.page.draw_text(20, self.y_current, line)
    #     self.y_current -= 30

    # def _draw_list(self, items: list, title: str) -> None:
    #     self._check_space(20 + len(items) * self.line_spacing)
    #     self.page.draw_text(
    #         20, self.y_current, title, font_name="Helvetica-Bold", font_size=14
    #     )
    #     self.y_current -= 20
    #     for item in items:
    #         self.page.draw_text(30, self.y_current, f"- {item}")
    #         self.y_current -= self.line_spacing
    #     self.y_current -= self.line_spacing

    def save(self) -> None:
        """Finalize and save the recipe PDF."""
        self.page.save()

    def build(self) -> None:
        """ """

        for recipe_section, text in self.recipe.items():
            print(recipe_section, text)
