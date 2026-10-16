"""Module with file-system utility functions."""

import json
import os

from pathlib import Path
from typing import Any


def load_json_file(file_path: str | Path) -> dict[str, Any]:
    """Load a JSON file and return its contents as a dictionary.

    Args:
        file_path (str | Path): Path to the JSON file to load.

    Returns:
        json_data (dict[str, Any]): The parsed contents of the JSON file. The
            shape is only known to the caller, so it is left generic here.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    return json_data


def ensure_directory(file_path: str | Path) -> None:
    """Create the parent directory of a file path if it does not exist.

    Args:
        file_path (str | Path): Path to a file whose parent directory should
            exist.
    """
    directory_path = Path(file_path).parent
    os.makedirs(directory_path, exist_ok=True)
