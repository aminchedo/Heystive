"""
LLM Manager for Persian Voice Assistant
Handles integration with language models for natural Persian conversation
"""

import asyncio
import logging
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path
import os

# Optional imports
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    openai = None
    OPENAI_AVAILABLE = False

logger = logging.getLogger(__name__)

class PersianLLMManager:
    """
    Advanced LLM integration optimized for Persian language
    Supports multiple LLM providers with Persian conversation capabilities
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.current_provider = config.get("llm_provider", "openai")
        self.model_name = config.get("model_name", "gpt-4")
        
        # Persian conversation context
        self.conversation_history = []
        self.system_prompt = self._load_persian_system_prompt()
        
        # Performance tracking
        self.response_stats = {
            "total_requests": 0,
            "average_latency": 0.0,
            "success_rate": 0.0,
            "persian_accuracy": 0.0
        }
        
        # Initialize LLM clients
        self.clients = {}
        self._initialize_llm_clients()
        
    def _initialize_llm_clients(self):
        """Initialize LLM client connections"""
        try:
            # OpenAI client
            if self.current_provider == "openai":
                openai.api_key = os.getenv("OPENAI_API_KEY")
                if not openai.api_key:
                    logger.warning("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
                else:
                    self.clients["openai"] = openai
                    logger.info("OpenAI client initialized")
            
            # Add other providers as needed
            # Anthropic Claude, Google Gemini, etc.
            
        except Exception as e:
            logger.error(f"LLM client initialization failed: {e}")
    
    def _load_persian_system_prompt(self) -> str:
        """Load Persian system prompt for Steve assistant"""
        return """شما استیو هستید، دستیار صوتی هوشمند فارسی زبان. شما باید:

1. همیشه به فارسی پاسخ دهید
2. طبیعی و دوستانه صحبت کنید
3. در کنترل خانه هوشمند کمک کنید
4. سوالات را به طور کامل پاسخ دهید
5. اگر متوجه نشدید، بپرسید که دوباره توضیح دهند

قابلیت‌های شما:
- کنترل چراغ‌ها و وسایل برقی
- پاسخ به سوالات عمومی
- کمک در کارهای روزمره
- ارائه اطلاعات مفید

