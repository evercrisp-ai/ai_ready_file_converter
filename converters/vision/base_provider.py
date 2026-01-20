"""
Abstract base class for Vision AI providers.
All provider implementations must inherit from this class.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from pathlib import Path


@dataclass
class ImageAnalysisResult:
    """Result of image analysis from a Vision AI provider."""
    
    success: bool
    analysis: Optional[dict] = None
    error: Optional[str] = None
    provider_name: str = ""
    model_used: str = ""
    
    def to_dict(self) -> dict:
        """Convert result to dictionary for JSON serialization."""
        result = {
            "success": self.success,
            "provider": self.provider_name,
            "model": self.model_used,
        }
        if self.success and self.analysis:
            result["analysis"] = self.analysis
        if self.error:
            result["error"] = self.error
        return result


class BaseVisionProvider(ABC):
    """Abstract base class for Vision AI providers."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the vision provider.
        
        Args:
            api_key: API key for the provider. If None, will attempt to read from environment.
        """
        self.api_key = api_key or self._get_api_key_from_env()
        self._validate_api_key()
    
    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the name of this provider."""
        pass
    
    @property
    @abstractmethod
    def default_model(self) -> str:
        """Return the default model to use."""
        pass
    
    @abstractmethod
    def _get_api_key_from_env(self) -> Optional[str]:
        """Get the API key from environment variables."""
        pass
    
    def _validate_api_key(self) -> None:
        """Validate that an API key is available."""
        if not self.api_key:
            raise ValueError(
                f"No API key provided for {self.provider_name}. "
                f"Set the appropriate environment variable or pass api_key parameter."
            )
    
    @abstractmethod
    def analyze_image(
        self,
        image_path: Path,
        prompt: str,
        model: Optional[str] = None,
    ) -> ImageAnalysisResult:
        """
        Analyze an image and return structured description.
        
        Args:
            image_path: Path to the image file
            prompt: The analysis prompt to use
            model: Optional specific model to use (defaults to provider's default)
            
        Returns:
            ImageAnalysisResult with the analysis data or error information
        """
        pass
    
    def _encode_image_base64(self, image_path: Path) -> str:
        """Encode an image file to base64."""
        import base64
        
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    
    def _get_mime_type(self, image_path: Path) -> str:
        """Get the MIME type for an image file."""
        suffix = image_path.suffix.lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".webp": "image/webp",
        }
        return mime_types.get(suffix, "image/png")
    
    def is_available(self) -> bool:
        """Check if this provider is available (has valid API key)."""
        return bool(self.api_key)
