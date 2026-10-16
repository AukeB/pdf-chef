from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from pdf_chef.config_manager import ConfigManager

PROJECT_CONFIG_PATH = (
    Path(__file__).resolve().parents[2]
    / "src"
    / "pdf_chef"
    / "configs"
    / "config_mobile_recipes.yaml"
)


# Testing the "load_config_file" method from the "ConfigManager" class.


def test_load_config_file_loads_project_config() -> None:
    """The project YAML file validates into a ConfigModel."""

    config_manager = ConfigManager()

    project_config = config_manager.load_config_file(path=PROJECT_CONFIG_PATH)

    assert project_config.page.width == 90


def test_load_config_file_rejects_unknown_key(
    tmp_path: Path, raw_config: dict[str, Any]
) -> None:
    """A key that is not declared in the model fails at load time."""

    raw_config["unknown_section"] = {"value": 1}
    config_path = tmp_path / "config.yaml"
    config_path.write_text(yaml.safe_dump(raw_config), encoding="utf-8")

    config_manager = ConfigManager()

    with pytest.raises(ValidationError):
        config_manager.load_config_file(path=config_path)
