"""Module for rendering a single recipe's sections onto a page."""

from pathlib import Path
from typing import Tuple, cast

from pdf_chef.page_builder import PageBuilder
from pdf_chef.text_segment import TextSegment
from pdf_chef.config_manager import Config
from pdf_chef.utils.utils_colors import normalize_rgb


class RecipeRenderer:
    """Render one recipe as vertically stacked, styled blocks onto a page.

    Translates a single recipe's data and the shared configuration into
    :class:`PageBuilder` drawing calls, tracking the current vertical position
    and cycling background colors across sections.
    """

    def __init__(self, config: Config, page: PageBuilder) -> None:
        """Initialize a RecipeRenderer.

        Args:
            config (Config): Validated configuration controlling page layout,
                margins, fonts, and colors.
            page (PageBuilder): The page builder used to draw the recipe.
        """

        self.config = config
        self.page = page
        self.y_position: float = self.page.page_height
        self.section_counter: int = 0
        self.background_color_palette: list[Tuple[float, float, float]] = []

    def render(self, recipe: dict) -> float:
        """Render a single recipe onto the current page.

        Resets the render state, selects the recipe's background palette, and
        draws each known section in the order it appears in the recipe.

        Args:
            recipe (dict): The recipe to render.

        Returns:
            float: The vertical position of the bottom of the drawn content, in
                points.
        """

        self.y_position = self.page.page_height
        self.section_counter = 0
        self.background_color_palette = [
            cast(Tuple[float, float, float], normalize_rgb(color))
            for color in recipe["colors"]["background_color_palette"]
        ]

        self._draw_cover_image(image_path=recipe.get("cover_image"))

        for section_name in recipe.keys():
            if section_name == "cover_image":
                continue
            self.add_section(recipe=recipe, section_name=section_name)

        return self.y_position

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

        self.y_position = self.page.draw_image(
            image_path=image_path, y_pos=self.y_position
        )

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

        background_color = self.background_color_palette[
            self.section_counter % len(self.background_color_palette)
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

        background_color = self.background_color_palette[
            self.section_counter % len(self.background_color_palette)
        ]

        self.y_position = self.page.draw_structured_block(
            segments=segments,
            x=self.config.document_margins.left,
            y=self.y_position,
            background_color=background_color,
            font_name=font_name,
            font_size=font_size,
        )

        self.section_counter += 1

    def _draw_instructions(self, instructions: list[dict]) -> None:
        """Draw the recipe instructions as a single uniform section.

        All instruction sections are rendered together in one block so the whole
        instructions area shares a single background color. Each section
        contributes a header line ``"<section_number>. <section>"`` followed by
        indented step lines formatted as ``"<section_number>.<step_number>
        <text>"``. Extra vertical space is inserted above every section header
        except the first.

        Args:
            instructions (list[dict]): Instruction sections, each containing a
                ``section_number``, ``section`` title, and a list of ``steps``
                where every step has a ``step_number`` and ``text``.
        """

        segments: list[TextSegment] = []

        for index, section in enumerate(instructions):
            section_number = section["section_number"]
            segments.append(
                TextSegment(
                    text=f"{section_number}. {section['section']}",
                    space_before=0.0
                    if index == 0
                    else self.config.typography.instructions.section_spacing,
                    font_name=self.config.typography.instructions.header.font_name,
                    font_size=self.config.typography.instructions.header.font_size,
                )
            )

            for step_index, step in enumerate(section["steps"]):
                segments.append(
                    TextSegment(
                        text=f"{section_number}.{step['step_number']} {step['text']}",
                        indent=self.config.typography.instructions.step_indent,
                        space_before=(
                            self.config.typography.instructions.section_header_bottom_spacing
                            if step_index == 0
                            else 0.0
                        ),
                        font_name=self.config.typography.instructions.step.font_name,
                        font_size=self.config.typography.instructions.step.font_size,
                    )
                )

        self._draw_structured_block(segments=segments)

    def _draw_ingredients(self, ingredients: list[dict]) -> None:
        """Draw the categorized ingredient list as a single structured block.

        Each category is rendered as a bold header followed by indented,
        bulleted items, mirroring the layout of instruction sections.

        Args:
            ingredients (list[dict]): Ingredient categories, each containing a
                ``category`` name and a list of ``items``.
        """

        segments: list[TextSegment] = []

        for index, category in enumerate(ingredients):
            segments.append(
                TextSegment(
                    text=category["category"],
                    space_before=0.0
                    if index == 0
                    else self.config.typography.ingredients.section_spacing,
                    font_name=self.config.typography.ingredients.category.font_name,
                    font_size=self.config.typography.ingredients.category.font_size,
                )
            )

            for item_index, item in enumerate(category["items"]):
                segments.append(
                    TextSegment(
                        text=f"{self.config.typography.ingredients.bullet}{item}",
                        indent=self.config.typography.ingredients.item_indent,
                        space_before=(
                            self.config.typography.ingredients.section_header_bottom_spacing
                            if item_index == 0
                            else 0.0
                        ),
                        font_name=self.config.typography.ingredients.item.font_name,
                        font_size=self.config.typography.ingredients.item.font_size,
                    )
                )

        self._draw_structured_block(segments=segments)

    def _draw_title_with_back_link(self, title: str) -> None:
        """Draw the recipe title block and overlay a back link in the lower-
        right.

        Args:
            title (str): The recipe title text to render.
        """

        self._draw_text_block(
            text=title,
            font_size=self.config.typography.title.font_size,
            font_name=self.config.typography.title.font_name,
        )
        self._draw_back_link(title_block_bottom=self.y_position)

    def _draw_back_link(self, title_block_bottom: float) -> None:
        """Draw the back-to-overview link in the lower-right of the title block.

        Args:
            title_block_bottom (float): Y position of the bottom divider of the
                title block, in points.
        """

        self.page.draw_inline_link_right(
            text=self.config.back_link.text,
            destination="toc",
            y=title_block_bottom
            + self.config.back_link.bottom_margin
            + self.config.back_link.font.font_size,
            font_name=self.config.back_link.font.font_name,
            font_size=self.config.back_link.font.font_size,
        )

    def add_section(self, recipe: dict, section_name: str) -> None:
        """Add a recipe section by name using a dispatch table.

        Args:
            recipe (dict): The recipe whose section should be rendered.
            section_name (str): Name of the recipe section to render. Only known
                section names are drawn; unknown names are ignored.
        """

        section_handlers = {
            "title": lambda value: self._draw_title_with_back_link(value),
            "description": lambda value: self._draw_text_block(
                text=value,
                font_size=self.config.typography.description.font_size,
                font_name=self.config.typography.description.font_name,
            ),
            "ingredients": lambda value: self._draw_ingredients(ingredients=value),
            "instructions": lambda value: self._draw_instructions(instructions=value),
        }

        if section_name in section_handlers:
            handler = section_handlers[section_name]
            handler(recipe[section_name])
