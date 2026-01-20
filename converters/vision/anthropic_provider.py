"""
Anthropic Vision provider implementation.
Uses Claude Vision models (claude-3-sonnet, claude-3-opus, etc.) for image analysis.
"""

import os
import json
from pathlib import Path
from typing import Optional

from .base_provider import BaseVisionProvider, ImageAnalysisResult
from .analysis_prompt import get_analysis_prompt


class AnthropicVisionProvider(BaseVisionProvider):
    """Vision provider using Anthropic's Claude Vision models."""
    
    @property
    def provider_name(self) -> str:
        return "anthropic"
    
    @property
    def default_model(self) -> str:
        return "claude-3-5-sonnet-20241022"
    
    def _get_api_key_from_env(self) -> Optional[str]:
        return os.environ.get("ANTHROPIC_API_KEY")
    
    def analyze_image(
        self,
        image_path: Path,
        prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> ImageAnalysisResult:
        """
        Analyze an image using Anthropic's Claude Vision API.
        
        Args:
            image_path: Path to the image file
            prompt: The analysis prompt (defaults to comprehensive prompt)
            model: Model to use (defaults to claude-3-5-sonnet)
            
        Returns:
            ImageAnalysisResult with structured analysis
        """
        try:
            import anthropic
        except ImportError:
            return ImageAnalysisResult(
                success=False,
                error="Anthropic library not installed. Run: pip install anthropic",
                provider_name=self.provider_name,
                model_used=model or self.default_model,
            )
        
        model = model or self.default_model
        prompt = prompt or get_analysis_prompt()
        
        try:
            # Encode image to base64
            base64_image = self._encode_image_base64(image_path)
            mime_type = self._get_mime_type(image_path)
            
            # Create Anthropic client
            client = anthropic.Anthropic(api_key=self.api_key)
            
            # Make the API call
            response = client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": mime_type,
                                    "data": base64_image,
                                },
                            },
                            {
                                "type": "text",
                                "text": prompt,
                            },
                        ],
                    }
                ],
            )
            
            # Extract the response content
            content = response.content[0].text
            
            # Parse the JSON response
            analysis = self._parse_json_response(content)
            
            return ImageAnalysisResult(
                success=True,
                analysis=analysis,
                provider_name=self.provider_name,
                model_used=model,
            )
            
        except json.JSONDecodeError as e:
            return ImageAnalysisResult(
                success=False,
                error=f"Failed to parse JSON response: {str(e)}",
                provider_name=self.provider_name,
                model_used=model,
            )
        except Exception as e:
            return ImageAnalysisResult(
                success=False,
                error=f"Anthropic API error: {str(e)}",
                provider_name=self.provider_name,
                model_used=model,
            )
    
    def _parse_json_response(self, content: str) -> dict:
        """Parse JSON from the response, handling potential markdown formatting."""
        # Clean up the response - remove markdown code blocks if present
        content = content.strip()
        
        # Remove markdown code block markers
        if content.startswith("```json"):
            content = content[7:]
        elif content.startswith("```"):
            content = content[3:]
        
        if content.endswith("```"):
            content = content[:-3]
        
        content = content.strip()
        
        # Parse JSON
        return json.loads(content)
