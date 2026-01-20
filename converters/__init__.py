"""
Converter registry for AI-Ready File Converter.
Maps file extensions to their appropriate converter classes.
"""
from __future__ import annotations

from .base import BaseConverter
from .docx_converter import DocxConverter
from .pdf_converter import PdfConverter
from .pptx_converter import PptxConverter
from .xlsx_converter import XlsxConverter
from .image_converter import ImageConverter
from .reverse import MarkdownToDocxConverter

# Registry mapping file extensions to converter classes
CONVERTER_REGISTRY = {
    # Documents
    '.docx': DocxConverter,
    '.doc': DocxConverter,
    '.pdf': PdfConverter,
    '.pptx': PptxConverter,
    '.ppt': PptxConverter,
    # Spreadsheets
    '.xlsx': XlsxConverter,
    '.xls': XlsxConverter,
    '.csv': XlsxConverter,
    # Images
    '.png': ImageConverter,
    '.jpg': ImageConverter,
    '.jpeg': ImageConverter,
    '.gif': ImageConverter,
    '.bmp': ImageConverter,
    '.tiff': ImageConverter,
    '.tif': ImageConverter,
    '.webp': ImageConverter,
    # Markdown (reverse conversion)
    '.md': MarkdownToDocxConverter,
    '.markdown': MarkdownToDocxConverter,
}

# Default output formats for each file type
DEFAULT_OUTPUT_FORMATS = {
    '.docx': 'md',
    '.doc': 'md',
    '.pdf': 'md',
    '.pptx': 'md',
    '.ppt': 'md',
    '.xlsx': 'json',
    '.xls': 'json',
    '.csv': 'json',
    '.png': 'json',
    '.jpg': 'json',
    '.jpeg': 'json',
    '.gif': 'json',
    '.bmp': 'json',
    '.tiff': 'json',
    '.tif': 'json',
    '.webp': 'json',
    '.md': 'docx',
    '.markdown': 'docx',
}

def get_converter(extension: str) -> type[BaseConverter] | None:
    """Get the converter class for a given file extension."""
    return CONVERTER_REGISTRY.get(extension.lower())

def get_default_format(extension: str) -> str:
    """Get the default output format for a given file extension."""
    return DEFAULT_OUTPUT_FORMATS.get(extension.lower(), 'md')

def get_supported_extensions() -> list[str]:
    """Get list of all supported file extensions."""
    return list(CONVERTER_REGISTRY.keys())

def is_reverse_converter(extension: str) -> bool:
    """Check if the extension uses a reverse converter (binary output)."""
    converter_class = CONVERTER_REGISTRY.get(extension.lower())
    if converter_class is None:
        return False
    # Check if it's a reverse converter by checking the module
    return 'reverse' in converter_class.__module__


__all__ = [
    'BaseConverter',
    'DocxConverter',
    'PdfConverter',
    'PptxConverter',
    'XlsxConverter',
    'ImageConverter',
    'MarkdownToDocxConverter',
    'CONVERTER_REGISTRY',
    'DEFAULT_OUTPUT_FORMATS',
    'get_converter',
    'get_default_format',
    'get_supported_extensions',
    'is_reverse_converter',
]
