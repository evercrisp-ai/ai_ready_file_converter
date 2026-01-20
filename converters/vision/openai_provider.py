"""
OpenAI Vision provider implementation.
Uses GPT-4 Vision (gpt-4-vision-preview or gpt-4o) for image analysis.
"""

import os
import json
from pathlib import Path
from typing import Optional

from .base_provider import BaseVisionProvider, ImageAnalysisResult
from .analysis_prompt import get_analysis_prompt


class OpenAIVisionProvider(BaseVisionProvider):
    """Vision provider using OpenAI's GPT-4 Vision models."""
    
    @property
    def provider_name(self) -> str:
        return "openai"
    
    @property
    def default_model(self) -> str:
        return "gpt-4o"
    
    def _get_api_key_from_env(self) -> Optional[str]:
        return os.environ.get("OPENAI_API_KEY")
    
    def analyze_image(
        self,
        image_path: Path,
        prompt: Optional[str] = None,
        model: Optional[str] = None,
    ) -> ImageAnalysisResult:
        """
        Analyze an image using OpenAI's Vision API.
        
        Args:
            image_path: Path to the image file
            prompt: The analysis prompt (defaults to comprehensive prompt)
            model: Model to use (defaults to gpt-4o)
            
        Returns:
            ImageAnalysisResult with structured analysis
        """
        try:
            from openai import OpenAI
        except ImportError:
            return ImageAnalysisResult(
                success=False,
                error="OpenAI library not installed. Run: pip install openai",
                provider_name=self.provider_name,
                model_used=model or self.default_model,
            )
        
        model = model or self.default_model
        prompt = prompt or get_analysis_prompt()
        
        try:
            # Encode image to base64
            base64_image = self._encode_image_base64(image_path)
            mime_type = self._get_mime_type(image_path)
            
            # Create OpenAI client
            client = OpenAI(api_key=self.api_key)
            
            # Make the API call
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt,
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{mime_type};base64,{base64_image}",
                                    "detail": "high",
                                },
                            },
                        ],
                    }
                ],
                max_tokens=4096,
                temperature=0.1,  # Low temperature for consistent, precise output
            )
            
            # Extract the response content
            content = response.choices[0].message.content
            
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
                error=f"OpenAI API error: {str(e)}",
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
