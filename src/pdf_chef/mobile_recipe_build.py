"""Module for creating recipes in .pdf format optimized for mobile screen
format.
"""

from pathlib import Path

from pdf_chef.page_builder import PageBuilder
from pdf_chef.config_manager import Config
from pdf_chef.recipe_renderer import RecipeRenderer
from pdf_chef.utils.utils_file_system import load_json_file


class RecipePDFBuilder:
    """Build recipe PDFs optimized for mobile screens.

    Reads one or more recipes from JSON files, renders a table of contents page
    and one page per recipe, and crops every page to its content height. Each
    recipe page is rendered by a :class:`RecipeRenderer`.
    """

    def __init__(self, config: Config) -> None:
        """Initialize a RecipePDFBuilder for mobile-optimized recipe PDFs.

        Sets up the page builder and recipe renderer from the configuration and
        loads the recipe JSON files into memory.

        Args:
            config (Config): Validated configuration controlling page layout,
                margins, fonts, and colors.
        """
        self.config = config
        self.page = PageBuilder(config=self.config)
        self.renderer = RecipeRenderer(config=self.config, page=self.page)
        self.y_position = self.page.page_height
        self.recipes = [
            load_json_file(file_path=path)
            for path in sorted(
                Path(self.config.io.input_recipe_directory).glob("*.json")
            )
        ]

    def _draw_toc(self) -> None:
        """Draw the table of contents page.

        Fills the page background, renders a title block, then one clickable
        underlined entry per recipe with consistent spacing.
        """
        x = self.config.document_margins.left

        self.page.fill_background(self.config.toc.background_color)

        self.y_position = self.page.draw_text_block(
            text="Recepten",
            x=x,
            y=self.y_position,
            background_color=self.config.toc.title_font.background_color,
            font_name=self.config.toc.title_font.font_name,
            font_size=self.config.toc.title_font.font_size,
        )

        y = self.y_position - self.config.toc.items_top_margin

        for index, recipe in enumerate(self.recipes):
            if index > 0:
                y -= self.config.toc.item_spacing
            y = self.page.draw_link_text(
                text=recipe["title"],
                destination=f"recipe_{index}",
                x=x,
                y=y,
                font_name=self.config.toc.item_font.font_name,
                font_size=self.config.toc.item_font.font_size,
            )

        self.y_position = y
        self.page.draw_horizontal_line(y=self.y_position)

    def build(self) -> None:
        """Render a TOC page followed by one page per recipe, then save.

        The TOC links to each recipe page; every recipe page has a back link to
        the TOC. All pages are cropped to their content height.
        """
        content_bottom_ys: list[float] = []

        # TOC page.
        self.y_position = self.page.page_height
        self.page.bookmark("toc")
        self._draw_toc()
        content_bottom_ys.append(self.y_position)
        self.page.new_page()

        # Recipe pages.
        for index, recipe in enumerate(self.recipes):
            self.page.bookmark(f"recipe_{index}")
            content_bottom_y = self.renderer.render(recipe=recipe)
            content_bottom_ys.append(content_bottom_y)

            if index < len(self.recipes) - 1:
                self.page.new_page()

        self.page.save(content_bottom_ys=content_bottom_ys)
