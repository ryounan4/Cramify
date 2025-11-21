"""
PDF processing utilities.

Handles conversion of PDF files to images for OCR/vision processing.
"""

from typing import List

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

DPI = 300  # Image resolution for OCR


def pdf_to_images(pdf_bytes: bytes, dpi: int = DPI) -> List[bytes]:
    """
    Render PDF pages to PNG images for OCR.

    Args:
        pdf_bytes: PDF file bytes
        dpi: Resolution (300 recommended for OCR quality)

    Returns:
        List of PNG image bytes

    Raises:
        ImportError: If PyMuPDF is not installed
    """
    if fitz is None:
        raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []

    matrix = fitz.Matrix(dpi / 72, dpi / 72)

    for page in doc:
        pix = page.get_pixmap(matrix=matrix, alpha=False)
        png_bytes = pix.tobytes("png")
        images.append(png_bytes)

    doc.close()
    return images


def count_pdf_pages(pdf_bytes: bytes) -> int:
    """
    Count the number of pages in a PDF.

    Args:
        pdf_bytes: PDF file bytes

    Returns:
        Number of pages

    Raises:
        ImportError: If PyMuPDF is not installed
    """
    if fitz is None:
        raise ImportError("PyMuPDF not installed. Run: pip install pymupdf")

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    page_count = len(doc)
    doc.close()
    return page_count
