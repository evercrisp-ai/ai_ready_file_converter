"""
Factory for creating Vision AI provider instances.
"""

import os
from typing import Optional, Type
from .base_provider import BaseVisionProvider


class VisionProviderFactory:
    """Factory class for creating vision provider instances."""
    
    _providers: dict[str, Type[BaseVisionProvider]] = {}
    
    @classmethod
    def register(cls, name: str, provider_class: Type[BaseVisionProvider]) -> None:
        """Register a provider class with the factory."""
        cls._providers[name.lower()] = provider_class
    
    @classmethod
    def get_provider(
        cls,
        provider_name: Optional[str] = None,
        api_key: Optional[str] = None,
    ) -> Optional[BaseVisionProvider]:
        """
        Get a vision provider instance.
        
        Args:
            provider_name: Name of the provider ('openai', 'anthropic', 'gemini').
                          If None, reads from VISION_PROVIDER env var, defaults to 'openai'.
            api_key: Optional API key to use. If None, provider will read from env.
            
        Returns:
            Configured provider instance, or None if provider unavailable.
        """
        # Determine which provider to use
        if provider_name is None:
            provider_name = os.environ.get("VISION_PROVIDER", "openai")
        
        provider_name = provider_name.lower()
        
        # Check if vision is enabled
        vision_enabled = os.environ.get("VISION_ENABLED", "true").lower()
        if vision_enabled == "false":
            return None
        
        # Get the provider class
        provider_class = cls._providers.get(provider_name)
        if provider_class is None:
            # Try to import and register the provider
            provider_class = cls._try_import_provider(provider_name)
        
        if provider_class is None:
            raise ValueError(
                f"Unknown vision provider: {provider_name}. "
                f"Available providers: {list(cls._providers.keys())}"
            )
        
        try:
            return provider_class(api_key=api_key)
        except ValueError as e:
            # API key not available
            return None
    
    @classmethod
    def _try_import_provider(cls, name: str) -> Optional[Type[BaseVisionProvider]]:
        """Try to import and register a provider by name."""
        try:
            if name == "openai":
                from .openai_provider import OpenAIVisionProvider
                cls.register("openai", OpenAIVisionProvider)
                return OpenAIVisionProvider
            elif name == "anthropic":
                from .anthropic_provider import AnthropicVisionProvider
                cls.register("anthropic", AnthropicVisionProvider)
                return AnthropicVisionProvider
            elif name == "gemini":
                from .gemini_provider import GeminiVisionProvider
                cls.register("gemini", GeminiVisionProvider)
                return GeminiVisionProvider
        except ImportError:
            pass
        return None
    
    @classmethod
    def list_available_providers(cls) -> list[str]:
        """List all available provider names."""
        available = []
        for name in ["openai", "anthropic", "gemini"]:
            try:
                provider = cls.get_provider(name)
                if provider is not None:
                    available.append(name)
            except (ValueError, ImportError):
                pass
        return available


def get_vision_provider(
    provider_name: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Optional[BaseVisionProvider]:
    """
    Convenience function to get a vision provider.
    
    Args:
        provider_name: Name of the provider ('openai', 'anthropic', 'gemini').
        api_key: Optional API key.
        
    Returns:
        Configured provider instance, or None if unavailable.
    """
    return VisionProviderFactory.get_provider(provider_name, api_key)
