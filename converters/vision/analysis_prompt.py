"""
Comprehensive analysis prompt for hyper-detailed image description.
This prompt is shared across all vision providers to ensure consistent output.
"""

# The structured analysis prompt that instructs the Vision AI to provide
# incredibly detailed descriptions for near-identical image reproduction
ANALYSIS_PROMPT = """You are an expert image analyst. Your task is to provide an incredibly detailed, structured analysis of this image that would allow for near-identical reproduction.

Analyze the image and return a JSON object with the following structure. Be extremely precise and thorough:

{
  "summary": "A concise 1-2 sentence overview of what the image depicts",
  
  "scene_composition": {
    "layout": "The compositional structure (e.g., centered, rule-of-thirds, symmetrical, asymmetrical, diagonal, radial, golden-ratio)",
    "orientation": "landscape/portrait/square",
    "depth_layers": {
      "foreground": ["List of elements in the foreground with brief descriptions"],
      "midground": ["List of elements in the middle ground"],
      "background": ["List of elements in the background"]
    },
    "focal_points": [
      {
        "description": "What the focal point is",
        "position": {"x_percent": 0-100, "y_percent": 0-100},
        "visual_weight": "primary/secondary/tertiary"
      }
    ],
    "negative_space": "Description of empty/negative space and its role",
    "visual_flow": "Description of how the eye moves through the image"
  },
  
  "objects": [
    {
      "name": "Object/element name",
      "category": "person/animal/object/text/shape/nature/architecture/etc",
      "description": "Detailed description including state, pose, expression if applicable",
      "position": {
        "x_percent": 0-100,
        "y_percent": 0-100,
        "quadrant": "top-left/top-center/top-right/center-left/center/center-right/bottom-left/bottom-center/bottom-right"
      },
      "size": {
        "width_percent": 0-100,
        "height_percent": 0-100,
        "relative_scale": "dominant/large/medium/small/tiny"
      },
      "attributes": {
        "primary_color": "#hexcode",
        "secondary_colors": ["#hexcode"],
        "material": "Material/texture description",
        "opacity": "opaque/semi-transparent/transparent",
        "state": "Any relevant state (open/closed, lit/unlit, etc)",
        "orientation": "facing direction, rotation, angle"
      },
      "relationships": ["Spatial relationships with other objects"]
    }
  ],
  
  "colors": {
    "dominant_colors": [
      {
        "hex": "#hexcode",
        "name": "Color name (e.g., 'coral pink', 'deep navy')",
        "percentage": 0-100,
        "location": "Where this color primarily appears"
      }
    ],
    "palette_type": "warm/cool/neutral/monochromatic/complementary/analogous/triadic/split-complementary",
    "color_temperature": "warm/cool/neutral with description",
    "saturation_level": "vibrant/muted/desaturated/mixed",
    "contrast_level": "high/medium/low",
    "gradients": [
      {
        "type": "linear/radial/angular",
        "from_color": "#hexcode",
        "to_color": "#hexcode",
        "location": "Where the gradient appears"
      }
    ],
    "color_harmony": "Description of how colors work together"
  },
  
  "text_content": [
    {
      "text": "Exact text content",
      "font_style": "serif/sans-serif/script/decorative/monospace",
      "font_weight": "light/regular/medium/bold/black",
      "case": "uppercase/lowercase/title-case/mixed",
      "size": "large/medium/small relative to image",
      "color": "#hexcode",
      "background_color": "#hexcode or null",
      "position": {"x_percent": 0-100, "y_percent": 0-100},
      "alignment": "left/center/right/justified",
      "effects": ["shadow", "outline", "glow", "3d", "none"]
    }
  ],
  
  "lighting": {
    "type": "natural/artificial/mixed/ambient/dramatic/studio",
    "sources": [
      {
        "type": "sun/lamp/window/neon/fire/screen/etc",
        "direction": "top/bottom/left/right/top-left/top-right/bottom-left/bottom-right/behind/front",
        "intensity": "bright/moderate/dim/subtle",
        "color_temperature": "warm/cool/neutral with kelvin estimate if applicable"
      }
    ],
    "overall_brightness": "bright/moderate/dark/high-key/low-key",
    "contrast": "high/medium/low/flat",
    "shadows": {
      "presence": "strong/soft/minimal/none",
      "direction": "Direction shadows fall",
      "hardness": "hard-edged/soft/diffused"
    },
    "highlights": {
      "presence": "prominent/subtle/none",
      "type": "specular/diffused/rim"
    },
    "time_of_day_suggestion": "If applicable, what time of day the lighting suggests"
  },
  
  "textures": [
    {
      "surface": "What surface/object has this texture",
      "type": "smooth/rough/bumpy/grainy/glossy/matte/metallic/fabric/organic/etc",
      "pattern": "solid/striped/checkered/spotted/geometric/organic/random/none",
      "detail_level": "highly detailed/moderately detailed/smooth/stylized"
    }
  ],
  
  "style": {
    "artistic_style": "photorealistic/illustration/3d-render/cartoon/anime/watercolor/oil-painting/digital-art/vector/sketch/pixel-art/etc",
    "rendering_quality": "photographic/hyper-realistic/realistic/stylized/abstract",
    "mood": "cheerful/somber/energetic/calm/dramatic/mysterious/romantic/nostalgic/futuristic/etc",
    "atmosphere": "Description of the overall feeling/atmosphere",
    "era_influence": "modern/vintage/retro/futuristic/historical-period with specifics",
    "genre": "If applicable (portrait/landscape/still-life/abstract/conceptual/etc)",
    "visual_effects": ["blur", "bokeh", "vignette", "grain", "lens-flare", "motion-blur", "none"]
  },
  
  "technical": {
    "aspect_ratio": "16:9/4:3/1:1/3:2/etc",
    "perceived_resolution": "high/medium/low",
    "quality_assessment": "professional/amateur/ai-generated/stock-photo/screenshot/etc",
    "noise_level": "none/minimal/moderate/heavy",
    "sharpness": "tack-sharp/sharp/soft/blurry",
    "depth_of_field": "deep/shallow/selective with description",
    "perspective": "eye-level/bird's-eye/worm's-eye/isometric/forced/etc",
    "distortion": "none/barrel/pincushion/fisheye/etc"
  },
  
  "reproduction_prompt": "A detailed, optimized text-to-image generation prompt that would recreate this image as closely as possible. Include all crucial visual elements, style, lighting, colors, composition, and mood. Write it as a complete prompt ready to use with AI image generators like DALL-E, Midjourney, or Stable Diffusion. Be specific and comprehensive."
}

IMPORTANT INSTRUCTIONS:
1. Provide EXACT hex color codes whenever describing colors
2. Use precise percentage positions (0-100) for element placement
3. Be extremely thorough - include every visible element
4. The reproduction_prompt should be comprehensive enough to recreate the image
5. If any field doesn't apply, use null or an empty array []
6. Return ONLY valid JSON, no additional text or markdown formatting
7. Estimate values when exact measurements aren't possible, but be as accurate as possible"""


def get_analysis_prompt() -> str:
    """Get the comprehensive analysis prompt for image description."""
    return ANALYSIS_PROMPT


def get_minimal_prompt() -> str:
    """Get a minimal analysis prompt for faster/cheaper processing."""
    return """Analyze this image and return a JSON object with:
{
  "summary": "Brief description",
  "objects": [{"name": "...", "position": {"x_percent": 50, "y_percent": 50}}],
  "colors": {"dominant_colors": [{"hex": "#...", "name": "..."}]},
  "style": {"artistic_style": "...", "mood": "..."},
  "reproduction_prompt": "A prompt to recreate this image"
}
Return ONLY valid JSON."""
