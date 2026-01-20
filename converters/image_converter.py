"""
Image converter for AI-Ready File Converter.
Extracts text via OCR, provides Base64 encoding, and generates
hyper-detailed Vision AI analysis for near-identical reproduction.
"""

import os
from pathlib import Path
import base64
from io import BytesIO
from typing import Optional
from PIL import Image
from .base import BaseConverter

# Try to import pytesseract, handle gracefully if not available
try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

# Try to import vision module
try:
    from .vision import get_vision_provider
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False


class ImageConverter(BaseConverter):
    """Converter for image files with OCR, Base64 encoding, and Vision AI analysis."""
    
    def __init__(self, file_path: Path, vision_provider: Optional[str] = None):
        """
        Initialize the image converter.
        
        Args:
            file_path: Path to the source image file
            vision_provider: Optional vision provider name ('openai', 'anthropic', 'gemini')
        """
        self._vision_provider_name = vision_provider
        self._vision_analysis = None
        super().__init__(file_path)
    
    def _get_file_type(self) -> str:
        ext = self.file_path.suffix.lower()
        return f"image_{ext.replace('.', '')}"
    
    def _perform_vision_analysis(self) -> Optional[dict]:
        """
        Perform Vision AI analysis on the image.
        
        Returns:
            Analysis result dictionary or None if unavailable
        """
        if not VISION_AVAILABLE:
            return {
                "success": False,
                "error": "Vision module not available",
                "provider": None,
                "model": None,
            }
        
        # Check if vision is disabled
        vision_enabled = os.environ.get("VISION_ENABLED", "true").lower()
        if vision_enabled == "false":
            return {
                "success": False,
                "error": "Vision analysis disabled via VISION_ENABLED=false",
                "provider": None,
                "model": None,
            }
        
        try:
            provider = get_vision_provider(self._vision_provider_name)
            if provider is None:
                return {
                    "success": False,
                    "error": "No vision provider available. Set API key for your preferred provider.",
                    "provider": None,
                    "model": None,
                }
            
            # Perform analysis
            result = provider.analyze_image(self.file_path)
            return result.to_dict()
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Vision analysis failed: {str(e)}",
                "provider": None,
                "model": None,
            }
    
    def _extract_content(self) -> dict:
        """Extract content from image via OCR, Base64 encoding, and Vision AI."""
        content = {
            "ocr_text": "",
            "base64_data": "",
            "image_format": "",
            "dimensions": {},
            "vision_analysis": None,
        }
        
        # Open and process image
        with Image.open(self.file_path) as img:
            # Store image info
            content["image_format"] = img.format or self.file_path.suffix.upper().replace(".", "")
            content["dimensions"] = {
                "width": img.width,
                "height": img.height
            }
            
            # Convert to RGB if necessary (for OCR)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparent images
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img_for_ocr = background
            elif img.mode != 'RGB':
                img_for_ocr = img.convert('RGB')
            else:
                img_for_ocr = img
            
            # Perform OCR if available
            if TESSERACT_AVAILABLE:
                try:
                    ocr_text = pytesseract.image_to_string(img_for_ocr)
                    content["ocr_text"] = ocr_text.strip()
                except Exception as e:
                    content["ocr_text"] = f"[OCR Error: {str(e)}]"
                    content["ocr_error"] = str(e)
            else:
                content["ocr_text"] = "[OCR not available - Tesseract not installed]"
                content["ocr_available"] = False
            
            # Base64 encode the image
            # Use original format if possible, fallback to PNG
            buffer = BytesIO()
            save_format = img.format if img.format else 'PNG'
            
            # Handle format compatibility
            if save_format.upper() in ('JPEG', 'JPG'):
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')
                save_format = 'JPEG'
            
            try:
                img.save(buffer, format=save_format)
            except Exception:
                # Fallback to PNG
                img_rgb = img.convert('RGB') if img.mode not in ('RGB', 'L') else img
                img_rgb.save(buffer, format='PNG')
                save_format = 'PNG'
            
            buffer.seek(0)
            base64_data = base64.b64encode(buffer.read()).decode('utf-8')
            content["base64_data"] = base64_data
            content["base64_mime"] = f"image/{save_format.lower()}"
        
        # Perform Vision AI analysis
        content["vision_analysis"] = self._perform_vision_analysis()
        
        # Update metadata
        vision_result = content["vision_analysis"] or {}
        self._metadata = {
            "format": content["image_format"],
            "width": content["dimensions"]["width"],
            "height": content["dimensions"]["height"],
            "ocr_word_count": len(content["ocr_text"].split()) if content["ocr_text"] else 0,
            "base64_size_bytes": len(content["base64_data"]),
            "vision_analysis_success": vision_result.get("success", False),
            "vision_provider": vision_result.get("provider"),
            "vision_model": vision_result.get("model"),
        }
        
        return content
    
    def _format_as_markdown(self, content: dict) -> str:
        """Format image content as Markdown."""
        md_parts = []
        
        # Image info
        md_parts.append("## Image Information")
        md_parts.append("")
        md_parts.append(f"- **Format:** {content['image_format']}")
        md_parts.append(f"- **Dimensions:** {content['dimensions']['width']} x {content['dimensions']['height']} pixels")
        md_parts.append("")
        
        # Vision AI Analysis
        vision_analysis = content.get("vision_analysis", {})
        if vision_analysis and vision_analysis.get("success"):
            analysis = vision_analysis.get("analysis", {})
            
            md_parts.append("## AI Vision Analysis")
            md_parts.append("")
            md_parts.append(f"*Analyzed by: {vision_analysis.get('provider', 'unknown')} ({vision_analysis.get('model', 'unknown')})*")
            md_parts.append("")
            
            # Summary
            if analysis.get("summary"):
                md_parts.append("### Summary")
                md_parts.append("")
                md_parts.append(analysis["summary"])
                md_parts.append("")
            
            # Reproduction Prompt
            if analysis.get("reproduction_prompt"):
                md_parts.append("### Reproduction Prompt")
                md_parts.append("")
                md_parts.append("```")
                md_parts.append(analysis["reproduction_prompt"])
                md_parts.append("```")
                md_parts.append("")
            
            # Style
            if analysis.get("style"):
                style = analysis["style"]
                md_parts.append("### Style & Mood")
                md_parts.append("")
                if style.get("artistic_style"):
                    md_parts.append(f"- **Artistic Style:** {style['artistic_style']}")
                if style.get("mood"):
                    md_parts.append(f"- **Mood:** {style['mood']}")
                if style.get("atmosphere"):
                    md_parts.append(f"- **Atmosphere:** {style['atmosphere']}")
                md_parts.append("")
            
            # Colors
            if analysis.get("colors"):
                colors = analysis["colors"]
                md_parts.append("### Colors")
                md_parts.append("")
                if colors.get("dominant_colors"):
                    md_parts.append("**Dominant Colors:**")
                    for color in colors["dominant_colors"][:5]:
                        name = color.get("name", "unknown")
                        hex_code = color.get("hex", "#???")
                        pct = color.get("percentage", "?")
                        md_parts.append(f"- {name} ({hex_code}) - {pct}%")
                if colors.get("palette_type"):
                    md_parts.append(f"\n**Palette Type:** {colors['palette_type']}")
                md_parts.append("")
        elif vision_analysis:
            md_parts.append("## AI Vision Analysis")
            md_parts.append("")
            md_parts.append(f"*Analysis unavailable: {vision_analysis.get('error', 'Unknown error')}*")
            md_parts.append("")
        
        # OCR text
        md_parts.append("## Extracted Text (OCR)")
        md_parts.append("")
        
        if content["ocr_text"] and not content["ocr_text"].startswith("["):
            md_parts.append("```")
            md_parts.append(content["ocr_text"])
            md_parts.append("```")
        else:
            md_parts.append(f"*{content['ocr_text']}*")
        
        md_parts.append("")
        
        # Base64 data (truncated for readability)
        md_parts.append("## Base64 Encoded Image")
        md_parts.append("")
        md_parts.append(f"*MIME Type:* `{content.get('base64_mime', 'image/png')}`")
        md_parts.append("")
        md_parts.append("```")
        # Show first 100 chars with indication of more
        if len(content["base64_data"]) > 200:
            md_parts.append(f"{content['base64_data'][:200]}...")
            md_parts.append(f"[{len(content['base64_data'])} total characters]")
        else:
            md_parts.append(content["base64_data"])
        md_parts.append("```")
        
        return "\n".join(md_parts)
    
    def _build_json_structure(self, content: dict) -> dict:
        """Build JSON structure with full Base64 data and Vision AI analysis."""
        from datetime import datetime, timezone
        
        vision_analysis = content.get("vision_analysis", {})
        
        result = {
            "source": {
                "filename": self.filename,
                "type": self.file_type,
                "converted_at": datetime.now(timezone.utc).isoformat()
            },
            "metadata": {
                "format": content["image_format"],
                "dimensions": content["dimensions"],
                "ocr_word_count": len(content["ocr_text"].split()) if content["ocr_text"] else 0,
                "base64_size_bytes": len(content["base64_data"]),
                "vision_provider": vision_analysis.get("provider"),
                "vision_model": vision_analysis.get("model"),
            },
        }
        
        # Add Vision AI analysis if successful
        if vision_analysis and vision_analysis.get("success"):
            result["image_analysis"] = vision_analysis.get("analysis", {})
        elif vision_analysis:
            result["image_analysis"] = {
                "error": vision_analysis.get("error", "Vision analysis unavailable"),
                "success": False,
            }
        else:
            result["image_analysis"] = {
                "error": "Vision analysis not performed",
                "success": False,
            }
        
        # Add content (OCR and base64)
        result["content"] = {
            "ocr_text": content["ocr_text"],
            "base64_data": content["base64_data"],
            "base64_mime": content.get("base64_mime", "image/png"),
            "base64_data_uri": f"data:{content.get('base64_mime', 'image/png')};base64,{content['base64_data']}"
        }
        
        return result
