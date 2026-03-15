"""Arrange compiled components onto A4 pages as a print-ready PDF."""

from __future__ import annotations

import math
from pathlib import Path

from fpdf import FPDF

# Physical sizes in mm (Spirit Island standard)
CARD_WIDTH_MM = 63.5
CARD_HEIGHT_MM = 88.0
BOARD_WIDTH_MM = 228.0
BOARD_HEIGHT_MM = 152.0

# A4 in mm
A4_WIDTH_MM = 210.0
A4_HEIGHT_MM = 297.0

# Spacing between cards in mm
CARD_SPACING_MM = 5.0

# Cards per page in landscape A4: 3 columns × 2 rows (with spacing)
CARD_COLS = 3
CARD_ROWS = 2
CARDS_PER_PAGE = CARD_COLS * CARD_ROWS


def _classify_files(output_dir: Path) -> dict[str, list[Path]]:
    """Classify PNG files in the output directory by component type.

    Only includes PNGs that have a matching HTML file (i.e., compiled components).
    """
    result: dict[str, list[Path]] = {
        "board_front": [],
        "board_lore": [],
        "card_back": [],
        "cards": [],
    }

    for png in sorted(output_dir.glob("*.png")):
        # Only include compiled components (those with a matching .html)
        html = png.with_suffix(".html")
        if not html.exists():
            continue

        name = png.stem
        if name.endswith("-front"):
            result["board_front"].append(png)
        elif name.endswith("-lore"):
            result["board_lore"].append(png)
        elif "card-back" in name:
            result["card_back"].append(png)
        else:
            result["cards"].append(png)

    return result


def _add_card_page(pdf: FPDF, cards: list[Path]) -> None:
    """Add a landscape A4 page with cards arranged in a grid with spacing."""
    pdf.add_page(orientation="L")

    # In landscape, page is 297mm wide × 210mm tall
    page_w = A4_HEIGHT_MM
    page_h = A4_WIDTH_MM

    # Center the grid (including spacing) on the page
    grid_width = CARD_COLS * CARD_WIDTH_MM + (CARD_COLS - 1) * CARD_SPACING_MM
    grid_height = CARD_ROWS * CARD_HEIGHT_MM + (CARD_ROWS - 1) * CARD_SPACING_MM
    x_offset = (page_w - grid_width) / 2
    y_offset = (page_h - grid_height) / 2

    for i, card_path in enumerate(cards):
        col = i % CARD_COLS
        row = i // CARD_COLS
        x = x_offset + col * (CARD_WIDTH_MM + CARD_SPACING_MM)
        y = y_offset + row * (CARD_HEIGHT_MM + CARD_SPACING_MM)
        pdf.image(str(card_path), x=x, y=y, w=CARD_WIDTH_MM, h=CARD_HEIGHT_MM)


def _add_card_back_page(pdf: FPDF, card_back: Path, count: int) -> None:
    """Add a landscape A4 page with card backs mirrored for double-sided printing."""
    pdf.add_page(orientation="L")

    # In landscape, page is 297mm wide × 210mm tall
    page_w = A4_HEIGHT_MM
    page_h = A4_WIDTH_MM

    grid_width = CARD_COLS * CARD_WIDTH_MM + (CARD_COLS - 1) * CARD_SPACING_MM
    grid_height = CARD_ROWS * CARD_HEIGHT_MM + (CARD_ROWS - 1) * CARD_SPACING_MM
    x_offset = (page_w - grid_width) / 2
    y_offset = (page_h - grid_height) / 2

    # Mirror horizontally: columns go right-to-left so backs align with fronts
    for i in range(count):
        col = i % CARD_COLS
        row = i // CARD_COLS
        mirrored_col = (CARD_COLS - 1) - col
        x = x_offset + mirrored_col * (CARD_WIDTH_MM + CARD_SPACING_MM)
        y = y_offset + row * (CARD_HEIGHT_MM + CARD_SPACING_MM)
        pdf.image(str(card_back), x=x, y=y, w=CARD_WIDTH_MM, h=CARD_HEIGHT_MM)


def _add_board_page(pdf: FPDF, board_path: Path) -> None:
    """Add a landscape A4 page with a spirit board at exact size, centered."""
    pdf.add_page(orientation="L")

    # In landscape, page is 297mm wide × 210mm tall
    page_w = A4_HEIGHT_MM
    page_h = A4_WIDTH_MM

    x = (page_w - BOARD_WIDTH_MM) / 2
    y = (page_h - BOARD_HEIGHT_MM) / 2

    pdf.image(str(board_path), x=x, y=y, w=BOARD_WIDTH_MM, h=BOARD_HEIGHT_MM)


def generate_print_layout(output_dir: Path, pdf_path: Path) -> Path:
    """Generate a print-ready A4 PDF from compiled component PNGs.

    Page order:
    1. Spirit board front (landscape)
    2. Spirit board lore (landscape)
    3. Card fronts page (portrait, 3×3 grid)
    4. Card backs page (portrait, mirrored for double-sided)
    ... repeat 3-4 if more than 9 cards

    Returns the path to the generated PDF.
    """
    files = _classify_files(output_dir)

    pdf = FPDF(unit="mm")
    pdf.set_auto_page_break(auto=False)

    # Board front
    for board in files["board_front"]:
        _add_board_page(pdf, board)

    # Board lore
    for board in files["board_lore"]:
        _add_board_page(pdf, board)

    # Cards: interleave front pages with back pages
    cards = files["cards"]
    card_back = files["card_back"][0] if files["card_back"] else None

    if cards:
        num_pages = math.ceil(len(cards) / CARDS_PER_PAGE)
        for page_idx in range(num_pages):
            start = page_idx * CARDS_PER_PAGE
            end = min(start + CARDS_PER_PAGE, len(cards))
            page_cards = cards[start:end]

            # Front page
            _add_card_page(pdf, page_cards)

            # Back page (mirrored)
            if card_back:
                _add_card_back_page(pdf, card_back, len(page_cards))

    pdf.output(str(pdf_path))
    return pdf_path
