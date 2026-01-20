"""
Base class for reverse converters in AI-Ready File Converter.
These converters transform AI-friendly formats (like Markdown) back to document formats.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class ReverseConverter(ABC):
    """Abstract base class for reverse converters (e.g., MD to DOCX)."""
    
    def __init__(self, file_path: Path):
        """
        Initialize the reverse converter with a file path.
        
        Args:
            file_path: Path to the source file
        """
        self.file_path = file_path
        self.filename = file_path.name
        self._source_content = None
    
    @abstractmethod
    def _get_source_type(self) -> str:
        """Return the human-readable source file type name."""
        pass
    
    @abstractmethod
    def _get_target_type(self) -> str:
        """Return the human-readable target file type name."""
        pass
    
    @abstractmethod
    def _get_target_extension(self) -> str:
        """Return the target file extension (e.g., '.docx')."""
        pass
    
    @abstractmethod
    def _parse_source(self) -> Any:
        """
        Parse the source file content.
        
        Returns:
            Parsed content structure
        """
        pass
    
    @abstractmethod
    def _generate_output(self, parsed_content: Any) -> bytes:
        """
        Generate the target document from parsed content.
        
        Args:
            parsed_content: The parsed source content
            
        Returns:
            Binary content of the target document
        """
        pass
    
    def convert(self) -> bytes:
        """
        Convert the source file to the target format.
        
        Returns:
            Binary content of the converted document
        """
        parsed = self._parse_source()
        return self._generate_output(parsed)
    
    def get_output_filename(self) -> str:
        """
        Get the output filename with appropriate extension.
        
        Returns:
            Filename with new extension (original_converted.ext)
        """
        stem = self.file_path.stem
        ext = self._get_target_extension()
        return f"{stem}_converted{ext}"
    
    def is_binary_output(self) -> bool:
        """
        Check if the output is binary (non-text).
        
        Returns:
            True if output is binary, False if text
        """
        return True  # Most reverse conversions produce binary output
