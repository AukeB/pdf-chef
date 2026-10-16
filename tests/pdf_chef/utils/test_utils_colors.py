from pdf_chef.utils.utils_colors import normalize_rgb


# Testing the "normalize_rgb" function.


def test_normalize_rgb_scales_tuple_to_unit_range() -> None:
    """A 0-255 tuple is scaled to a 0-1 tuple."""

    normalized_color = normalize_rgb((255, 0, 51))

    assert normalized_color == (1.0, 0.0, 0.2)


def test_normalize_rgb_accepts_list() -> None:
    """A list with three components is normalized like a tuple."""

    normalized_color = normalize_rgb([0, 255, 0])

    assert normalized_color == (0.0, 1.0, 0.0)


def test_normalize_rgb_returns_value_unchanged_when_not_three_components() -> None:
    """Sequences that are not three components are returned as they are."""

    value = [1, 2]

    normalized_color = normalize_rgb(value)

    assert normalized_color is value


def test_normalize_rgb_returns_non_sequence_unchanged() -> None:
    """Non-sequence values are returned as they are."""

    normalized_color = normalize_rgb("red")

    assert normalized_color == "red"
