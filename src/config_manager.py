"""Module for loading the configuration files."""

import yaml
from pydantic import BaseModel
from typing import Literal



class Config(BaseModel):
    class DocumentMargins(BaseModel):
        left: int
        right: int

    class SectionMargins(BaseModel):
        top: int
        bottom: int

    class LayoutCover(BaseModel):
        image_height: int

    class Font(BaseModel):
        font_shift_factor: float

    class Colors(BaseModel):
        color_mode: Literal["repeating"]
        palette: list

    document_margins: DocumentMargins
    section_margins: SectionMargins
    layout_cover: LayoutCover
    font: Font
    colors: Colors


class ConfigManager:
    """Utility class for loading and validating YAML config files."""

    def load_config_file(self, path: str) -> Config:
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