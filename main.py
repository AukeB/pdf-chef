"""Main module"""

from src.mobile_recipe_builder import RecipePDFBuilder


def main():
    """
    Main function    
    """
    recipe_pdf_builder = RecipePDFBuilder()
    recipe_pdf_builder.build()

if __name__ == "__main__":
    main()
