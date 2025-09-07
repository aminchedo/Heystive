#!/usr/bin/env python3
"""
Advanced Persian UI Components for Heystive Voice Assistant
==========================================================

This module provides advanced Persian UI components optimized for RTL languages
and Persian cultural design patterns.

Key Features:
- Advanced Persian typography and text rendering
- Cultural color schemes and design patterns
- RTL-optimized layouts and navigation
- Persian calendar and date/time components
- Voice-first interaction patterns for Persian speakers
- Accessibility improvements for Persian users
"""

from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import logging
import json

logger = logging.getLogger(__name__)

class PersianTypographySystem:
    """Advanced Persian typography system with cultural adaptations"""
    
    PERSIAN_FONTS = {
        # Modern Persian fonts with fallbacks
        "vazirmatn": {
            "name": "Vazirmatn",
            "fallbacks": ["Vazir", "Sahel", "Tahoma", "Arial"],
            "weights": [100, 200, 300, 400, 500, 600, 700, 800, 900],
            "styles": ["normal", "italic"],
            "features": ["contextual_alternates", "ligatures", "kerning"],
            "best_for": ["body_text", "headings", "ui_elements"]
        },
        "vazir": {
            "name": "Vazir",
            "fallbacks": ["Sahel", "Tahoma", "Arial"],
            "weights": [300, 400, 500, 600, 700],
            "styles": ["normal"],
            "features": ["ligatures", "kerning"],
            "best_for": ["body_text", "ui_elements"]
        },
        "sahel": {
            "name": "Sahel",
            "fallbacks": ["Tahoma", "Arial"],
            "weights": [300, 400, 500, 600, 700],
            "styles": ["normal"],
            "features": ["basic_shaping"],
            "best_for": ["body_text", "fallback"]
        },
        "amiri": {
            "name": "Amiri",
            "fallbacks": ["Times New Roman"],
            "weights": [400, 700],
            "styles": ["normal", "italic"],
            "features": ["advanced_typography", "decorative"],
            "best_for": ["headings", "decorative_text"]
        }
    }
    
    TYPOGRAPHY_SCALE = {
        # Persian-optimized typography scale
        "display_large": {"size": 57, "line_height": 64, "weight": 400, "spacing": -0.25},
        "display_medium": {"size": 45, "line_height": 52, "weight": 400, "spacing": 0},
        "display_small": {"size": 36, "line_height": 44, "weight": 400, "spacing": 0},
        "headline_large": {"size": 32, "line_height": 40, "weight": 400, "spacing": 0},
        "headline_medium": {"size": 28, "line_height": 36, "weight": 400, "spacing": 0},
        "headline_small": {"size": 24, "line_height": 32, "weight": 400, "spacing": 0},
        "title_large": {"size": 22, "line_height": 28, "weight": 500, "spacing": 0},
        "title_medium": {"size": 16, "line_height": 24, "weight": 500, "spacing": 0.15},
        "title_small": {"size": 14, "line_height": 20, "weight": 500, "spacing": 0.1},
        "body_large": {"size": 16, "line_height": 24, "weight": 400, "spacing": 0.5},
        "body_medium": {"size": 14, "line_height": 20, "weight": 400, "spacing": 0.25},
        "body_small": {"size": 12, "line_height": 16, "weight": 400, "spacing": 0.4},
        "label_large": {"size": 14, "line_height": 20, "weight": 500, "spacing": 0.1},
        "label_medium": {"size": 12, "line_height": 16, "weight": 500, "spacing": 0.5},
        "label_small": {"size": 11, "line_height": 16, "weight": 500, "spacing": 0.5}
    }
    
    @classmethod
    def get_font_stack(cls, primary_font: str = "vazirmatn") -> str:
        """Get CSS font stack for Persian text"""
        font_config = cls.PERSIAN_FONTS.get(primary_font, cls.PERSIAN_FONTS["vazirmatn"])
        
        fonts = [f"'{font_config['name']}'"] + [f"'{font}'" for font in font_config["fallbacks"]]
        return ", ".join(fonts) + ", sans-serif"
        
    @classmethod
    def get_typography_css(cls, scale_name: str, font_family: str = "vazirmatn") -> str:
        """Get CSS for specific typography scale"""
        scale = cls.TYPOGRAPHY_SCALE.get(scale_name)
        if not scale:
            return ""
            
        font_stack = cls.get_font_stack(font_family)
        
        return f"""
        font-family: {font_stack};
        font-size: {scale['size']}px;
        line-height: {scale['line_height']}px;
        font-weight: {scale['weight']};
        letter-spacing: {scale['spacing']}px;
        direction: rtl;
        text-align: right;
        """

