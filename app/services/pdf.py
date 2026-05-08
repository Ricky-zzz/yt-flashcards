"""Service for extracting text from PDF files."""
from pathlib import Path

from pypdf import PdfReader


def extract_pdf_text(file_path: Path, max_pages: int | None = None) -> str:
    """Extract text content from a PDF file."""
    reader = PdfReader(str(file_path))
    if max_pages is not None and len(reader.pages) > max_pages:
        raise ValueError(f"PDF has too many pages (max {max_pages})")
    text_parts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        if page_text:
            text_parts.append(page_text)
    return "\n".join(text_parts).strip()
