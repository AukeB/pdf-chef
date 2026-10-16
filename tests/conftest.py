"""Shared fixtures for the test suite."""

from pathlib import Path
from typing import Any

import pytest
import yaml

from pdf_chef.config.config_model import ConfigModel
from pdf_chef.recipe_model import Recipe

REPO_ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = REPO_ROOT / "src" / "pdf_chef" / "configs" / "config_mobile_recipes.yaml"


@pytest.fixture
def raw_config() -> dict[str, Any]:
    """Return the project YAML config as an unvalidated dictionary.

    Returns:
        raw_config (dict[str, Any]): The parsed YAML content. Its shape is only
            known after validation, so it stays generic here.
    """

    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        raw_config = yaml.safe_load(f)

    return raw_config


@pytest.fixture
def config(raw_config: dict[str, Any], tmp_path: Path) -> ConfigModel:
    """Return the validated project config, redirected into a temporary folder.

    The output PDF is written to ``tmp_path`` and the recipe input directory is
    an empty folder inside ``tmp_path``, so tests never touch the real files.

    Args:
        raw_config (dict[str, Any]): The unvalidated project config.
        tmp_path (Path): The temporary folder provided by pytest.

    Returns:
        config (ConfigModel): The validated configuration.
    """

    input_directory = tmp_path / "recipes"
    input_directory.mkdir()

    raw_config["io"]["output_file_path"] = str(tmp_path / "out" / "recipes.pdf")
    raw_config["io"]["input_recipe_directory"] = str(input_directory)

    config = ConfigModel(**raw_config)

    return config


@pytest.fixture
def sample_recipe() -> Recipe:
    """Return a small recipe without a cover image.

    Returns:
        recipe (Recipe): A recipe with a two-color palette, one ingredient
            category and one instruction section.
    """

    recipe: Recipe = {
        "title": "Test soup",
        "description": "A short description of the soup.",
        "servings": 2,
        "colors": {
            "background_color_palette": [[246, 235, 214], [199, 140, 50]],
        },
        "ingredients": [
            {"category": "Basis", "items": ["1 onion", "2 carrots"]},
        ],
        "instructions": [
            {
                "section_number": 1,
                "section": "Maak het",
                "steps": [{"step_number": 1, "text": "Snijd de ui."}],
            },
        ],
    }

    return recipe
