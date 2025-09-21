"""Main module"""
from pathlib import Path

from src.config_manager import ConfigManager
from src.mobile_recipe_build import RecipePDFBuilder

def main():
    """
    Main function
    """
    config_path_mobile_recipes = Path("src/configs/config_mobile_recipes.yaml")

    config_manager = ConfigManager()
    config_mobile_recipes = config_manager.load_config_file(path=config_path_mobile_recipes)

    recipe_pdf_builder = RecipePDFBuilder(config=config_mobile_recipes)
    recipe_pdf_builder.build()

if __name__ == "__main__":
    main()
