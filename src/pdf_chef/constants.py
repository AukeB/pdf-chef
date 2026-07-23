"""Project-wide constants."""

# Height of the working canvas before the empty bottom space is cropped away.
# Kept below the PDF spec limit of 14400 points (~5080 mm) so the intermediate
# document stays valid; the final page is cropped down to fit the content
WORKING_PAGE_HEIGHT_MM: int = 5000  # Units: mm.
