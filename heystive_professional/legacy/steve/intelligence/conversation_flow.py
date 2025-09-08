"""
Persian Conversation Flow Manager
Handles natural Persian dialogue flow and context management
"""

import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Tuple
from enum import Enum
import json

logger = logging.getLogger(__name__)

class ConversationState(Enum):
    """Conversation states for flow management"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    RESPONDING = "responding"
    WAITING_CONFIRMATION = "waiting_confirmation"
    DEVICE_CONTROL = "device_control"
    QUESTION_ANSWERING = "question_answering"

class PersianConversationFlow:
    """
    Advanced Persian conversation flow management
    Handles context, state transitions, and natural dialogue
    """
    
    def __init__(self, llm_manager, tts_engine, smart_home_controller=None):
        self.llm_manager = llm_manager
        self.tts_engine = tts_engine
        self.smart_home_controller = smart_home_controller
        
        # Conversation state
        self.current_state = ConversationState.IDLE
        self.conversation_context = {}
        self.pending_actions = []
        
        # Persian language patterns
        self.persian_patterns = self._initialize_persian_patterns()
        
        # Response templates
        self.response_templates = self._load_response_templates()
        
        # Performance tracking
        self.flow_stats = {
            "total_conversations": 0,
            "successful_completions": 0,
            "average_turns": 0.0,
            "context_accuracy": 0.0
        }
    
    def _initialize_persian_patterns(self) -> Dict[str, List[str]]:
        """Initialize Persian language patterns for intent recognition"""
        return {
            "greetings": [
                "سلام", "درود", "صبح بخیر", "عصر بخیر", "شب بخیر",
                "سلام علیکم", "احوال", "چطوری", "حالت چطوره"
            ],
            "device_control": {
                "lights": ["چراغ", "لامپ", "نور", "روشنایی"],
                "outlets": ["پریز", "برق", "دوشاخه"],
                "fans": ["پنکه", "فن", "باد"],
                "tv": ["تلویزیون", "تی وی", "تلوزیون"]
            },
            "actions": {
                "turn_on": ["روشن", "باز", "فعال", "استارت"],
                "turn_off": ["خاموش", "بسته", "غیرفعال", "استاپ"],
                "increase": ["بیشتر", "زیاد", "افزایش", "بالا"],
                "decrease": ["کمتر", "کم", "کاهش", "پایین"]
            },
            "questions": [
                "چی", "چه", "کی", "کجا", "چطور", "چرا", "کدام",
                "ساعت", "زمان", "تاریخ", "آب و هوا", "هوا"
            ],
            "confirmations": {
                "yes": ["بله", "آره", "درسته", "همین", "باشه", "اوکی"],
                "no": ["نه", "نخیر", "غلطه", "اشتباه", "نمی‌خوام"]
            },
            "help": ["کمک", "راهنما", "چیکار", "قابلیت", "می‌تونی"]
        }
    
    def _load_response_templates(self) -> Dict[str, List[str]]:
        """Load Persian response templates"""
        return {
            "greeting_responses": [
                "سلام! چطور می‌تونم کمکتون کنم؟",
                "درود! چه کاری برات انجام بدم؟",
                "سلام عزیز! در خدمتم."
            ],
            "device_success": [
                "{device} {action} شد.",
                "انجام شد. {device} رو {action} کردم.",
                "باشه، {device} {action} شد."
            ],
            "device_error": [
                "متاسفم، نتونستم {device} رو {action} کنم.",
                "مشکلی پیش اومده. {device} {action} نشد.",
                "خطا در {action} کردن {device}."
            ],
            "confirmation_requests": [
                "می‌خوای {device} رو {action} کنم؟",
                "آیا مطمئنی که {device} {action} بشه؟",
                "تأیید می‌کنی که {device} {action} شود؟"
            ],
            "clarification_requests": [
                "متوجه نشدم. می‌تونی دوباره بگی؟",
                "کدوم دستگاه رو می‌گی؟",
                "منظورت چیه دقیقاً؟"
            ],
            "help_responses": [
                "می‌تونم چراغ‌ها و وسایل برقی رو کنترل کنم، به سوالاتت جواب بدم.",
                "قابلیت‌هام شامل کنترل خانه هوشمند و پاسخ به سوالات عمومیه.",
                "می‌تونی ازم بخوای چراغ روشن کنم، سوال بپرسی، یا کمک بخوای."
            ]
        }
    
    async def process_user_input(self, user_input: str) -> str:
        """
        Process user input and manage conversation flow
        
        Args:
            user_input: Persian text from user
            
        Returns:
            Persian response text
        """
        try:
            logger.info(f"Processing user input: '{user_input}' in state: {self.current_state}")
            
            # Update conversation stats
            self.flow_stats["total_conversations"] += 1
            
            # Analyze user intent
            intent_data = await self._analyze_persian_intent(user_input)
            
            # Update conversation context
            self._update_context(user_input, intent_data)
            
            # Process based on current state and intent
            response = await self._handle_conversation_turn(user_input, intent_data)
            
            # Update state based on response
            self._update_conversation_state(intent_data, response)
            
            logger.info(f"Generated response: '{response}' - New state: {self.current_state}")
            return response
            
        except Exception as e:
            logger.error(f"Conversation processing failed: {e}")
            return "متاسفم، مشکلی پیش اومده. لطفاً دوباره امتحان کنید."
    
    async def _analyze_persian_intent(self, user_input: str) -> Dict[str, Any]:
        """Analyze Persian user intent using pattern matching and LLM"""
        try:
            # First, try pattern matching for speed
            pattern_intent = self._pattern_match_intent(user_input)
            
            # If pattern matching is confident, use it
            if pattern_intent["confidence"] > 0.8:
                return pattern_intent
            
            # Otherwise, use LLM for more complex analysis
            llm_intent = await self.llm_manager.analyze_intent(user_input)
            
            # Combine results
            combined_intent = self._combine_intent_results(pattern_intent, llm_intent)
            
            return combined_intent
            
        except Exception as e:
            logger.error(f"Intent analysis failed: {e}")
            return {"intent": "other", "confidence": 0.0, "entities": {}}
    
    def _pattern_match_intent(self, user_input: str) -> Dict[str, Any]:
        """Fast pattern matching for common Persian intents"""
        user_lower = user_input.lower()
        intent_data = {
            "intent": "other",
            "confidence": 0.0,
            "entities": {},
            "action": None,
            "device": None
        }
        
        # Check for greetings
        if any(greeting in user_lower for greeting in self.persian_patterns["greetings"]):
            intent_data.update({
                "intent": "greeting",
                "confidence": 0.9
            })
            return intent_data
        
        # Check for help requests
        if any(help_word in user_lower for help_word in self.persian_patterns["help"]):
            intent_data.update({
                "intent": "help",
                "confidence": 0.9
            })
            return intent_data
        
        # Check for device control
        device_found = None
        action_found = None
        
        # Find device
        for device_type, device_words in self.persian_patterns["device_control"].items():
            if any(word in user_lower for word in device_words):
                device_found = device_type
                break
        
        # Find action
        for action_type, action_words in self.persian_patterns["actions"].items():
            if any(word in user_lower for word in action_words):
                action_found = action_type
                break
        
        if device_found and action_found:
            intent_data.update({
                "intent": "device_control",
                "confidence": 0.85,
                "device": device_found,
                "action": action_found,
                "entities": {
                    "device": device_found,
                    "action": action_found
                }
            })
            return intent_data
        
        # Check for questions
        if any(question_word in user_lower for question_word in self.persian_patterns["questions"]):
            intent_data.update({
                "intent": "question",
                "confidence": 0.7
            })
            return intent_data
        
        # Check for confirmations (if waiting for confirmation)
        if self.current_state == ConversationState.WAITING_CONFIRMATION:
            if any(yes_word in user_lower for yes_word in self.persian_patterns["confirmations"]["yes"]):
                intent_data.update({
                    "intent": "confirmation",
                    "confirmation": True,
                    "confidence": 0.9
                })
                return intent_data
            elif any(no_word in user_lower for no_word in self.persian_patterns["confirmations"]["no"]):
                intent_data.update({
                    "intent": "confirmation",
                    "confirmation": False,
                    "confidence": 0.9
                })
                return intent_data
        
        return intent_data
    
    def _combine_intent_results(self, pattern_result: Dict, llm_result: Dict) -> Dict[str, Any]:
        """Combine pattern matching and LLM intent results"""
        # If pattern matching is confident, prefer it for speed
        if pattern_result["confidence"] > 0.8:
            return pattern_result
        
        # If LLM is more confident, use it
        if llm_result.get("confidence", 0) > pattern_result["confidence"]:
            return llm_result
        
        # Default to pattern result
        return pattern_result
    
    async def _handle_conversation_turn(self, user_input: str, intent_data: Dict[str, Any]) -> str:
        """Handle conversation turn based on intent and state"""
        intent = intent_data.get("intent", "other")
        
        if intent == "greeting":
            return await self._handle_greeting()
        
        elif intent == "help":
            return await self._handle_help_request()
        
        elif intent == "device_control":
            return await self._handle_device_control(intent_data)
        
        elif intent == "question":
            return await self._handle_question(user_input)
        
        elif intent == "confirmation":
            return await self._handle_confirmation(intent_data)
        
        else:
            return await self._handle_general_conversation(user_input)
    
    async def _handle_greeting(self) -> str:
        """Handle greeting interactions"""
        import random
        response = random.choice(self.response_templates["greeting_responses"])
        self.current_state = ConversationState.IDLE
        return response
    
    async def _handle_help_request(self) -> str:
        """Handle help requests"""
        import random
        response = random.choice(self.response_templates["help_responses"])
        self.current_state = ConversationState.IDLE
        return response
    
    async def _handle_device_control(self, intent_data: Dict[str, Any]) -> str:
        """Handle smart home device control"""
        try:
            device = intent_data.get("device")
            action = intent_data.get("action")
            
            if not device or not action:
                return "کدوم دستگاه رو می‌خوای کنترل کنم؟"
            
            # Check if we need confirmation for this action
            if self._needs_confirmation(device, action):
                self.pending_actions.append({"device": device, "action": action})
                self.current_state = ConversationState.WAITING_CONFIRMATION
                
                device_persian = self._translate_device_to_persian(device)
                action_persian = self._translate_action_to_persian(action)
                
                import random
                template = random.choice(self.response_templates["confirmation_requests"])
                return template.format(device=device_persian, action=action_persian)
            
            # Execute device control immediately
            return await self._execute_device_control(device, action)
            
        except Exception as e:
            logger.error(f"Device control handling failed: {e}")
            return "مشکلی در کنترل دستگاه پیش اومده."
    
    async def _handle_question(self, user_input: str) -> str:
        """Handle general questions"""
        try:
            # Use LLM for question answering
            context = self._get_current_context()
            response = await self.llm_manager.generate_persian_response(user_input, context)
            
            self.current_state = ConversationState.IDLE
            return response
            
        except Exception as e:
            logger.error(f"Question handling failed: {e}")
            return "متاسفم، الان نمی‌تونم به این سوال جواب بدم."
    
    async def _handle_confirmation(self, intent_data: Dict[str, Any]) -> str:
        """Handle confirmation responses"""
        try:
            confirmation = intent_data.get("confirmation", False)
            
            if confirmation and self.pending_actions:
                # Execute pending action
                action_data = self.pending_actions.pop(0)
                response = await self._execute_device_control(
                    action_data["device"], 
                    action_data["action"]
                )
                self.current_state = ConversationState.IDLE
                return response
            else:
                # User declined or no pending actions
                self.pending_actions.clear()
                self.current_state = ConversationState.IDLE
                return "باشه، کاری انجام نمی‌دم."
                
        except Exception as e:
            logger.error(f"Confirmation handling failed: {e}")
            self.current_state = ConversationState.IDLE
            return "متاسفم، مشکلی پیش اومده."
    
    async def _handle_general_conversation(self, user_input: str) -> str:
        """Handle general conversation using LLM"""
        try:
            context = self._get_current_context()
            response = await self.llm_manager.generate_persian_response(user_input, context)
            
            self.current_state = ConversationState.IDLE
            return response
            
        except Exception as e:
            logger.error(f"General conversation failed: {e}")
            return "متوجه نشدم. می‌تونی دوباره بگی؟"
    
    async def _execute_device_control(self, device: str, action: str) -> str:
        """Execute smart home device control"""
        try:
            if not self.smart_home_controller:
                return "کنترل خانه هوشمند فعال نیست."
            
            # Map to Persian command
            device_persian = self._translate_device_to_persian(device)
            action_persian = self._translate_action_to_persian(action)
            
            # Create Persian command
            persian_command = f"{device_persian} را {action_persian} کن"
            
            # Execute command
            result = await self.smart_home_controller.control_device_by_persian_command(persian_command)
            
            if "پیدا نشد" in result or "خطا" in result:
                import random
                template = random.choice(self.response_templates["device_error"])
                return template.format(device=device_persian, action=action_persian)
            else:
                import random
                template = random.choice(self.response_templates["device_success"])
                return template.format(device=device_persian, action=action_persian)
                
        except Exception as e:
            logger.error(f"Device control execution failed: {e}")
            return f"مشکلی در کنترل {device} پیش اومده."
    
    def _needs_confirmation(self, device: str, action: str) -> bool:
        """Check if device control needs user confirmation"""
        # For now, don't require confirmation for basic light controls
        # In production, you might want confirmation for critical devices
        return False
    
    def _translate_device_to_persian(self, device: str) -> str:
        """Translate device type to Persian"""
        translations = {
            "light": "چراغ",
            "lights": "چراغ",
            "outlet": "پریز", 
            "outlets": "پریز",
            "fan": "پنکه",
            "fans": "پنکه",
            "tv": "تلویزیون"
        }
        return translations.get(device, device)
    
    def _translate_action_to_persian(self, action: str) -> str:
        """Translate action to Persian"""
        translations = {
            "turn_on": "روشن",
            "turn_off": "خاموش",
            "increase": "زیاد",
            "decrease": "کم"
        }
        return translations.get(action, action)
    
    def _update_context(self, user_input: str, intent_data: Dict[str, Any]):
        """Update conversation context"""
        self.conversation_context.update({
            "last_user_input": user_input,
            "last_intent": intent_data,
            "timestamp": time.time()
        })
        
        # Add device states if available
        if self.smart_home_controller:
            try:
                # This would get actual device states
                # For now, we'll use a placeholder
                self.conversation_context["device_states"] = {}
            except Exception as e:
                # NEW: Add logging to silent failure but keep same behavior
                logger.debug(f"Device state update failed (non-critical): {e}")
                pass
    
    def _get_current_context(self) -> Dict[str, Any]:
        """Get current conversation context"""
        context = self.conversation_context.copy()
        
        # Add current time
        import datetime
        context["time"] = datetime.datetime.now().strftime("%H:%M")
        
        return context
    
    def _update_conversation_state(self, intent_data: Dict[str, Any], response: str):
        """Update conversation state based on interaction"""
        intent = intent_data.get("intent", "other")
        
        if intent == "device_control" and "می‌خوای" in response:
            self.current_state = ConversationState.WAITING_CONFIRMATION
        elif self.current_state == ConversationState.WAITING_CONFIRMATION:
            if intent == "confirmation":
                self.current_state = ConversationState.IDLE
        else:
            self.current_state = ConversationState.IDLE
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get conversation flow statistics"""
        return {
            "current_state": self.current_state.value,
            "flow_stats": self.flow_stats,
            "context_size": len(self.conversation_context),
            "pending_actions": len(self.pending_actions)
        }
    
    def reset_conversation(self):
        """Reset conversation state"""
        self.current_state = ConversationState.IDLE
        self.conversation_context.clear()
        self.pending_actions.clear()
        logger.info("Conversation state reset")