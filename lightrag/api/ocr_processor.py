"""OCR processor for scanned PDFs using Google Cloud Vision API.

Fallback for PDFs where pypdf extracts no text (scanned/image-only).
"""

import logging
from functools import lru_cache
from io import BytesIO

logger = logging.getLogger("lightrag")


def classify_pdf(file_bytes: bytes, sample_pages: int = 3) -> str:
    """Pre-flight scan detection using pypdf resource inspection.

    Checks first N pages for font and image resources.
    Returns: 'text' | 'scanned' | 'mixed' | 'unknown'
    """
    from pypdf import PdfReader

    try:
        reader = PdfReader(BytesIO(file_bytes))
        total = len(reader.pages)
        pages = reader.pages[: min(sample_pages, total)]

        verdicts = []
        for page in pages:
            res = page.get("/Resources")
            if res is None:
                verdicts.append("unknown")
                continue

            fonts = res.get("/Font", {})
            xobjects = res.get("/XObject", {})
            images = [
                v
                for v in (xobjects or {}).values()
                if hasattr(v, "get") and v.get("/Subtype") == "/Image"
            ]

            if images and not fonts:
                verdicts.append("scanned")
            elif fonts:
                verdicts.append("text")
            else:
                verdicts.append("unknown")

        if all(v == "scanned" for v in verdicts):
            return "scanned"
        if all(v == "text" for v in verdicts):
            return "text"
        if "scanned" in verdicts and "text" in verdicts:
            return "mixed"
        return "unknown"
    except Exception:
        return "unknown"


@lru_cache(maxsize=1)
def is_ocr_available() -> bool:
    """Check if Google Cloud Vision and pdf2image are installed."""
    try:
        from google.cloud import vision  # noqa: F401
        from pdf2image import convert_from_bytes  # noqa: F401

        return True
    except ImportError:
        return False


def ocr_pdf(file_bytes: bytes) -> str:
    """Extract text from a scanned PDF using Google Cloud Vision.

    Args:
        file_bytes: PDF file content as bytes

    Returns:
        str: OCR-extracted text, concatenated across all pages

    Raises:
        Exception: If OCR fails or returns no text
    """
    from google.cloud import vision
    from pdf2image import convert_from_bytes

    images = convert_from_bytes(file_bytes, dpi=300)

    client = vision.ImageAnnotatorClient()
    all_text = []

    for i, page_image in enumerate(images):
        img_buffer = BytesIO()
        page_image.save(img_buffer, format="PNG")
        img_bytes = img_buffer.getvalue()

        image = vision.Image(content=img_bytes)
        response = client.document_text_detection(image=image)

        if response.error.message:
            logger.warning(f"[OCR] Error on page {i + 1}: {response.error.message}")
            continue

        if response.full_text_annotation:
            all_text.append(response.full_text_annotation.text)

    if not all_text:
        raise Exception("OCR produced no text from scanned PDF")

    return "\n".join(all_text)
