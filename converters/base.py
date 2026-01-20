"""
Base converter class for AI-Ready File Converter.
All specific converters inherit from this class.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timezone
from pathlib import Path
import json


class BaseConverter(ABC):
    """Abstract base class for all file converters."""
    
    def __init__(self, file_path: Path):
        """
        Initialize the converter with a file path.
        
        Args:
            file_path: Path to the source file
        """
        self.file_path = file_path
        self.filename = file_path.name
        self.file_type = self._get_file_type()
        self._content = None
        self._metadata = {}
    
    @abstractmethod
    def _get_file_type(self) -> str:
        """Return the human-readable file type name."""
        pass
    
    @abstractmethod
    def _extract_content(self) -> dict:
        """
        Extract content from the source file.
        
        Returns:
            Dictionary containing extracted content
        """
        pass
    
    @abstractmethod
    def _format_as_markdown(self, content: dict) -> str:
        """
        Format extracted content as Markdown.
        
        Args:
            content: Dictionary of extracted content
            
        Returns:
            Markdown-formatted string
        """
        pass
    
    def _build_json_structure(self, content: dict) -> dict:
        """
        Build the standard JSON output structure.
        
        Args:
            content: Dictionary of extracted content
            
        Returns:
            Standardized JSON structure
        """
        return {
            "source": {
                "filename": self.filename,
                "type": self.file_type,
                "converted_at": datetime.now(timezone.utc).isoformat()
            },
            "content": content,
            "metadata": self._metadata
        }
    
    def convert(self) -> dict:
        """
        Extract and cache content from the source file.
        
        Returns:
            Dictionary containing extracted content
        """
        if self._content is None:
            self._content = self._extract_content()
        return self._content
    
    def to_markdown(self) -> str:
        """
        Convert the file to Markdown format.
        
        Returns:
            Markdown-formatted string
        """
        content = self.convert()
        
        # Add header with source info
        header = f"# {self.filename}\n\n"
        header += f"> Converted from {self.file_type} on {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}\n\n"
        header += "---\n\n"
        
        body = self._format_as_markdown(content)
        
        return header + body
    
    def to_json(self) -> str:
        """
        Convert the file to JSON format.
        
        Returns:
            JSON-formatted string
        """
        content = self.convert()
        json_structure = self._build_json_structure(content)
        return json.dumps(json_structure, indent=2, ensure_ascii=False)
    
    def get_output(self, format: str = 'md') -> str:
        """
        Get the converted output in the specified format.
        
        Args:
            format: Output format ('md' or 'json')
            
        Returns:
            Converted content as string
        """
        if format.lower() == 'json':
            return self.to_json()
        return self.to_markdown()
    
    def get_output_filename(self, format: str = 'md') -> str:
        """
        Get the output filename with appropriate extension.
        
        Args:
            format: Output format ('md' or 'json')
            
        Returns:
            Filename with new extension (original_AI_converter.ext)
        """
        stem = self.file_path.stem
        ext = '.json' if format.lower() == 'json' else '.md'
        return f"{stem}_AI_converter{ext}"
