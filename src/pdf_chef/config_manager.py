"""Module for loading the configuration files."""

import yaml

from pathlib import Path

from pdf_chef.config.config_model import ConfigModel


class ConfigManager:
    """Load and validate YAML configuration files into ConfigModel objects.

    Example:
        >>> config_manager = ConfigManager()
        >>> config = config_manager.load_config_file(path="config.yaml")
    """

    def load_config_file(self, path: str | Path) -> ConfigModel:
        """Load and validate a YAML config file.

        Args:
            path (str | Path): Path to the YAML config file.

        Returns:
            config (ConfigModel): The validated configuration object.
        """
        with open(path, "r", encoding="utf-8") as f:
            raw_config = yaml.safe_load(f)

        config = ConfigModel(**raw_config)

        return config
