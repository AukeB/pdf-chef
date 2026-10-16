"""Pydantic models that mirror the layout of the YAML configuration file."""

from typing import Tuple

from pydantic import BaseModel, ConfigDict, field_validator

from pdf_chef.utils.utils_colors import normalize_rgb


class ConfiguredBaseModel(BaseModel):
    """Base model that forbids undeclared configuration fields."""

    model_config = ConfigDict(extra="forbid")


class ConfigModel(ConfiguredBaseModel):
    """Top-level validated configuration for building recipe PDFs.

    Attributes:
        io (ConfigModel.IO): Input and output file locations.
        page (ConfigModel.Page): Page dimensions.
        document_margins (ConfigModel.DocumentMargins): Horizontal margins of
            the document.
        section_margins (ConfigModel.SectionMargins): Vertical margins around
            each content section.
        layout_cover (ConfigModel.LayoutCover): Layout settings for the cover
            image.
        colors (ConfigModel.Colors): Color settings for lines.
        typography (ConfigModel.Typography): Typography settings for all recipe
            sections.
        toc (ConfigModel.Toc): Settings for the table of contents page.
        back_link (ConfigModel.BackLink): Settings for the back-to-overview link
            in the recipe title block.
    """

    class IO(ConfiguredBaseModel):
        """Input and output file locations.

        Attributes:
            output_file_path (str): Path of the generated PDF file.
            input_recipe_directory (str): Directory that holds the recipe JSON
                files.
        """

        output_file_path: str
        input_recipe_directory: str

    class Page(ConfiguredBaseModel):
        """Page dimensions.

        Attributes:
            width (int): Width of the page, in millimeters.
        """

        width: int

    class DocumentMargins(ConfiguredBaseModel):
        """Horizontal margins of the document.

        Attributes:
            left (int): Left margin, in points.
            right (int): Right margin, in points.
        """

        left: int
        right: int

    class SectionMargins(ConfiguredBaseModel):
        """Vertical margins around each content section.

        Attributes:
            top (int): Top margin, in points.
            bottom (int): Bottom margin, in points.
        """

        top: int
        bottom: int

    class LayoutCover(ConfiguredBaseModel):
        """Layout settings for the cover image.

        Attributes:
            image_height (int): Height of the cover image, in points.
            placeholder_color (Tuple[float, float, float]): Normalized RGB color
                of the placeholder shown when no cover image is available.
        """

        image_height: int
        placeholder_color: Tuple[float, float, float]

        @field_validator("placeholder_color", mode="before")
        @classmethod
        def _normalize_placeholder_color(cls, value: object) -> object:
            """Normalize a 0-255 RGB placeholder color to a 0-1 tuple.

            Args:
                value (object): The placeholder color as read from the config.

            Returns:
                normalized_color (object): The normalized color, or the value
                    unchanged when it is not a 3-element sequence.
            """

            normalized_color = normalize_rgb(value)

            return normalized_color

    class Colors(ConfiguredBaseModel):
        """Color settings for lines.

        Attributes:
            line_color (Tuple[float, float, float]): Normalized RGB color of the
                horizontal lines.
        """

        line_color: Tuple[float, float, float]

        @field_validator("line_color", mode="before")
        @classmethod
        def _convert_line_color(cls, value: object) -> object:
            """Normalize a 0-255 RGB line color to a 0-1 tuple.

            Args:
                value (object): The line color as read from the config.

            Returns:
                normalized_color (object): The normalized color, or the value
                    unchanged when it is not a 3-element sequence.
            """

            normalized_color = normalize_rgb(value)

            return normalized_color

    class Typography(ConfiguredBaseModel):
        """Typography settings for all recipe sections.

        Attributes:
            default (ConfigModel.Typography.Default): Document-wide font
                defaults.
            title (ConfigModel.Typography.FontStyle): Font of the recipe title.
            description (ConfigModel.Typography.FontStyle): Font of the recipe
                description.
            ingredients (ConfigModel.Typography.Ingredients): Typography and
                spacing for the ingredients section.
            instructions (ConfigModel.Typography.Instructions): Typography and
                spacing for the instructions section.
        """

        class Default(ConfiguredBaseModel):
            """Document-wide font defaults used as fallbacks in PageBuilder.

            Attributes:
                font_name (str): Name of the default font.
                font_size (int): Size of the default font, in points.
                font_shift_factor (float): Factor that corrects the vertical
                    text placement.
                line_height_factor (float): Line height as a multiple of the
                    font size.
            """

            font_name: str
            font_size: int
            font_shift_factor: float
            line_height_factor: float

        class FontStyle(ConfiguredBaseModel):
            """Simple font name and size pair.

            Attributes:
                font_name (str): Name of the font.
                font_size (int): Size of the font, in points.
            """

            font_name: str
            font_size: int

        class Ingredients(ConfiguredBaseModel):
            """Typography and spacing for the ingredients section.

            Attributes:
                bullet (str): Prefix drawn before each ingredient item.
                item_indent (int): Horizontal indent of the items, in points.
                section_spacing (int): Space above each category header, in
                    points.
                section_header_bottom_spacing (int): Space below a category
                    header before its first item, in points.
                category (ConfigModel.Typography.Ingredients.CategoryFont): Font
                    for the category headers.
                item (ConfigModel.Typography.Ingredients.ItemFont): Font for the
                    ingredient items.
            """

            class CategoryFont(ConfiguredBaseModel):
                """Font for ingredient category headers.

                Attributes:
                    font_name (str): Name of the font.
                    font_size (int): Size of the font, in points.
                """

                font_name: str
                font_size: int

            class ItemFont(ConfiguredBaseModel):
                """Font for individual ingredient items.

                Attributes:
                    font_name (str): Name of the font.
                    font_size (int): Size of the font, in points.
                """

                font_name: str
                font_size: int

            bullet: str
            item_indent: int
            section_spacing: int
            section_header_bottom_spacing: int
            category: CategoryFont
            item: ItemFont

        class Instructions(ConfiguredBaseModel):
            """Typography and spacing for the instructions section.

            Attributes:
                step_indent (int): Horizontal indent of the steps, in points.
                section_spacing (int): Space above each section header, in
                    points.
                section_header_bottom_spacing (int): Space below a section
                    header before its first step, in points.
                header (ConfigModel.Typography.Instructions.HeaderFont): Font
                    for the section headers.
                step (ConfigModel.Typography.Instructions.StepFont): Font for
                    the individual steps.
            """

            class HeaderFont(ConfiguredBaseModel):
                """Font for instruction section headers.

                Attributes:
                    font_name (str): Name of the font.
                    font_size (int): Size of the font, in points.
                """

                font_name: str
                font_size: int

            class StepFont(ConfiguredBaseModel):
                """Font for individual instruction steps.

                Attributes:
                    font_name (str): Name of the font.
                    font_size (int): Size of the font, in points.
                """

                font_name: str
                font_size: int

            step_indent: int
            section_spacing: int
            section_header_bottom_spacing: int
            header: HeaderFont
            step: StepFont

        default: Default
        title: FontStyle
        description: FontStyle
        ingredients: Ingredients
        instructions: Instructions

    class Toc(ConfiguredBaseModel):
        """Settings for the table of contents page.

        Attributes:
            title_text (str): Title shown at the top of the table of contents.
            background_color (Tuple[float, float, float]): Normalized RGB
                background color of the page.
            items_top_margin (int): Space between the title divider and the
                first item, in points.
            item_spacing (int): Space between recipe items, in points.
            title_font (ConfigModel.Toc.TitleFont): Font and background color of
                the title block.
            item_font (ConfigModel.Toc.ItemFont): Font of the recipe links.
        """

        class TitleFont(ConfiguredBaseModel):
            """Font and background color for the TOC title block.

            Attributes:
                font_name (str): Name of the font.
                font_size (int): Size of the font, in points.
                background_color (Tuple[float, float, float]): Normalized RGB
                    background color of the title block.
            """

            font_name: str
            font_size: int
            background_color: Tuple[float, float, float]

            @field_validator("background_color", mode="before")
            @classmethod
            def _convert_background_color(cls, value: object) -> object:
                """Normalize a 0-255 RGB background color to a 0-1 tuple.

                Args:
                    value (object): The background color as read from the
                        config.

                Returns:
                    normalized_color (object): The normalized color, or the
                        value unchanged when it is not a 3-element sequence.
                """

                normalized_color = normalize_rgb(value)

                return normalized_color

        class ItemFont(ConfiguredBaseModel):
            """Font for TOC recipe link items.

            Attributes:
                font_name (str): Name of the font.
                font_size (int): Size of the font, in points.
            """

            font_name: str
            font_size: int

        title_text: str
        background_color: Tuple[float, float, float]
        items_top_margin: int
        item_spacing: int
        title_font: TitleFont
        item_font: ItemFont

        @field_validator("background_color", mode="before")
        @classmethod
        def _convert_background_color(cls, value: object) -> object:
            """Normalize a 0-255 RGB background color to a 0-1 tuple.

            Args:
                value (object): The background color as read from the config.

            Returns:
                normalized_color (object): The normalized color, or the value
                    unchanged when it is not a 3-element sequence.
            """

            normalized_color = normalize_rgb(value)

            return normalized_color

    class BackLink(ConfiguredBaseModel):
        """Settings for the back-to-overview link in the recipe title block.

        Attributes:
            text (str): Text of the back link.
            bottom_margin (int): Gap between the link baseline and the title
                block divider, in points.
            font (ConfigModel.BackLink.Font): Font of the back link.
        """

        class Font(ConfiguredBaseModel):
            """Font for the back link text.

            Attributes:
                font_name (str): Name of the font.
                font_size (int): Size of the font, in points.
            """

            font_name: str
            font_size: int

        text: str
        bottom_margin: int
        font: Font

    io: IO
    page: Page
    document_margins: DocumentMargins
    section_margins: SectionMargins
    layout_cover: LayoutCover
    colors: Colors
    typography: Typography
    toc: Toc
    back_link: BackLink
