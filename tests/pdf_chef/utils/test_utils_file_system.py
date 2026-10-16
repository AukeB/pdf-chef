import json
from pathlib import Path

from pdf_chef.utils.utils_file_system import ensure_directory, load_json_file


# Testing the "load_json_file" function.


def test_load_json_file_returns_parsed_contents(tmp_path: Path) -> None:
    """The parsed JSON content is returned as a dictionary."""

    json_path = tmp_path / "recipe.json"
    json_path.write_text(json.dumps({"title": "Soep", "servings": 2}), encoding="utf-8")

    json_data = load_json_file(file_path=json_path)

    assert json_data == {"title": "Soep", "servings": 2}


def test_load_json_file_reads_utf8(tmp_path: Path) -> None:
    """Non-ASCII characters are read correctly."""

    json_path = tmp_path / "recipe.json"
    json_path.write_text(json.dumps({"text": "← Alle recepten"}), encoding="utf-8")

    json_data = load_json_file(file_path=json_path)

    assert json_data["text"] == "← Alle recepten"


# Testing the "ensure_directory" function.


def test_ensure_directory_creates_parent_folder(tmp_path: Path) -> None:
    """The parent folder of the file path is created."""

    file_path = tmp_path / "nested" / "folder" / "out.pdf"

    ensure_directory(file_path=file_path)

    assert file_path.parent.is_dir()


def test_ensure_directory_is_safe_when_folder_exists(tmp_path: Path) -> None:
    """Calling the function on an existing folder does not raise."""

    file_path = tmp_path / "out.pdf"

    ensure_directory(file_path=file_path)
    ensure_directory(file_path=file_path)

    assert tmp_path.is_dir()
