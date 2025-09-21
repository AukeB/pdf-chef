"""Module for loading the configuration files."""

import yaml
from pydantic import BaseModel, Field, conlist
from typing import Literal


class DocumentMargins(BaseModel):
    LEFT: int = Field(..., description="Left margin in pixels")
    RIGHT: int = Field(..., description="Right margin in pixels")


class SectionMargins(BaseModel):
    TOP: int = Field(..., description="Top margin in pixels")
    BOTTOM: int = Field(..., description="Bottom margin in pixels")


class LayoutCover(BaseModel):
    IMAGE_HEIGHT: int = Field(..., description="Cover image height in pixels")


class FontConfig(BaseModel):
    FONT_SHIFT_FACTOR: float = Field(
        ..., description="Font baseline vertical shift factor"
    )


class ColorsConfig(BaseModel):
    COLOR_MODE: Literal["repeating"] = Field(
        ..., description="Color mode (currently only 'repeating' is allowed)"
    )
    PALETTE: list[conlist(float, min_items=3, max_items=3)] = Field(
        ..., description="List of RGB colors as normalized floats"
    )


class ConfigSchema(BaseModel):
    DOCUMENT_MARGINS: DocumentMargins
    SECTION_MARGINS: SectionMargins
    LAYOUT_COVER: LayoutCover
    FONT: FontConfig
    COLORS: ColorsConfig


# -------------------------
# Config Manager
# -------------------------


class ConfigManager:
    """Utility class for loading and validating YAML config files."""

    def load_config_file(self, path: str) -> dict:
        """
        Load and validate a YAML config file.

        Args:
            path (str): Path to the YAML config file.

        Returns:
            dict: The validated config as a dictionary.
        """
        with open(path, "r", encoding="utf-8") as f:
            raw_config = yaml.safe_load(f)

        config = ConfigSchema(**raw_config)
        return config.model_dump()
