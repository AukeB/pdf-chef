from typing import Any

import pytest
from pydantic import ValidationError

from pdf_chef.config.config_model import ConfigModel


# Testing the "ConfigModel" class.


def test_config_model_normalizes_255_colors(raw_config: dict[str, Any]) -> None:
    """RGB colors given as 0-255 values are stored as 0-1 tuples."""

    config = ConfigModel(**raw_config)

    assert config.colors.line_color == (0.0, 0.0, 0.0)
    assert config.toc.title_font.background_color == pytest.approx(
        (199 / 255, 140 / 255, 50 / 255)
    )


def test_config_model_rejects_unknown_nested_key(raw_config: dict[str, Any]) -> None:
    """An undeclared key inside a nested section fails validation."""

    raw_config["page"]["height"] = 100

    with pytest.raises(ValidationError):
        ConfigModel(**raw_config)
