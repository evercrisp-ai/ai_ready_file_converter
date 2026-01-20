"""
Google Gemini Vision provider implementation.
Uses Gemini Pro Vision models for image analysis.
"""

import os
import json
from pathlib import Path
from typing import Optional

from .base_provider import BaseVisionProvider, ImageAnalysisResult
from .analysis_prompt import get_analysis_prompt


class GeminiVisionProvider(BaseVisionProvider):
    """Vision provider using Google's Gemini Vision models."""
    
    @property
    def provider_name(self) -> str:
        return "gemini"
    
    @property
    def default_model(self) -> str:
        return "gemini-1.5-pro"
    
    def _get_api_key_from_env(self) -> Optional[str]:
        return os.environ.get("GOOGLE_API_KEY")
    
    def analyze_image(
        self,
        image_path: Path,
        prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> ImageAnalysisResult:
        """
        Analyze an image using Google's Gemini Vision API.
        
        Args:
            image_path: Path to the image file
            prompt: The analysis prompt (defaults to comprehensive prompt)
            model: Model to use (defaults to gemini-1.5-pro)
            
        Returns:
            ImageAnalysisResult with structured analysis
        """
        try:
            import google.generativeai as genai
        except ImportError:
            return ImageAnalysisResult(
                success=False,
                error="Google Generative AI library not installed. Run: pip install google-generativeai",
                provider_name=self.provider_name,
                model_used=model or self.default_model,
            )
        
        model_name = model or self.default_model
        prompt = prompt or get_analysis_prompt()
        
        try:
            # Configure the API key
            genai.configure(api_key=self.api_key)
            
            # Load the image
            from PIL import Image
            img = Image.open(image_path)
            
            # Create the model
            gemini_model = genai.GenerativeModel(model_name)
            
            # Configure generation settings for precise output
            generation_config = genai.types.GenerationConfig(
                temperature=0.1,
                max_output_tokens=4096,
            )
            
            # Make the API call
            response = gemini_model.generate_content(
                [prompt, img],
                generation_config=generation_config,
            )
            
            # Extract the response content
            content = response.text
            
            # Parse the JSON response
            analysis = self._parse_json_response(content)
            
            return ImageAnalysisResult(
                success=True,
                analysis=analysis,
                provider_name=self.provider_name,
                model_used=model_name,
            )
            
        except json.JSONDecodeError as e:
            return ImageAnalysisResult(
                success=False,
                error=f"Failed to parse JSON response: {str(e)}",
                provider_name=self.provider_name,
                model_used=model_name,
            )
        except Exception as e:
            return ImageAnalysisResult(
                success=False,
                error=f"Gemini API error: {str(e)}",
                provider_name=self.provider_name,
                model_used=model_name,
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
