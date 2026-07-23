"""Module with utility function related to colors."""

from typing import Sequence, cast


def normalize_rgb(value: object) -> object:
    """Normalize a 0-255 RGB color to a 0-1 RGB tuple.

    Args:
        value (object): A ``(red, green, blue)`` sequence with components in the
            range ``[0, 255]``, or any other value which is returned unchanged.

    Returns:
        object: A ``(red, green, blue)`` tuple with components in the range
            ``[0, 1]`` when ``value`` is a 3-element sequence, otherwise
            ``value`` unchanged.
    """
    if isinstance(value, (list, tuple)) and len(value) == 3:
        components = cast(Sequence[float], value)
        return tuple(component / 255 for component in components)
    return value
