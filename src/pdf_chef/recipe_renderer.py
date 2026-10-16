"""Module for rendering a single recipe's sections onto a page."""

from pathlib import Path
from typing import Tuple, cast

from pdf_chef.config.config_model import ConfigModel
from pdf_chef.page_builder import PageBuilder
from pdf_chef.recipe_model import (
    Recipe,
    RecipeIngredient,
    RecipeInstructionSection,
)
from pdf_chef.text_segment import TextSegment
from pdf_chef.utils.utils_colors import normalize_rgb


class RecipeRenderer:
    """Render one recipe as vertically stacked, styled blocks onto a page.

    Translates a single recipe's data and the shared configuration into
    :class:`PageBuilder` drawing calls, tracking the current vertical position
    and cycling background colors across sections.

    Attributes:
        _config (ConfigModel): Validated configuration controlling page layout,
            margins, fonts, and colors.
        _page (PageBuilder): The page builder used to draw the recipe.
        _y_position (float): Current vertical position on the page, in points.
        _section_counter (int): Number of sections drawn so far on the current
            recipe, used to pick the background color.
        _background_color_palette (list[Tuple[float, float, float]]): Normalized
            RGB background colors of the current recipe.

    Example:
        renderer = RecipeRenderer(config=config, page=page) content_bottom_y =
        renderer.render(recipe=recipe)
    """

    def __init__(self, config: ConfigModel, page: PageBuilder) -> None:
        """Initialize a RecipeRenderer.

        Args:
            config (ConfigModel): Validated configuration controlling page
                layout, margins, fonts, and colors.
            page (PageBuilder): The page builder used to draw the recipe.
        """

        self._config: ConfigModel = config
        self._page: PageBuilder = page
        self._y_position: float = self._page.page_height
        self._section_counter: int = 0
        self._background_color_palette: list[Tuple[float, float, float]] = []

    def _draw_cover_image(self, image_path: str | None) -> None:
        """Draw the recipe cover image and update the vertical position.

        When ``image_path`` is ``None`` or points to a file that does not exist,
        a light-gray placeholder is drawn instead.

        Args:
            image_path (str | None): Path to the cover image to draw, or
                ``None`` to draw a placeholder.
        """

        if image_path is not None and not Path(image_path).is_file():
            image_path = None

        self._y_position = self._page.draw_image(
            image_path=image_path, y_pos=self._y_position
        )

    def _current_background_color(self) -> Tuple[float, float, float]:
        """Select the background color of the current section from the palette.

        The palette is cycled through based on the current section counter.

        Returns:
            background_color (Tuple[float, float, float]): The normalized RGB
                background color of the current section.
        """

        palette_index = self._section_counter % len(self._background_color_palette)
        background_color = self._background_color_palette[palette_index]

        return background_color

    def _draw_text_block(
        self,
        text: str,
        font_name: str | None = None,
        font_size: int | None = None,
    ) -> None:
        """Draw a styled text block with background and a horizontal divider.

        The background color is selected from the configured palette by cycling
        through it based on the current section counter, which is incremented
        after the block is drawn.

        Args:
            text (str): Text content to draw.
            font_name (str | None): Optional font name override.
            font_size (int | None): Optional font size override.
        """

        background_color = self._current_background_color()

        self._y_position = self._page.draw_text_block(
            text=text,
            x=self._config.document_margins.left,
            y=self._y_position,
            background_color=background_color,
            font_name=font_name,
            font_size=font_size,
        )

        self._section_counter += 1

    def _draw_structured_block(
        self,
        segments: list[TextSegment],
        font_name: str | None = None,
        font_size: int | None = None,
    ) -> None:
        """Draw a structured block of segments with a cycling background color.

        Args:
            segments (list[TextSegment]): Ordered text segments to draw.
            font_name (str | None): Optional font name override.
            font_size (int | None): Optional font size override.
        """

        background_color = self._current_background_color()

        self._y_position = self._page.draw_structured_block(
            segments=segments,
            x=self._config.document_margins.left,
            y=self._y_position,
            background_color=background_color,
            font_name=font_name,
            font_size=font_size,
        )

        self._section_counter += 1

    def _draw_instructions(self, instructions: list[RecipeInstructionSection]) -> None:
        """Draw the recipe instructions as a single uniform section.

        All instruction sections are rendered together in one block so the whole
        instructions area shares a single background color. Each section
        contributes a header line ``"<section_number>. <section>"`` followed by
        indented step lines formatted as ``"<section_number>.<step_number>
        <text>"``. Extra vertical space is inserted above every section header
        except the first.

        Args:
            instructions (list[RecipeInstructionSection]): Instruction sections,
                each containing a ``section_number``, ``section`` title, and a
                list of ``steps`` where every step has a ``step_number`` and
                ``text``.
        """

        segments: list[TextSegment] = []
        instructions_style = self._config.typography.instructions

        for index, section in enumerate(instructions):
            section_number = section["section_number"]
            header_space_before = (
                0.0 if index == 0 else instructions_style.section_spacing
            )

            header_segment = TextSegment(
                text=f"{section_number}. {section['section']}",
                space_before=header_space_before,
                font_name=instructions_style.header.font_name,
                font_size=instructions_style.header.font_size,
            )
            segments.append(header_segment)

            for step_index, step in enumerate(section["steps"]):
                step_space_before = (
                    instructions_style.section_header_bottom_spacing
                    if step_index == 0
                    else 0.0
                )

                step_segment = TextSegment(
                    text=f"{section_number}.{step['step_number']} {step['text']}",
                    indent=instructions_style.step_indent,
                    space_before=step_space_before,
                    font_name=instructions_style.step.font_name,
                    font_size=instructions_style.step.font_size,
                )
                segments.append(step_segment)

        self._draw_structured_block(segments=segments)

    def _draw_ingredients(self, ingredients: list[RecipeIngredient]) -> None:
        """Draw the categorized ingredient list as a single structured block.

        Each category is rendered as a bold header followed by indented,
        bulleted items, mirroring the layout of instruction sections.

        Args:
            ingredients (list[RecipeIngredient]): Ingredient categories, each
                containing a ``category`` name and a list of ``items``.
        """

        segments: list[TextSegment] = []
        ingredients_style = self._config.typography.ingredients

        for index, category in enumerate(ingredients):
            category_space_before = (
                0.0 if index == 0 else ingredients_style.section_spacing
            )

            category_segment = TextSegment(
                text=category["category"],
                space_before=category_space_before,
                font_name=ingredients_style.category.font_name,
                font_size=ingredients_style.category.font_size,
            )
            segments.append(category_segment)

            for item_index, item in enumerate(category["items"]):
                item_space_before = (
                    ingredients_style.section_header_bottom_spacing
                    if item_index == 0
                    else 0.0
                )

                item_segment = TextSegment(
                    text=f"{ingredients_style.bullet}{item}",
                    indent=ingredients_style.item_indent,
                    space_before=item_space_before,
                    font_name=ingredients_style.item.font_name,
                    font_size=ingredients_style.item.font_size,
                )
                segments.append(item_segment)

        self._draw_structured_block(segments=segments)

    def _draw_back_link(self, title_block_bottom: float) -> None:
        """Draw the back-to-overview link in the lower-right of the title block.

        Args:
            title_block_bottom (float): Y position of the bottom divider of the
                title block, in points.
        """

        self._page.draw_inline_link_right(
            text=self._config.back_link.text,
            destination="toc",
            y=title_block_bottom
            + self._config.back_link.bottom_margin
            + self._config.back_link.font.font_size,
            font_name=self._config.back_link.font.font_name,
            font_size=self._config.back_link.font.font_size,
        )

    def _draw_title_with_back_link(self, title: str) -> None:
        """Draw the recipe title block and overlay a back link in the lower-
        right.

        Args:
            title (str): The recipe title text to render.
        """

        self._draw_text_block(
            text=title,
            font_size=self._config.typography.title.font_size,
            font_name=self._config.typography.title.font_name,
        )
        self._draw_back_link(title_block_bottom=self._y_position)

    def _add_section(self, recipe: Recipe, section_name: str) -> None:
        """Add a recipe section by name using a dispatch table.

        Args:
            recipe (Recipe): The recipe whose section should be rendered.
            section_name (str): Name of the recipe section to render. Only known
                section names are drawn; unknown names are ignored.
        """

        section_handlers = {
            "title": lambda: self._draw_title_with_back_link(title=recipe["title"]),
            "description": lambda: self._draw_text_block(
                text=recipe["description"],
                font_size=self._config.typography.description.font_size,
                font_name=self._config.typography.description.font_name,
            ),
            "ingredients": lambda: self._draw_ingredients(
                ingredients=recipe["ingredients"]
            ),
            "instructions": lambda: self._draw_instructions(
                instructions=recipe["instructions"]
            ),
        }

        if section_name in section_handlers:
            handler = section_handlers[section_name]
            handler()

    def _load_palette(self, recipe: Recipe) -> None:
        """Load the recipe's background palette as normalized RGB colors.

        Args:
            recipe (Recipe): The recipe whose palette should be loaded.
        """

        palette: list[Tuple[float, float, float]] = []

        for color in recipe["colors"]["background_color_palette"]:
            normalized_color = normalize_rgb(color)
            palette_color = cast(Tuple[float, float, float], normalized_color)
            palette.append(palette_color)

        self._background_color_palette = palette

    def render(self, recipe: Recipe) -> float:
        """Render a single recipe onto the current page.

        Resets the render state, selects the recipe's background palette, and
        draws each known section in the order it appears in the recipe.

        Args:
            recipe (Recipe): The recipe to render.

        Returns:
            content_bottom_y (float): The vertical position of the bottom of the
                drawn content, in points.
        """

        self._y_position = self._page.page_height
        self._section_counter = 0
        self._load_palette(recipe=recipe)

        cover_image = recipe.get("cover_image")
        self._draw_cover_image(image_path=cover_image)

        for section_name in recipe.keys():
            if section_name == "cover_image":
                continue
            self._add_section(recipe=recipe, section_name=section_name)

        content_bottom_y = self._y_position

        return content_bottom_y