class PersianColorSystem:
    """Persian cultural color system with semantic meanings"""
    
    CULTURAL_COLORS = {
        # Traditional Persian colors with cultural significance
        "persian_blue": {
            "primary": "#1976D2",
            "light": "#42A5F5", 
            "dark": "#0D47A1",
            "meaning": "trust, wisdom, stability",
            "usage": ["primary_actions", "headers", "links"]
        },
        "persian_turquoise": {
            "primary": "#1ABC9C",
            "light": "#4DD0E1",
            "dark": "#00695C",
            "meaning": "healing, protection, spiritual",
            "usage": ["success_states", "health", "positive_feedback"]
        },
        "persian_gold": {
            "primary": "#FF9800",
            "light": "#FFB74D",
            "dark": "#F57C00",
            "meaning": "prosperity, luxury, warmth",
            "usage": ["warnings", "highlights", "premium_features"]
        },
        "persian_rose": {
            "primary": "#E91E63",
            "light": "#F48FB1",
            "dark": "#AD1457",
            "meaning": "beauty, love, passion",
            "usage": ["accent_colors", "decorative", "emotional_content"]
        },
        "persian_saffron": {
            "primary": "#FFC107",
            "light": "#FFECB3",
            "dark": "#FF8F00",
            "meaning": "precious, rare, celebration",
            "usage": ["special_occasions", "premium", "achievements"]
        },
        "persian_night": {
            "primary": "#263238",
            "light": "#37474F",
            "dark": "#102027",
            "meaning": "mystery, depth, elegance",
            "usage": ["dark_theme", "text", "backgrounds"]
        }
    }
    
    SEMANTIC_COLORS = {
        # Semantic color mapping for UI states
        "success": "persian_turquoise",
        "warning": "persian_gold", 
        "error": "persian_rose",
        "info": "persian_blue",
        "premium": "persian_saffron",
        "neutral": "persian_night"
    }
    
    @classmethod
    def get_color_palette(cls, theme: str = "light") -> Dict[str, str]:
        """Get complete color palette for specified theme"""
        if theme == "dark":
            return cls._get_dark_palette()
        else:
            return cls._get_light_palette()
            
    @classmethod
    def _get_light_palette(cls) -> Dict[str, str]:
        """Get light theme color palette"""
        return {
            # Primary colors
            "primary": cls.CULTURAL_COLORS["persian_blue"]["primary"],
            "primary_light": cls.CULTURAL_COLORS["persian_blue"]["light"],
            "primary_dark": cls.CULTURAL_COLORS["persian_blue"]["dark"],
            
            # Secondary colors
            "secondary": cls.CULTURAL_COLORS["persian_turquoise"]["primary"],
            "secondary_light": cls.CULTURAL_COLORS["persian_turquoise"]["light"],
            "secondary_dark": cls.CULTURAL_COLORS["persian_turquoise"]["dark"],
            
            # Accent colors
            "accent": cls.CULTURAL_COLORS["persian_gold"]["primary"],
            "accent_light": cls.CULTURAL_COLORS["persian_gold"]["light"],
            "accent_dark": cls.CULTURAL_COLORS["persian_gold"]["dark"],
            
            # Surface colors
            "background": "#FAFAFA",
            "surface": "#FFFFFF",
            "surface_variant": "#F5F5F5",
            
            # Text colors
            "on_background": "#212121",
            "on_surface": "#212121",
            "on_primary": "#FFFFFF",
            "on_secondary": "#FFFFFF",
            "on_accent": "#FFFFFF",
            
            # State colors
            "success": cls.CULTURAL_COLORS["persian_turquoise"]["primary"],
            "warning": cls.CULTURAL_COLORS["persian_gold"]["primary"],
            "error": cls.CULTURAL_COLORS["persian_rose"]["primary"],
            "info": cls.CULTURAL_COLORS["persian_blue"]["primary"]
        }
        
    @classmethod
    def _get_dark_palette(cls) -> Dict[str, str]:
        """Get dark theme color palette"""
        return {
            # Primary colors (adjusted for dark theme)
            "primary": cls.CULTURAL_COLORS["persian_blue"]["light"],
            "primary_light": "#90CAF9",
            "primary_dark": cls.CULTURAL_COLORS["persian_blue"]["primary"],
            
            # Secondary colors
            "secondary": cls.CULTURAL_COLORS["persian_turquoise"]["light"],
            "secondary_light": "#80CBC4",
            "secondary_dark": cls.CULTURAL_COLORS["persian_turquoise"]["primary"],
            
            # Accent colors
            "accent": cls.CULTURAL_COLORS["persian_gold"]["light"],
            "accent_light": "#FFCC02",
            "accent_dark": cls.CULTURAL_COLORS["persian_gold"]["primary"],
            
            # Surface colors (dark theme)
            "background": "#121212",
            "surface": "#1E1E1E",
            "surface_variant": "#2C2C2C",
            
            # Text colors (dark theme)
            "on_background": "#FFFFFF",
            "on_surface": "#FFFFFF",
            "on_primary": "#000000",
            "on_secondary": "#000000",
            "on_accent": "#000000",
            
            # State colors (adjusted for dark theme)
            "success": cls.CULTURAL_COLORS["persian_turquoise"]["light"],
            "warning": cls.CULTURAL_COLORS["persian_gold"]["light"],
            "error": cls.CULTURAL_COLORS["persian_rose"]["light"],
            "info": cls.CULTURAL_COLORS["persian_blue"]["light"]
        }

