#!/usr/bin/env python3
"""
Feature Extensions for Heystive Persian Voice Assistant
======================================================

This module provides feature extensions that enhance existing Heystive
functionality without modifying any existing code.

Key Features:
- Voice command extensions with Persian language support
- Enhanced TTS capabilities with cultural adaptations
- Smart home integration improvements
- Performance monitoring and optimization
- Advanced Persian text processing
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, Union
from pathlib import Path
import json
import time

logger = logging.getLogger(__name__)

class VoiceCommandExtensions:
    """Extensions for voice command processing with Persian enhancements"""
    
    def __init__(self, existing_voice_system=None):
        self.existing_system = existing_voice_system
        self.persian_commands = {}
        self.command_history = []
        self.performance_metrics = {}
        
        # Initialize Persian command extensions
        self._initialize_persian_commands()
        
    def _initialize_persian_commands(self):
        """Initialize Persian voice command extensions"""
        self.persian_commands = {
            # Enhanced greetings
            "greetings": {
                "patterns": [
                    "سلام استیو", "درود استیو", "سلام دستیار", 
                    "هی استیو", "استیو جان", "سلام علیکم استیو"
                ],
                "responses": [
                    "سلام! چطور می‌تونم کمکتون کنم؟",
                    "درود بر شما! در خدمت شما هستم.",
                    "سلام عزیز! چه کاری برای شما انجام بدم؟"
                ],
                "action": "greeting_response"
            },
            
            # Time and date queries
            "time_queries": {
                "patterns": [
                    "ساعت چنده", "چند ساعته", "وقت چقدره",
                    "تاریخ امروز", "امروز چندمه", "چه روزیه"
                ],
                "responses": [
                    "ساعت الان {time} است.",
                    "امروز {date} است.",
                    "الان {time} در تاریخ {date} می‌باشد."
                ],
                "action": "time_date_response"
            },
            
            # Voice settings
            "voice_settings": {
                "patterns": [
                    "صدات رو بلندتر کن", "آهسته‌تر صحبت کن",
                    "سرعت صدات رو کم کن", "صدای خوب‌تری داری"
                ],
                "responses": [
                    "تنظیمات صوتی تغییر کرد.",
                    "صدای من رو تنظیم کردم.",
                    "حالا بهتر می‌شنوید؟"
                ],
                "action": "voice_settings_change"
            },
            
            # Smart home controls (Persian)
            "smart_home": {
                "patterns": [
                    "چراغ {room} رو روشن کن", "پریز {device} رو خاموش کن",
                    "دمای اتاق رو {temperature} درجه کن", "موزیک پخش کن"
                ],
                "responses": [
                    "{device} رو {action} کردم.",
                    "دستور شما اجرا شد.",
                    "انجام شد!"
                ],
                "action": "smart_home_control"
            },
            
            # System status
            "system_status": {
                "patterns": [
                    "وضعیت سیستم چطوره", "همه چیز خوبه", 
                    "عملکرد سیستم", "مشکلی هست"
                ],
                "responses": [
                    "سیستم در وضعیت عالی کار می‌کند.",
                    "همه چیز عادی است. استفاده از پردازنده {cpu}٪ و حافظه {memory} گیگابایت.",
                    "هیچ مشکلی نیست، همه چیز روبراهه!"
                ],
                "action": "system_status_check"
            }
        }
        
        logger.info("✅ Persian command extensions initialized")
        
    def extend_voice_command_processing(self, original_processor: Callable) -> Callable:
        """Extend existing voice command processor with Persian enhancements"""
        
        async def enhanced_processor(audio_input: Any, context: Dict = None) -> Dict[str, Any]:
            """Enhanced voice processor with Persian command support"""
            
            # Start performance tracking
            start_time = time.time()
            
            try:
                # Try enhanced Persian processing first
                enhanced_result = await self._process_persian_commands(audio_input, context)
                
                if enhanced_result and enhanced_result.get("handled", False):
                    # Enhanced processing succeeded
                    processing_time = time.time() - start_time
                    self._record_performance_metric("enhanced_processing", processing_time)
                    
                    return enhanced_result
                else:
                    # Fall back to original processor
                    original_result = await original_processor(audio_input, context)
                    
                    # Enhance the original result with Persian formatting
                    enhanced_original = self._enhance_original_result(original_result)
                    
                    processing_time = time.time() - start_time
                    self._record_performance_metric("fallback_processing", processing_time)
                    
                    return enhanced_original
                    
            except Exception as e:
                logger.error(f"❌ Enhanced processing failed: {e}")
                
                # Always fall back to original processor on error
                try:
                    return await original_processor(audio_input, context)
                except Exception as original_error:
                    logger.error(f"❌ Original processor also failed: {original_error}")
                    return {
                        "success": False,
                        "error": "Voice processing failed",
                        "persian_error": "متأسفانه نتوانستم درخواست شما را پردازش کنم."
                    }
                    
        return enhanced_processor
        
    async def _process_persian_commands(self, audio_input: Any, context: Dict = None) -> Dict[str, Any]:
        """Process Persian voice commands with cultural context"""
        
        # Extract text from audio (this would integrate with existing STT)
        text = await self._extract_text_from_audio(audio_input)
        
        if not text:
            return {"handled": False}
            
        # Normalize Persian text
        normalized_text = self._normalize_persian_text(text)
        
        # Match against Persian command patterns
        for command_category, command_data in self.persian_commands.items():
            for pattern in command_data["patterns"]:
                if self._match_persian_pattern(normalized_text, pattern):
                    # Found matching command
                    response = await self._execute_persian_command(
                        command_category, pattern, normalized_text, context
                    )
                    
                    # Record command in history
                    self.command_history.append({
                        "timestamp": time.time(),
                        "input": text,
                        "normalized": normalized_text,
                        "category": command_category,
                        "pattern": pattern,
                        "response": response
                    })
                    
                    return {
                        "handled": True,
                        "success": True,
                        "category": command_category,
                        "input_text": text,
                        "response": response,
                        "persian_response": True
                    }
                    
        return {"handled": False}
        
    async def _extract_text_from_audio(self, audio_input: Any) -> Optional[str]:
        """Extract text from audio input (integrates with existing STT)"""
        try:
            # This would integrate with the existing STT system
            # For now, return a placeholder
            if hasattr(audio_input, 'text'):
                return audio_input.text
            elif isinstance(audio_input, str):
                return audio_input
            else:
                return None
                
        except Exception as e:
            logger.error(f"❌ Text extraction failed: {e}")
            return None
            
    def _normalize_persian_text(self, text: str) -> str:
        """Normalize Persian text for better matching"""
        if not text:
            return ""
            
        # Convert Arabic numerals to Persian
        arabic_to_persian = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
        text = text.translate(arabic_to_persian)
        
        # Normalize Persian characters
        normalizations = {
            'ي': 'ی',  # Arabic ya to Persian ya
            'ك': 'ک',  # Arabic kaf to Persian kaf
            'ء': '',   # Remove hamza
        }
        
        for old, new in normalizations.items():
            text = text.replace(old, new)
            
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        return text.strip()
        
    def _match_persian_pattern(self, text: str, pattern: str) -> bool:
        """Match Persian text against command pattern"""
        # Simple pattern matching - could be enhanced with regex or NLP
        pattern_words = pattern.split()
        text_words = text.split()
        
        # Check if all pattern words are in text (order-independent for Persian)
        for pattern_word in pattern_words:
            if '{' in pattern_word and '}' in pattern_word:
                # Skip placeholder words
                continue
            if pattern_word not in text:
                return False
                
        return True
        
    async def _execute_persian_command(self, category: str, pattern: str, text: str, context: Dict = None) -> str:
        """Execute Persian command and generate appropriate response"""
        
        command_data = self.persian_commands[category]
        action = command_data["action"]
        
        try:
            # Execute specific action based on command category
            if action == "greeting_response":
                return await self._handle_greeting(command_data)
                
            elif action == "time_date_response":
                return await self._handle_time_date(command_data)
                
            elif action == "voice_settings_change":
                return await self._handle_voice_settings(text, command_data)
                
            elif action == "smart_home_control":
                return await self._handle_smart_home(text, pattern, command_data)
                
            elif action == "system_status_check":
                return await self._handle_system_status(command_data)
                
            else:
                # Default response
                return command_data["responses"][0]
                
        except Exception as e:
            logger.error(f"❌ Command execution failed: {e}")
            return "متأسفانه مشکلی پیش آمد. لطفاً دوباره تلاش کنید."
            
    async def _handle_greeting(self, command_data: Dict) -> str:
        """Handle greeting commands"""
        import random
        return random.choice(command_data["responses"])
        
    async def _handle_time_date(self, command_data: Dict) -> str:
        """Handle time and date queries"""
        import datetime
        
        now = datetime.datetime.now()
        persian_months = [
            "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
            "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
        ]
        
        # Simple Gregorian date (could be enhanced with Persian calendar)
        time_str = now.strftime("%H:%M")
        date_str = f"{now.day} {persian_months[now.month-1] if now.month <= 12 else 'نامشخص'} {now.year}"
        
        response = command_data["responses"][0].format(time=time_str, date=date_str)
        return response
        
    async def _handle_voice_settings(self, text: str, command_data: Dict) -> str:
        """Handle voice settings changes"""
        # This would integrate with existing voice settings
        # For now, return acknowledgment
        return command_data["responses"][0]
        
    async def _handle_smart_home(self, text: str, pattern: str, command_data: Dict) -> str:
        """Handle smart home control commands"""
        # Extract device and action from text
        # This would integrate with existing smart home system
        return command_data["responses"][0].format(device="دستگاه", action="کنترل")
        
    async def _handle_system_status(self, command_data: Dict) -> str:
        """Handle system status queries"""
        # Get actual system metrics (would integrate with existing monitoring)
        cpu_usage = "۴۵"  # Placeholder
        memory_usage = "۲.۱"  # Placeholder
        
        response = command_data["responses"][1].format(cpu=cpu_usage, memory=memory_usage)
        return response
        
    def _enhance_original_result(self, original_result: Dict) -> Dict:
        """Enhance original result with Persian formatting"""
        if not original_result:
            return original_result
            
        # Add Persian formatting to response
        if "response" in original_result:
            # Add Persian politeness markers
            response = original_result["response"]
            if response and not response.endswith((".", "!", "؟")):
                response += "."
                
            # Add Persian cultural context
            original_result["persian_formatted"] = True
            original_result["response"] = response
            
        return original_result
        
    def _record_performance_metric(self, metric_name: str, value: float):
        """Record performance metric"""
        if metric_name not in self.performance_metrics:
            self.performance_metrics[metric_name] = []
            
        self.performance_metrics[metric_name].append({
            "timestamp": time.time(),
            "value": value
        })
        
        # Keep only last 100 measurements
        if len(self.performance_metrics[metric_name]) > 100:
            self.performance_metrics[metric_name] = self.performance_metrics[metric_name][-100:]
            
    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics summary"""
        metrics_summary = {}
        
        for metric_name, measurements in self.performance_metrics.items():
            if measurements:
                values = [m["value"] for m in measurements]
                metrics_summary[metric_name] = {
                    "count": len(values),
                    "average": sum(values) / len(values),
                    "min": min(values),
                    "max": max(values),
                    "recent": values[-5:] if len(values) >= 5 else values
                }
                
        return metrics_summary
        
    def get_command_history(self, limit: int = 10) -> List[Dict]:
        """Get recent command history"""
        return self.command_history[-limit:] if limit else self.command_history

