from pytest import approx

from pdf_chef.config.config_model import ConfigModel
from pdf_chef.page_builder import PageBuilder
from pdf_chef.recipe_model import Recipe
from pdf_chef.recipe_renderer import RecipeRenderer


# Testing the "_current_background_color" method from the "RecipeRenderer" class.


def test_current_background_color_cycles_through_palette(
    config: ConfigModel, sample_recipe: Recipe
) -> None:
    """Consecutive sections alternate through the recipe palette."""

    page = PageBuilder(config=config)
    renderer = RecipeRenderer(config=config, page=page)
    renderer._load_palette(recipe=sample_recipe)

    first = renderer._current_background_color()
    renderer._section_counter = 1
    second = renderer._current_background_color()
    renderer._section_counter = 2
    third = renderer._current_background_color()

    assert first == approx((246 / 255, 235 / 255, 214 / 255))
    assert second == approx((199 / 255, 140 / 255, 50 / 255))
    assert third == first


# Testing the "render" method from the "RecipeRenderer" class.


def test_render_returns_bottom_of_content(
    config: ConfigModel, sample_recipe: Recipe
) -> None:
    """Rendering a recipe returns a position inside the page, below the top."""

    page = PageBuilder(config=config)
    renderer = RecipeRenderer(config=config, page=page)

    content_bottom_y = renderer.render(recipe=sample_recipe)

    assert 0 < content_bottom_y < page.page_height


def test_render_missing_cover_image_draws_placeholder(
    config: ConfigModel, sample_recipe: Recipe
) -> None:
    """A cover image path that does not exist falls back to the placeholder."""

    page = PageBuilder(config=config)
    renderer = RecipeRenderer(config=config, page=page)
    sample_recipe["cover_image"] = "does/not/exist.jpg"

    content_bottom_y = renderer.render(recipe=sample_recipe)

    assert 0 < content_bottom_y < page.page_height


# Testing the "_add_section" method from the "RecipeRenderer" class.


def test_add_section_ignores_unknown_section(
    config: ConfigModel, sample_recipe: Recipe
) -> None:
    """Section names without a handler leave the vertical position unchanged."""

    page = PageBuilder(config=config)
    renderer = RecipeRenderer(config=config, page=page)
    y_before = renderer._y_position

    renderer._add_section(recipe=sample_recipe, section_name="servings")

    assert renderer._y_position == y_before