همیشه مؤدب، مفید و دقیق باشید."""

    async def generate_persian_response(self, user_input: str, context: Dict[str, Any] = None) -> str:
        """
        Generate natural Persian response using LLM
        
        Args:
            user_input: User's Persian input text
            context: Additional context (device states, time, etc.)
            
        Returns:
            Persian response text
        """
        start_time = time.time()
        
        try:
            # Prepare conversation context
            messages = self._prepare_conversation_context(user_input, context)
            
            # Generate response using current provider
            response = await self._call_llm(messages)
            
            # Post-process Persian response
            processed_response = self._post_process_persian_response(response)
            
            # Update conversation history
            self._update_conversation_history(user_input, processed_response)
            
            # Update performance stats
            latency = time.time() - start_time
            self._update_response_stats(latency, True)
            
            logger.info(f"Generated Persian response in {latency:.2f}s")
            return processed_response
            
        except Exception as e:
            logger.error(f"Persian response generation failed: {e}")
            self._update_response_stats(0, False)
            return self._get_fallback_response(user_input)
    
    def _prepare_conversation_context(self, user_input: str, context: Dict[str, Any] = None) -> List[Dict[str, str]]:
        """Prepare conversation context for LLM"""
        messages = [
            {"role": "system", "content": self.system_prompt}
        ]
        
        # Add recent conversation history
        for entry in self.conversation_history[-5:]:  # Last 5 exchanges
            messages.append({"role": "user", "content": entry["user"]})
            messages.append({"role": "assistant", "content": entry["assistant"]})
        
        # Add context information if available
        if context:
            context_info = self._format_context_info(context)
            if context_info:
                messages.append({"role": "system", "content": f"اطلاعات فعلی: {context_info}"})
        
        # Add current user input
        messages.append({"role": "user", "content": user_input})
        
        return messages
    
    def _format_context_info(self, context: Dict[str, Any]) -> str:
        """Format context information in Persian"""
        context_parts = []
        
        if "time" in context:
            context_parts.append(f"زمان: {context['time']}")
        
        if "device_states" in context:
            device_info = []
            for device, state in context["device_states"].items():
                status = "روشن" if state else "خاموش"
                device_info.append(f"{device}: {status}")
            if device_info:
                context_parts.append(f"وضعیت دستگاه‌ها: {', '.join(device_info)}")
        
        if "weather" in context:
            context_parts.append(f"آب و هوا: {context['weather']}")
        
        return " | ".join(context_parts)
    
    async def _call_llm(self, messages: List[Dict[str, str]]) -> str:
        """Call LLM API with prepared messages"""
        if self.current_provider == "openai" and "openai" in self.clients:
            return await self._call_openai(messages)
        else:
            raise Exception(f"LLM provider {self.current_provider} not available")
    
    async def _call_openai(self, messages: List[Dict[str, str]]) -> str:
        """Call OpenAI API"""
        try:
            response = await asyncio.to_thread(
                openai.ChatCompletion.create,
                model=self.model_name,
                messages=messages,
                max_tokens=500,
                temperature=0.7,
                top_p=0.9
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {e}")
            raise
    
    def _post_process_persian_response(self, response: str) -> str:
        """Post-process Persian response for quality"""
        # Remove any non-Persian artifacts
        processed = response.strip()
        
        # Ensure proper Persian punctuation
        processed = processed.replace('?', '؟')
        processed = processed.replace(',', '،')
        
        # Remove any English text that might have leaked through
        import re
        # Keep Persian, Arabic, numbers, and basic punctuation
        processed = re.sub(r'[^\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF\s\d\.\،\؟\!\:\;\(\)\-]', '', processed)
        
        # Ensure response isn't too long for TTS
        if len(processed) > 200:
            sentences = processed.split('.')
            processed = '. '.join(sentences[:2]) + '.'
        
        return processed
    
    def _update_conversation_history(self, user_input: str, assistant_response: str):
        """Update conversation history"""
        self.conversation_history.append({
            "user": user_input,
            "assistant": assistant_response,
            "timestamp": time.time()
        })
        
        # Keep only recent history
        if len(self.conversation_history) > 10:
            self.conversation_history = self.conversation_history[-10:]
    
    def _update_response_stats(self, latency: float, success: bool):
        """Update response statistics"""
        self.response_stats["total_requests"] += 1
        
        if success:
            # Update average latency
            total = self.response_stats["total_requests"]
            current_avg = self.response_stats["average_latency"]
            self.response_stats["average_latency"] = (current_avg * (total - 1) + latency) / total
            
            # Update success rate
            current_success_rate = self.response_stats["success_rate"]
            self.response_stats["success_rate"] = (current_success_rate * (total - 1) + 1) / total
        else:
            # Update success rate for failure
            total = self.response_stats["total_requests"]
            current_success_rate = self.response_stats["success_rate"]
            self.response_stats["success_rate"] = (current_success_rate * (total - 1)) / total
    
    def _get_fallback_response(self, user_input: str) -> str:
        """Generate fallback response when LLM fails"""
        user_lower = user_input.lower()
        
        # Simple pattern matching for common queries
        if any(word in user_lower for word in ["سلام", "درود", "صبح بخیر"]):
            return "سلام! چطور می‌تونم کمکتون کنم؟"
        elif any(word in user_lower for word in ["چراغ", "لامپ"]):
            if "روشن" in user_lower:
                return "چراغ را روشن می‌کنم."
            elif "خاموش" in user_lower:
                return "چراغ را خاموش می‌کنم."
            else:
                return "می‌خواهید چراغ را روشن کنم یا خاموش؟"
        elif any(word in user_lower for word in ["ساعت", "زمان"]):
            import datetime
            now = datetime.datetime.now()
            return f"الان ساعت {now.strftime('%H:%M')} است."
        elif any(word in user_lower for word in ["کمک", "راهنما"]):
            return "من استیو هستم. می‌تونم چراغ‌ها رو کنترل کنم و به سوالاتتون جواب بدم."
        else:
            return "متاسفم، الان نمی‌تونم به این سوال جواب بدم. لطفاً دوباره امتحان کنید."
    
    async def analyze_intent(self, user_input: str) -> Dict[str, Any]:
        """Analyze user intent from Persian input"""
        try:
            intent_prompt = f"""
کاربر این جمله را گفته: "{user_input}"

لطفاً قصد کاربر را تشخیص دهید و در قالب JSON پاسخ دهید:
{{
    "intent": "device_control|question|greeting|help|other",
    "action": "turn_on|turn_off|get_info|none",
    "device": "light|outlet|fan|tv|none",
    "confidence": 0.0-1.0
}}
"""
            
            messages = [
                {"role": "system", "content": "شما یک تحلیلگر قصد برای دستیار صوتی فارسی هستید."},
                {"role": "user", "content": intent_prompt}
            ]
            
            response = await self._call_llm(messages)
            
            # Parse JSON response
            import json
            intent_data = json.loads(response)
            
            return intent_data
            
        except Exception as e:
            logger.error(f"Intent analysis failed: {e}")
            return {
                "intent": "other",
                "action": "none", 
                "device": "none",
                "confidence": 0.0
            }
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get LLM performance statistics"""
        return {
            "provider": self.current_provider,
            "model": self.model_name,
            "response_stats": self.response_stats,
            "conversation_length": len(self.conversation_history),
            "available_clients": list(self.clients.keys())
        }
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
    
    async def cleanup(self):
        """Clean up LLM resources"""
        try:
            # Close any persistent connections
            self.clients.clear()
            self.conversation_history.clear()
            
            logger.info("LLM manager cleanup completed")
            
        except Exception as e:
            logger.error(f"LLM cleanup error: {e}")