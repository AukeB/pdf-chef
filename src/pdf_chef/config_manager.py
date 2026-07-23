"""Module for loading the configuration files."""

import yaml

from pathlib import Path
from pydantic import BaseModel, ConfigDict, field_validator
from typing import Tuple

from pdf_chef.utils.utils_colors import normalize_rgb


class StrictModel(BaseModel):
    """Base model that forbids undeclared configuration fields."""

    model_config = ConfigDict(extra="forbid")


class Config(StrictModel):
    """Top-level validated configuration for building recipe PDFs."""

    class IO(StrictModel):
        """Input and output file locations."""

        output_file_path: str
        input_recipe_directory: str

    class Page(StrictModel):
        """Page dimensions."""

        width: int

    class DocumentMargins(StrictModel):
        """Horizontal margins of the document."""

        left: int
        right: int

    class SectionMargins(StrictModel):
        """Vertical margins around each content section."""

        top: int
        bottom: int

    class LayoutCover(StrictModel):
        """Layout settings for the cover image."""

        image_height: int
        placeholder_color: Tuple[float, float, float]

        @field_validator("placeholder_color", mode="before")
        @classmethod
        def _normalize_placeholder_color(cls, value: object) -> object:
            return normalize_rgb(value)

    class Colors(StrictModel):
        """Color settings for lines."""

        line_color: Tuple[float, float, float]

        @field_validator("line_color", mode="before")
        @classmethod
        def _convert_line_color(cls, value: object) -> object:
            """Normalize a 0-255 RGB line color to a 0-1 tuple."""

            return normalize_rgb(value)

    class Typography(StrictModel):
        """Typography settings for all recipe sections."""

        class Default(StrictModel):
            """Document-wide font defaults used as fallbacks in PageBuilder."""

            font_name: str
            font_size: int
            font_shift_factor: float
            line_height_factor: float

        class FontStyle(StrictModel):
            """Simple font name and size pair."""

            font_name: str
            font_size: int

        class Ingredients(StrictModel):
            """Typography and spacing for the ingredients section."""

            class CategoryFont(StrictModel):
                """Font for ingredient category headers."""

                font_name: str
                font_size: int

            class ItemFont(StrictModel):
                """Font for individual ingredient items."""

                font_name: str
                font_size: int

            bullet: str
            item_indent: int
            section_spacing: int
            section_header_bottom_spacing: int
            category: CategoryFont
            item: ItemFont

        class Instructions(StrictModel):
            """Typography and spacing for the instructions section."""

            class HeaderFont(StrictModel):
                """Font for instruction section headers."""

                font_name: str
                font_size: int

            class StepFont(StrictModel):
                """Font for individual instruction steps."""

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

    class Toc(StrictModel):
        """Settings for the table of contents page."""

        class TitleFont(StrictModel):
            """Font and background color for the TOC title block."""

            font_name: str
            font_size: int
            background_color: Tuple[float, float, float]

            @field_validator("background_color", mode="before")
            @classmethod
            def _convert_background_color(cls, value: object) -> object:
                """Normalize a 0-255 RGB background color to a 0-1 tuple."""

                return normalize_rgb(value)

        class ItemFont(StrictModel):
            """Font for TOC recipe link items."""

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
            """Normalize a 0-255 RGB background color to a 0-1 tuple."""

            return normalize_rgb(value)

    class BackLink(StrictModel):
        """Settings for the back-to-overview link in the recipe title block."""

        class Font(StrictModel):
            """Font for the back link text."""

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


class ConfigManager:
    """Load and validate YAML configuration files into Config objects."""

    def load_config_file(self, path: str | Path) -> Config:
        """Load and validate a YAML config file.

        Args:
            path (str | Path): Path to the YAML config file.

        Returns:
            Config: The validated configuration object.
        """
        with open(path, "r", encoding="utf-8") as f:
            raw_config = yaml.safe_load(f)

        return Config(**raw_config)