class TTSEnhancementExtensions:
    """Extensions for TTS system with Persian cultural adaptations"""
    
    def __init__(self, existing_tts_system=None):
        self.existing_system = existing_tts_system
        self.persian_voice_profiles = {}
        self.cultural_adaptations = {}
        
        # Initialize Persian TTS enhancements
        self._initialize_persian_tts_enhancements()
        
    def _initialize_persian_tts_enhancements(self):
        """Initialize Persian TTS enhancements"""
        
        self.persian_voice_profiles = {
            "formal": {
                "name": "رسمی",
                "description": "صدای رسمی و محترمانه",
                "speed_modifier": 0.9,  # Slightly slower
                "pitch_modifier": 1.0,
                "emphasis_patterns": ["جناب", "سرکار", "محترم"]
            },
            "friendly": {
                "name": "دوستانه", 
                "description": "صدای گرم و دوستانه",
                "speed_modifier": 1.1,  # Slightly faster
                "pitch_modifier": 1.05,  # Slightly higher
                "emphasis_patterns": ["عزیز", "جان", "دوست"]
            },
            "professional": {
                "name": "حرفه‌ای",
                "description": "صدای حرفه‌ای و قابل اعتماد",
                "speed_modifier": 1.0,
                "pitch_modifier": 0.95,  # Slightly lower
                "emphasis_patterns": ["سیستم", "پردازش", "عملکرد"]
            }
        }
        
        self.cultural_adaptations = {
            "politeness_markers": {
                "please": ["لطفاً", "خواهشمندم", "ممنون می‌شم"],
                "thank_you": ["متشکرم", "سپاسگزارم", "ممنونم"],
                "excuse_me": ["ببخشید", "عذر می‌خوام", "شرمنده"]
            },
            "time_expressions": {
                "morning": "صبح بخیر",
                "afternoon": "ظهر بخیر", 
                "evening": "عصر بخیر",
                "night": "شب بخیر"
            },
            "response_patterns": {
                "confirmation": ["بله", "حتماً", "البته"],
                "negation": ["نه", "خیر", "متأسفانه نه"],
                "uncertainty": ["احتمالاً", "شاید", "ممکنه"]
            }
        }
        
        logger.info("✅ Persian TTS enhancements initialized")
        
    def extend_tts_generation(self, original_tts: Callable) -> Callable:
        """Extend existing TTS with Persian cultural adaptations"""
        
        async def enhanced_tts(text: str, voice_profile: str = "friendly", **kwargs) -> Any:
            """Enhanced TTS with Persian cultural adaptations"""
            
            try:
                # Apply Persian text preprocessing
                enhanced_text = self._preprocess_persian_text(text, voice_profile)
                
                # Apply voice profile modifications
                voice_config = self._get_voice_configuration(voice_profile)
                
                # Merge configurations
                enhanced_kwargs = {**kwargs, **voice_config}
                
                # Generate TTS with enhancements
                result = await original_tts(enhanced_text, **enhanced_kwargs)
                
                # Post-process result if needed
                enhanced_result = self._postprocess_tts_result(result, voice_profile)
                
                return enhanced_result
                
            except Exception as e:
                logger.error(f"❌ Enhanced TTS failed: {e}")
                
                # Fall back to original TTS
                try:
                    return await original_tts(text, **kwargs)
                except Exception as original_error:
                    logger.error(f"❌ Original TTS also failed: {original_error}")
                    return None
                    
        return enhanced_tts
        
    def _preprocess_persian_text(self, text: str, voice_profile: str) -> str:
        """Preprocess Persian text for better TTS output"""
        if not text:
            return text
            
        # Add cultural politeness based on profile
        if voice_profile == "formal":
            text = self._add_formal_markers(text)
        elif voice_profile == "friendly":
            text = self._add_friendly_markers(text)
            
        # Normalize Persian text
        text = self._normalize_persian_for_tts(text)
        
        # Add pronunciation hints
        text = self._add_pronunciation_hints(text)
        
        return text
        
    def _add_formal_markers(self, text: str) -> str:
        """Add formal politeness markers to text"""
        # Add formal greeting if not present
        if not any(marker in text for marker in ["جناب", "سرکار", "محترم"]):
            if text.startswith(("سلام", "درود")):
                text = "سلام محترم، " + text[text.find(" ")+1:]
                
        return text
        
    def _add_friendly_markers(self, text: str) -> str:
        """Add friendly markers to text"""
        # Add friendly tone if not present
        if not any(marker in text for marker in ["عزیز", "جان", "دوست"]):
            if text.startswith("سلام"):
                text = "سلام عزیز، " + text[text.find(" ")+1:]
                
        return text
        
    def _normalize_persian_for_tts(self, text: str) -> str:
        """Normalize Persian text for better TTS pronunciation"""
        
        # Convert numbers to Persian words (simplified)
        number_mapping = {
            '۰': 'صفر', '۱': 'یک', '۲': 'دو', '۳': 'سه', '۴': 'چهار',
            '۵': 'پنج', '۶': 'شش', '۷': 'هفت', '۸': 'هشت', '۹': 'نه'
        }
        
        for digit, word in number_mapping.items():
            text = text.replace(digit, word)
            
        # Expand common abbreviations
        abbreviations = {
            'م.': 'متر',
            'کم.': 'کمپانی', 
            'ش.': 'شرکت',
            'ج.': 'جناب'
        }
        
        for abbr, expansion in abbreviations.items():
            text = text.replace(abbr, expansion)
            
        return text
        
    def _add_pronunciation_hints(self, text: str) -> str:
        """Add pronunciation hints for better TTS output"""
        
        # Add pauses for better rhythm
        text = text.replace('،', '، ')  # Add space after comma
        text = text.replace('؛', '؛ ')  # Add space after semicolon
        
        # Emphasize important words
        emphasis_words = ['استیو', 'سیستم', 'دستیار', 'صوتی']
        for word in emphasis_words:
            text = text.replace(word, f'<emphasis>{word}</emphasis>')
            
        return text
        
    def _get_voice_configuration(self, voice_profile: str) -> Dict[str, Any]:
        """Get voice configuration for specific profile"""
        
        profile_config = self.persian_voice_profiles.get(voice_profile, 
                                                        self.persian_voice_profiles["friendly"])
        
        return {
            "speed": profile_config["speed_modifier"],
            "pitch": profile_config["pitch_modifier"],
            "voice_profile": voice_profile
        }
        
    def _postprocess_tts_result(self, result: Any, voice_profile: str) -> Any:
        """Post-process TTS result based on voice profile"""
        # This would apply any final modifications to the generated audio
        # For now, just return the result as-is
        return result

