import json
from pathlib import Path

from pypdf import PdfReader

from pdf_chef.config.config_model import ConfigModel
from pdf_chef.mobile_recipe_build import RecipePDFBuilder
from pdf_chef.recipe_model import Recipe

REPO_ROOT = Path(__file__).resolve().parents[2]


# Testing the "build" method from the "RecipePDFBuilder" class.


def test_build_writes_toc_and_one_page_per_recipe(
    config: ConfigModel, sample_recipe: Recipe
) -> None:
    """The output has a table of contents page followed by one page per recipe."""

    recipe_path = Path(config.io.input_recipe_directory) / "test_soup.json"
    recipe_path.write_text(json.dumps(sample_recipe), encoding="utf-8")

    builder = RecipePDFBuilder(config=config)
    builder.build()

    reader = PdfReader(config.io.output_file_path)
    toc_text = reader.pages[0].extract_text()

    assert len(reader.pages) == 2
    assert "Recepten" in toc_text
    assert "Test soup" in toc_text


def test_build_renders_all_project_recipes(config: ConfigModel) -> None:
    """Building the project recipes gives a TOC page plus one page per recipe."""

    config.io.input_recipe_directory = str(REPO_ROOT / "recipes")

    builder = RecipePDFBuilder(config=config)
    builder.build()

    reader = PdfReader(config.io.output_file_path)

    assert len(reader.pages) == 10
