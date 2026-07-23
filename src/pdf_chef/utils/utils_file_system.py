"""Module with file-system utility functions."""

import json
import os

from pathlib import Path


def load_json_file(file_path: str | Path) -> dict:
    """Load a JSON file and return its contents as a dictionary.

    Args:
        file_path (str | Path): Path to the JSON file to load.

    Returns:
        dict: The parsed contents of the JSON file.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def ensure_directory(file_path: str | Path) -> None:
    """Create the parent dictionary of a file path if it does not exist.

    Args:
        file_path (str | Path): Path to a file whose parent directory should
            exist.
    """
    directory_path = Path(file_path).parent
    os.makedirs(directory_path, exist_ok=True)
