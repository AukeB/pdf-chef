"""TypedDicts that describe the structure of a recipe JSON file."""

from typing import NotRequired, TypedDict


class RecipeColors(TypedDict):
    """Color settings of a recipe.

    Attributes:
        background_color_palette (list[list[int]]): 0-255 RGB colors that the
            sections cycle through as their background.
    """

    background_color_palette: list[list[int]]


class RecipeIngredient(TypedDict):
    """One ingredient category of a recipe.

    Attributes:
        category (str): Name of the category.
        items (list[str]): Ingredients in this category.
    """

    category: str
    items: list[str]


class RecipeInstructionStep(TypedDict):
    """One numbered step within an instruction section.

    Attributes:
        step_number (int): Number of the step within its section.
        text (str): Text of the step.
    """

    step_number: int
    text: str


class RecipeInstructionSection(TypedDict):
    """One numbered section of the instructions.

    Attributes:
        section_number (int): Number of the section.
        section (str): Title of the section.
        steps (list[RecipeInstructionStep]): Steps of the section.
    """

    section_number: int
    section: str
    steps: list[RecipeInstructionStep]


class Recipe(TypedDict):
    """A single recipe as stored in a recipe JSON file.

    Attributes:
        title (str): Title of the recipe.
        description (str): Short description of the recipe.
        servings (int): Number of servings.
        colors (RecipeColors): Color settings of the recipe.
        ingredients (list[RecipeIngredient]): Ingredient categories.
        instructions (list[RecipeInstructionSection]): Instruction sections.
        cover_image (NotRequired[str]): Path to the cover image, when present.
    """

    title: str
    description: str
    servings: int
    colors: RecipeColors
    ingredients: list[RecipeIngredient]
    instructions: list[RecipeInstructionSection]
    cover_image: NotRequired[str]
