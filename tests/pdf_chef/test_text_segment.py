from pdf_chef.text_segment import TextSegment


# Testing the "TextSegment" class.


def test_text_segment_defaults() -> None:
    """Only the text is required; the other fields have neutral defaults."""

    segment = TextSegment(text="Snijd de ui.")

    assert segment.indent == 0.0
    assert segment.space_before == 0.0
    assert segment.font_name is None
    assert segment.font_size is None
