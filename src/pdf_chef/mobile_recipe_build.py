"""Module for creating recipes in .pdf format optimized for mobile screen
format.
"""

from pathlib import Path
from typing import cast

from pdf_chef.config.config_model import ConfigModel
from pdf_chef.page_builder import PageBuilder
from pdf_chef.recipe_model import Recipe
from pdf_chef.recipe_renderer import RecipeRenderer
from pdf_chef.utils.utils_file_system import load_json_file


class RecipePDFBuilder:
    """Build recipe PDFs optimized for mobile screens.

    Reads one or more recipes from JSON files, renders a table of contents page
    and one page per recipe, and crops every page to its content height. Each
    recipe page is rendered by a :class:`RecipeRenderer`.

    Attributes:
        _config (ConfigModel): Validated configuration controlling page layout,
            margins, fonts, and colors.
        _page (PageBuilder): The page builder that all pages are drawn on.
        _renderer (RecipeRenderer): Renders the content of each recipe page.
        _y_position (float): Current vertical position on the page, in points.
        _recipes (list[Recipe]): The recipes loaded from the input directory,
            sorted by file name.

    Example:
        >>> config = ConfigManager().load_config_file(path="config.yaml")
        >>> builder = RecipePDFBuilder(config=config)
        >>> builder.build()
    """

    def __init__(self, config: ConfigModel) -> None:
        """Initialize a RecipePDFBuilder for mobile-optimized recipe PDFs.

        Sets up the page builder and recipe renderer from the configuration and
        loads the recipe JSON files into memory.

        Args:
            config (ConfigModel): Validated configuration controlling page
                layout, margins, fonts, and colors.
        """

        self._config: ConfigModel = config
        self._page: PageBuilder = PageBuilder(config=self._config)

        self._renderer: RecipeRenderer = RecipeRenderer(
            config=self._config, page=self._page
        )

        self._y_position: float = self._page.page_height
        self._recipes: list[Recipe] = []

        input_directory = Path(self._config.io.input_recipe_directory)
        recipe_glob = input_directory.glob("*.json")

        for recipe_path in sorted(recipe_glob):
            recipe_data = load_json_file(file_path=recipe_path)
            recipe = cast(Recipe, recipe_data)
            self._recipes.append(recipe)

    def _draw_toc(self) -> None:
        """Draw the table of contents page.

        Fills the page background, renders a title block, then one clickable
        underlined entry per recipe with consistent spacing.
        """

        x = self._config.document_margins.left

        self._page.fill_background(self._config.toc.background_color)

        self._y_position = self._page.draw_text_block(
            text=self._config.toc.title_text,
            x=x,
            y=self._y_position,
            background_color=self._config.toc.title_font.background_color,
            font_name=self._config.toc.title_font.font_name,
            font_size=self._config.toc.title_font.font_size,
        )

        y = self._y_position - self._config.toc.items_top_margin

        for index, recipe in enumerate(self._recipes):
            if index > 0:
                y -= self._config.toc.item_spacing

            y = self._page.draw_link_text(
                text=recipe["title"],
                destination=f"recipe_{index}",
                x=x,
                y=y,
                font_name=self._config.toc.item_font.font_name,
                font_size=self._config.toc.item_font.font_size,
            )

        self._y_position = y
        self._page.draw_horizontal_line(y=self._y_position)

    def build(self) -> None:
        """Render a TOC page followed by one page per recipe, then save.

        The TOC links to each recipe page; every recipe page has a back link to
        the TOC. All pages are cropped to their content height.
        """

        content_bottom_ys: list[float] = []

        # TOC page.
        self._y_position = self._page.page_height
        self._page.bookmark("toc")
        self._draw_toc()
        content_bottom_ys.append(self._y_position)
        self._page.new_page()

        # Recipe pages.
        for index, recipe in enumerate(self._recipes):
            self._page.bookmark(f"recipe_{index}")
            content_bottom_y = self._renderer.render(recipe=recipe)
            content_bottom_ys.append(content_bottom_y)

            if index < len(self._recipes) - 1:
                self._page.new_page()

        self._page.save(content_bottom_ys=content_bottom_ys)