class PersianLayoutSystem:
    """Advanced RTL layout system for Persian interfaces"""
    
    LAYOUT_PATTERNS = {
        "voice_dashboard": {
            "grid": "1fr 2fr 1fr",  # Sidebar, main, sidebar (RTL)
            "areas": [
                "voice-controls main-content system-status",
                "voice-controls main-content system-status"
            ],
            "responsive_breakpoints": {
                "mobile": "1fr",  # Single column on mobile
                "tablet": "1fr 2fr",  # Two columns on tablet
                "desktop": "1fr 2fr 1fr"  # Three columns on desktop
            }
        },
        "settings_panel": {
            "grid": "auto 1fr",  # Header, content
            "areas": [
                "settings-header settings-header",
                "settings-nav settings-content"
            ],
            "responsive_breakpoints": {
                "mobile": "auto 1fr",  # Stack on mobile
                "tablet": "auto 1fr 1fr",  # Side by side on tablet
                "desktop": "auto 200px 1fr"  # Fixed sidebar on desktop
            }
        },
        "voice_interaction": {
            "grid": "auto 1fr auto",  # Header, content, controls
            "areas": [
                "voice-status voice-status voice-status",
                "voice-visualizer voice-visualizer voice-visualizer", 
                "voice-controls voice-controls voice-controls"
            ],
            "responsive_breakpoints": {
                "mobile": "auto 1fr auto",
                "tablet": "auto 1fr auto", 
                "desktop": "auto 1fr auto"
            }
        }
    }
    
    @classmethod
    def get_layout_css(cls, pattern_name: str, breakpoint: str = "desktop") -> str:
        """Get CSS for specific layout pattern"""
        pattern = cls.LAYOUT_PATTERNS.get(pattern_name)
        if not pattern:
            return ""
            
        grid = pattern["responsive_breakpoints"].get(breakpoint, pattern["grid"])
        areas = pattern["areas"]
        
        grid_areas = "\n".join([f'"{area}"' for area in areas])
        
        return f"""
        display: grid;
        grid-template-columns: {grid};
        grid-template-areas: 
            {grid_areas};
        gap: 1rem;
        direction: rtl;
        """

