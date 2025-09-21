"""Module for loading the configuration files."""

import yaml

from pathlib import Path
from pydantic import BaseModel
from typing import Literal, Tuple


class IO(BaseModel):
    output_file_path: str
    input_recipe_file_path: str


class Page(BaseModel):
    width: int
    height: int


class DocumentMargins(BaseModel):
    left: int
    right: int


class SectionMargins(BaseModel):
    top: int
    bottom: int


class LayoutCover(BaseModel):
    image_height: int


class Font(BaseModel):
    font_name: str
    font_size: int
    font_shift_factor: float
    line_height_factor: float


class Colors(BaseModel):
    background_color_mode: Literal["repeating"]
    background_color_palette: list[Tuple[float, float, float]]
    line_color: Tuple[float, float, float]


class Config(BaseModel):
    io: IO
    page: Page
    document_margins: DocumentMargins
    section_margins: SectionMargins
    layout_cover: LayoutCover
    font: Font
    colors: Colors


class ConfigManager:
    """Utility class for loading and validating YAML config files."""

    def load_config_file(self, path: str | Path) -> Config:
        path = str(path)
        """
        Load and validate a YAML config file.

        Args:
            path (str): Path to the YAML config file.

        Returns:
            dict: The validated config as a dictionary.
        """
        with open(path, "r", encoding="utf-8") as f:
            raw_config = yaml.safe_load(f)

        return Config(**raw_config)