class SmartHomeExtensions:
    """Extensions for smart home integration with Persian commands"""
    
    def __init__(self, existing_smart_home=None):
        self.existing_system = existing_smart_home
        self.persian_device_names = {}
        self.room_mappings = {}
        
        # Initialize Persian smart home extensions
        self._initialize_persian_smart_home()
        
    def _initialize_persian_smart_home(self):
        """Initialize Persian smart home command extensions"""
        
        self.persian_device_names = {
            # Lighting
            "چراغ": ["light", "lamp", "bulb"],
            "لامپ": ["light", "lamp", "bulb"], 
            "نور": ["light", "lamp", "bulb"],
            
            # Electrical
            "پریز": ["outlet", "plug", "socket"],
            "کلید": ["switch"],
            "برق": ["power", "electricity"],
            
            # Climate
            "کولر": ["ac", "air_conditioner", "cooling"],
            "بخاری": ["heater", "heating"],
            "فن": ["fan"],
            "دما": ["temperature", "thermostat"],
            
            # Entertainment
            "تلویزیون": ["tv", "television"],
            "موزیک": ["music", "speaker", "audio"],
            "رادیو": ["radio"],
            
            # Security
            "دوربین": ["camera", "security_camera"],
            "آلارم": ["alarm", "security_alarm"],
            "قفل": ["lock", "door_lock"]
        }
        
        self.room_mappings = {
            "نشیمن": ["living_room", "lounge"],
            "اتاق خواب": ["bedroom", "master_bedroom"],
            "آشپزخانه": ["kitchen"],
            "حمام": ["bathroom", "toilet"],
            "اتاق کار": ["office", "study"],
            "اتاق کودک": ["kids_room", "children_room"],
            "راهرو": ["hallway", "corridor"],
            "ورودی": ["entrance", "foyer"],
            "پذیرایی": ["guest_room", "reception"]
        }
        
        logger.info("✅ Persian smart home extensions initialized")
        
    def extend_smart_home_control(self, original_controller: Callable) -> Callable:
        """Extend existing smart home controller with Persian commands"""
        
        async def enhanced_controller(command: str, **kwargs) -> Dict[str, Any]:
            """Enhanced smart home controller with Persian support"""
            
            try:
                # Parse Persian command
                parsed_command = self._parse_persian_smart_home_command(command)
                
                if parsed_command["success"]:
                    # Convert to English command for existing system
                    english_command = self._convert_to_english_command(parsed_command)
                    
                    # Execute through existing system
                    result = await original_controller(english_command, **kwargs)
                    
                    # Add Persian response
                    if result and result.get("success"):
                        result["persian_response"] = self._generate_persian_response(
                            parsed_command, result
                        )
                        
                    return result
                else:
                    # Fall back to original controller
                    return await original_controller(command, **kwargs)
                    
            except Exception as e:
                logger.error(f"❌ Enhanced smart home control failed: {e}")
                
                # Fall back to original controller
                try:
                    return await original_controller(command, **kwargs)
                except Exception as original_error:
                    logger.error(f"❌ Original smart home controller failed: {original_error}")
                    return {
                        "success": False,
                        "error": "Smart home control failed",
                        "persian_error": "کنترل خانه هوشمند با مشکل مواجه شد."
                    }
                    
        return enhanced_controller
        
    def _parse_persian_smart_home_command(self, command: str) -> Dict[str, Any]:
        """Parse Persian smart home command"""
        
        result = {
            "success": False,
            "device": None,
            "room": None,
            "action": None,
            "value": None
        }
        
        command_lower = command.lower()
        
        # Extract device
        for persian_device, english_devices in self.persian_device_names.items():
            if persian_device in command_lower:
                result["device"] = english_devices[0]  # Use first English equivalent
                break
                
        # Extract room
        for persian_room, english_rooms in self.room_mappings.items():
            if persian_room in command_lower:
                result["room"] = english_rooms[0]  # Use first English equivalent
                break
                
        # Extract action
        if "روشن" in command_lower or "باز" in command_lower:
            result["action"] = "turn_on"
        elif "خاموش" in command_lower or "بسته" in command_lower:
            result["action"] = "turn_off"
        elif "کم" in command_lower:
            result["action"] = "decrease"
        elif "زیاد" in command_lower or "بیشتر" in command_lower:
            result["action"] = "increase"
            
        # Extract value (temperature, brightness, etc.)
        import re
        numbers = re.findall(r'[\d۰-۹]+', command)
        if numbers:
            # Convert Persian numbers to English
            persian_to_english = str.maketrans('۰۱۲۳۴۵۶۷۸۹', '0123456789')
            result["value"] = numbers[0].translate(persian_to_english)
            
        # Check if we have minimum required information
        if result["device"] and result["action"]:
            result["success"] = True
            
        return result
        
    def _convert_to_english_command(self, parsed_command: Dict) -> str:
        """Convert parsed Persian command to English command"""
        
        parts = []
        
        if parsed_command["action"]:
            parts.append(parsed_command["action"])
            
        if parsed_command["device"]:
            parts.append(parsed_command["device"])
            
        if parsed_command["room"]:
            parts.append(f"in {parsed_command['room']}")
            
        if parsed_command["value"]:
            parts.append(f"to {parsed_command['value']}")
            
        return " ".join(parts)
        
    def _generate_persian_response(self, parsed_command: Dict, result: Dict) -> str:
        """Generate Persian response for smart home command"""
        
        device_persian = None
        for persian_device, english_devices in self.persian_device_names.items():
            if parsed_command["device"] in english_devices:
                device_persian = persian_device
                break
                
        room_persian = None
        if parsed_command["room"]:
            for persian_room, english_rooms in self.room_mappings.items():
                if parsed_command["room"] in english_rooms:
                    room_persian = persian_room
                    break
                    
        action_persian = {
            "turn_on": "روشن کردم",
            "turn_off": "خاموش کردم", 
            "increase": "زیاد کردم",
            "decrease": "کم کردم"
        }.get(parsed_command["action"], "تغییر دادم")
        
        # Construct Persian response
        response_parts = []
        
        if device_persian:
            response_parts.append(device_persian)
            
        if room_persian:
            response_parts.append(room_persian)
            
        response_parts.append("را")
        response_parts.append(action_persian)
        
        return " ".join(response_parts) + "."

# Convenience functions for easy integration
def create_voice_command_extensions(existing_voice_system=None) -> VoiceCommandExtensions:
    """Create voice command extensions"""
    return VoiceCommandExtensions(existing_voice_system)

def create_tts_enhancement_extensions(existing_tts_system=None) -> TTSEnhancementExtensions:
    """Create TTS enhancement extensions"""
    return TTSEnhancementExtensions(existing_tts_system)

def create_smart_home_extensions(existing_smart_home=None) -> SmartHomeExtensions:
    """Create smart home extensions"""
    return SmartHomeExtensions(existing_smart_home)