class PersianVoiceUIComponents:
    """Advanced Persian voice UI components"""
    
    def __init__(self):
        self.typography = PersianTypographySystem()
        self.colors = PersianColorSystem()
        self.layout = PersianLayoutSystem()
        
    def generate_voice_status_component(self, theme: str = "light") -> str:
        """Generate Persian voice status component"""
        colors = self.colors.get_color_palette(theme)
        typography = self.typography.get_typography_css("title_medium")
        
        return f"""
        <div class="persian-voice-status" style="
            background: linear-gradient(135deg, {colors['primary']}, {colors['secondary']});
            color: {colors['on_primary']};
            border-radius: 12px;
            padding: 1rem 1.5rem;
            display: flex;
            align-items: center;
            gap: 0.75rem;
            {typography}
        ">
            <div class="status-indicator" style="
                width: 12px;
                height: 12px;
                border-radius: 50%;
                background-color: {colors['success']};
                animation: pulse 2s infinite;
            "></div>
            <span class="status-text">آماده برای دریافت فرمان صوتی</span>
            <div class="voice-wave" style="
                margin-right: auto;
                display: flex;
                align-items: center;
                gap: 2px;
            ">
                {''.join([f'<div class="wave-bar" style="width: 3px; height: {4 + i*2}px; background: {colors["on_primary"]}; border-radius: 1px; animation: wave 1.5s ease-in-out infinite; animation-delay: {i*0.1}s;"></div>' for i in range(5)])}
            </div>
        </div>
        """
        
    def generate_persian_button(self, text: str, style: str = "primary", size: str = "medium", theme: str = "light") -> str:
        """Generate Persian button with cultural styling"""
        colors = self.colors.get_color_palette(theme)
        
        # Button style variations
        style_configs = {
            "primary": {
                "background": colors["primary"],
                "color": colors["on_primary"],
                "border": "none"
            },
            "secondary": {
                "background": colors["secondary"],
                "color": colors["on_secondary"],
                "border": "none"
            },
            "outlined": {
                "background": "transparent",
                "color": colors["primary"],
                "border": f"2px solid {colors['primary']}"
            },
            "text": {
                "background": "transparent",
                "color": colors["primary"],
                "border": "none"
            }
        }
        
        # Size variations
        size_configs = {
            "small": {"padding": "8px 16px", "font_size": "12px"},
            "medium": {"padding": "12px 24px", "font_size": "14px"},
            "large": {"padding": "16px 32px", "font_size": "16px"}
        }
        
        style_config = style_configs.get(style, style_configs["primary"])
        size_config = size_configs.get(size, size_configs["medium"])
        typography = self.typography.get_typography_css("label_large")
        
        return f"""
        <button class="persian-button persian-button--{style} persian-button--{size}" style="
            background: {style_config['background']};
            color: {style_config['color']};
            border: {style_config['border']};
            border-radius: 8px;
            padding: {size_config['padding']};
            font-size: {size_config['font_size']};
            {typography}
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            user-select: none;
            outline: none;
            position: relative;
            overflow: hidden;
        " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.15)';" 
           onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 4px rgba(0,0,0,0.1)';"
           onmousedown="this.style.transform='translateY(0)';"
           onmouseup="this.style.transform='translateY(-2px)';">
            {text}
            <span class="button-ripple" style="
                position: absolute;
                top: 50%;
                left: 50%;
                width: 0;
                height: 0;
                background: rgba(255,255,255,0.3);
                border-radius: 50%;
                transform: translate(-50%, -50%);
                transition: width 0.6s, height 0.6s;
            "></span>
        </button>
        """
        
    def generate_persian_text_field(self, label: str, placeholder: str = "", field_type: str = "text", theme: str = "light") -> str:
        """Generate Persian text field with RTL support"""
        colors = self.colors.get_color_palette(theme)
        typography = self.typography.get_typography_css("body_large")
        label_typography = self.typography.get_typography_css("label_medium")
        
        field_id = f"field_{hash(label) % 10000}"
        
        return f"""
        <div class="persian-textfield" style="
            position: relative;
            margin: 1rem 0;
            direction: rtl;
        ">
            <input type="{field_type}" id="{field_id}" class="persian-textfield__input" 
                   placeholder="{placeholder}" style="
                width: 100%;
                padding: 16px 12px 8px 12px;
                border: 2px solid {colors['surface_variant']};
                border-radius: 8px;
                background: {colors['surface']};
                color: {colors['on_surface']};
                {typography}
                outline: none;
                transition: border-color 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                direction: rtl;
                text-align: right;
            " onfocus="this.style.borderColor='{colors['primary']}'; this.nextElementSibling.style.color='{colors['primary']}'; this.nextElementSibling.style.transform='translateY(-20px) scale(0.8)';"
               onblur="if(!this.value) {{ this.nextElementSibling.style.transform='translateY(0) scale(1)'; this.nextElementSibling.style.color='{colors['on_surface']}'; }} this.style.borderColor='{colors['surface_variant']}';">
            <label for="{field_id}" class="persian-textfield__label" style="
                position: absolute;
                top: 16px;
                right: 12px;
                color: {colors['on_surface']};
                {label_typography}
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                pointer-events: none;
                background: {colors['surface']};
                padding: 0 4px;
                transform-origin: top right;
            ">{label}</label>
        </div>
        """
        
    def generate_persian_card(self, title: str, content: str, actions: List[str] = None, theme: str = "light") -> str:
        """Generate Persian card component"""
        colors = self.colors.get_color_palette(theme)
        title_typography = self.typography.get_typography_css("title_large")
        content_typography = self.typography.get_typography_css("body_medium")
        
        actions_html = ""
        if actions:
            actions_html = f"""
            <div class="card-actions" style="
                display: flex;
                gap: 0.5rem;
                margin-top: 1rem;
                padding-top: 1rem;
                border-top: 1px solid {colors['surface_variant']};
                justify-content: flex-end;
            ">
                {''.join([self.generate_persian_button(action, "text", "small", theme) for action in actions])}
            </div>
            """
            
        return f"""
        <div class="persian-card" style="
            background: {colors['surface']};
            color: {colors['on_surface']};
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            direction: rtl;
        " onmouseover="this.style.boxShadow='0 4px 16px rgba(0,0,0,0.15)';"
           onmouseout="this.style.boxShadow='0 2px 8px rgba(0,0,0,0.1)';">
            <h3 class="card-title" style="
                {title_typography}
                color: {colors['primary']};
                margin: 0 0 0.75rem 0;
            ">{title}</h3>
            <div class="card-content" style="
                {content_typography}
                line-height: 1.6;
            ">{content}</div>
            {actions_html}
        </div>
        """
        
    def generate_persian_voice_visualizer(self, theme: str = "light") -> str:
        """Generate Persian voice visualizer component"""
        colors = self.colors.get_color_palette(theme)
        
        bars_html = ''.join([
            f'<div class="voice-bar" style="width: 4px; height: 8px; background: linear-gradient(to top, {colors["primary"]}, {colors["secondary"]}); border-radius: 2px; transition: height 0.1s ease; animation: voice-wave 1.5s ease-in-out infinite; animation-delay: {i*0.1}s;"></div>'
            for i in range(24)
        ])
        
        return f"""
        <div class="persian-voice-visualizer" style="
            width: 100%;
            height: 120px;
            background: {colors['surface']};
            border: 2px solid {colors['primary']};
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 3px;
            padding: 1rem;
            position: relative;
            overflow: hidden;
        ">
            <div class="voice-bars" style="
                display: flex;
                align-items: center;
                gap: 3px;
                height: 100%;
            ">
                {bars_html}
            </div>
            
            <div class="visualizer-overlay" style="
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: linear-gradient(45deg, transparent 48%, {colors['primary']}20 50%, transparent 52%);
                animation: scan 3s linear infinite;
            "></div>
        </div>
        
        <style>
        @keyframes voice-wave {{
            0%, 100% {{ height: 8px; opacity: 0.6; }}
            50% {{ height: 40px; opacity: 1; }}
        }}
        
        @keyframes scan {{
            0% {{ transform: translateX(-100%); }}
            100% {{ transform: translateX(100%); }}
        }}
        </style>
        """
        
    def generate_complete_persian_voice_interface(self, theme: str = "light") -> str:
        """Generate complete Persian voice interface"""
        colors = self.colors.get_color_palette(theme)
        
        return f"""
        <!DOCTYPE html>
        <html lang="fa" dir="rtl">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>استیو - دستیار صوتی پیشرفته</title>
            <style>
                body {{
                    font-family: {self.typography.get_font_stack()};
                    background: {colors['background']};
                    color: {colors['on_background']};
                    margin: 0;
                    padding: 1rem;
                    direction: rtl;
                }}
                
                .main-container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    {self.layout.get_layout_css('voice_dashboard')}
                }}
                
                .voice-controls {{ grid-area: voice-controls; }}
                .main-content {{ grid-area: main-content; }}
                .system-status {{ grid-area: system-status; }}
                
                @media (max-width: 768px) {{
                    .main-container {{
                        grid-template-columns: 1fr;
                        grid-template-areas: 
                            "voice-controls"
                            "main-content"
                            "system-status";
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="main-container">
                <div class="voice-controls">
                    {self.generate_persian_card("کنترل صوتی", self.generate_voice_status_component(theme) + self.generate_persian_voice_visualizer(theme), ["شروع گوش دادن", "توقف", "تست"], theme)}
                </div>
                
                <div class="main-content">
                    {self.generate_persian_card("تعامل صوتی", 
                        self.generate_persian_text_field("آخرین فرمان دریافتی", "فرمان صوتی اینجا نمایش داده می‌شود...", "textarea", theme) +
                        self.generate_persian_text_field("پاسخ سیستم", "پاسخ سیستم اینجا نمایش داده می‌شود...", "textarea", theme),
                        theme=theme)}
                </div>
                
                <div class="system-status">
                    {self.generate_persian_card("وضعیت سیستم", 
                        "<p>استفاده از پردازنده: <span class='persian-number'>۴۵٪</span></p>" +
                        "<p>استفاده از حافظه: <span class='persian-number'>۲.۱ گیگابایت</span></p>" +
                        "<p>موتور صوتی: Whisper Large</p>" +
                        "<p>موتور TTS: Persian VITS</p>",
                        ["بروزرسانی", "بهینه‌سازی"], theme)}
                </div>
            </div>
        </body>
        </html>
        """

# Convenience functions
def create_persian_ui_components() -> PersianVoiceUIComponents:
    """Create Persian UI components system"""
    return PersianVoiceUIComponents()

def generate_persian_voice_interface(output_path: str, theme: str = "light") -> bool:
    """Generate complete Persian voice interface and save to file"""
    try:
        components = create_persian_ui_components()
        html_content = components.generate_complete_persian_voice_interface(theme)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        logger.info(f"✅ Persian voice interface generated: {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to generate Persian voice interface: {e}")
        return False