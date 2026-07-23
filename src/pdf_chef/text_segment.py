"""Data models used when composing PDF content."""

from dataclasses import dataclass


@dataclass
class TextSegment:
    """A single indented line of text within a structured text block.

    Attributes:
        text (str): The text content of the segment.
        indent (float): Horizontal indentation of the segment, in points.
            Defaults to 0.0.
        space_before (float): Extra vertical space above the segment, in points.
        font_name (str | None): Optional font name override for this segment.
        font_size (int | None): Optional font size override for this segment.
    """

    text: str
    indent: float = 0.0
    space_before: float = 0.0
    font_name: str | None = None
    font_size: int | None = None
