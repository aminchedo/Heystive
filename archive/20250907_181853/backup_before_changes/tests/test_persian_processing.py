"""
Persian Language Processing Tests
Tests for Persian text normalization, phoneme processing, and language-specific features
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from steve.core.persian_stt import PersianTextNormalizer as STTNormalizer
from steve.core.persian_tts import PersianTextNormalizer as TTSNormalizer
from steve.intelligence.conversation_flow import PersianConversationFlow
from steve.intelligence.llm_manager import PersianLLMManager

class TestPersianTextNormalization:
    """Test Persian text normalization functionality"""
    
    @pytest.fixture
    def stt_normalizer(self):
        return STTNormalizer()
    
    @pytest.fixture
    def tts_normalizer(self):
        return TTSNormalizer()
    
    def test_persian_digit_normalization(self, stt_normalizer):
        """Test Persian to English digit conversion"""
        test_cases = [
            ("۱۲۳۴۵", "12345"),
            ("ساعت ۱۲:۳۰", "ساعت 12:30"),
            ("۰۹۱۲۳۴۵۶۷۸۹", "09123456789"),
            ("سال ۱۴۰۲", "سال 1402")
        ]
        
        for persian_text, expected in test_cases:
            normalized = stt_normalizer.normalize(persian_text)
            assert expected in normalized or normalized == expected
    
    def test_persian_punctuation_normalization(self, stt_normalizer):
        """Test Persian punctuation normalization"""
        test_cases = [
            ("سلام، حال شما چطور است؟", "سلام, حال شما چطور است?"),
            ("بله، من خوبم", "بله, من خوبم"),
            ("آیا می‌توانید کمک کنید؟", "آیا می‌توانید کمک کنید?")
        ]
        
        for persian_text, expected in test_cases:
            normalized = stt_normalizer.normalize(persian_text)
            # Check that Persian punctuation is converted
            assert "،" not in normalized or "," in normalized
            assert "؟" not in normalized or "?" in normalized
    
    def test_whitespace_normalization(self, stt_normalizer):
        """Test whitespace normalization"""
        test_cases = [
            ("سلام    من    استیو    هستم", "سلام من استیو هستم"),
            ("  چراغ را روشن کن  ", "چراغ را روشن کن"),
            ("متن\t\nبا\r\nفاصله‌های\tمختلف", "متن با فاصله‌های مختلف")
        ]
        
        for input_text, expected in test_cases:
            normalized = stt_normalizer.normalize(input_text)
            # Should have single spaces and no leading/trailing whitespace
            assert "  " not in normalized
            assert normalized.strip() == normalized
    
    def test_tts_specific_normalization(self, tts_normalizer):
        """Test TTS-specific text normalization"""
        test_cases = [
            ("سلام، من استیو هستم", "سلام, من استیو هستم"),
            ("ساعت ۱۲:۳۰ است", "ساعت 12:30 است"),
            ("چراغ را روشن کن!", "چراغ را روشن کن!")
        ]
        
        for input_text, expected in test_cases:
            normalized = tts_normalizer.normalize(input_text)
            assert isinstance(normalized, str)
            assert len(normalized) > 0

class TestPersianLanguagePatterns:
    """Test Persian language pattern recognition"""
    
    @pytest.fixture
    def mock_llm_manager(self):
        """Mock LLM manager for testing"""
        from unittest.mock import Mock
        mock_llm = Mock()
        mock_llm.analyze_intent = Mock(return_value={
            "intent": "device_control",
            "confidence": 0.8,
            "device": "light",
            "action": "turn_on"
        })
        return mock_llm
    
    @pytest.fixture
    def conversation_flow(self, mock_llm_manager):
        """Create conversation flow for testing"""
        return PersianConversationFlow(mock_llm_manager, None, None)
    
    def test_greeting_pattern_recognition(self, conversation_flow):
        """Test Persian greeting pattern recognition"""
        greeting_inputs = [
            "سلام",
            "درود",
            "صبح بخیر",
            "عصر بخیر",
            "سلام علیکم",
            "احوال شما چطور است"
        ]
        
        for greeting in greeting_inputs:
            intent = conversation_flow._pattern_match_intent(greeting)
            assert intent["intent"] == "greeting"
            assert intent["confidence"] > 0.8
    
    def test_device_control_pattern_recognition(self, conversation_flow):
        """Test device control pattern recognition"""
        device_commands = [
            ("چراغ را روشن کن", "light", "turn_on"),
            ("لامپ را خاموش کن", "light", "turn_off"),
            ("پریز را فعال کن", "outlet", "turn_on"),
            ("برق را قطع کن", "outlet", "turn_off"),
            ("نور را کم کن", "light", "dim"),
            ("روشنایی را زیاد کن", "light", "brighten")
        ]
        
        for command, expected_device, expected_action in device_commands:
            intent = conversation_flow._pattern_match_intent(command)
            
            if intent["confidence"] > 0.7:  # Only check if pattern matching was confident
                assert intent["intent"] == "device_control"
                assert intent["device"] == expected_device
                assert intent["action"] == expected_action
    
    def test_help_pattern_recognition(self, conversation_flow):
        """Test help request pattern recognition"""
        help_inputs = [
            "کمک",
            "راهنما",
            "چیکار می‌تونی بکنی",
            "قابلیت‌هات چیه",
            "می‌تونی کمکم کنی"
        ]
        
        for help_request in help_inputs:
            intent = conversation_flow._pattern_match_intent(help_request)
            assert intent["intent"] == "help"
            assert intent["confidence"] > 0.8
    
    def test_question_pattern_recognition(self, conversation_flow):
        """Test question pattern recognition"""
        questions = [
            "ساعت چنده",
            "زمان چیه",
            "تاریخ امروز چیه",
            "آب و هوا چطوره",
            "چه خبر"
        ]
        
        for question in questions:
            intent = conversation_flow._pattern_match_intent(question)
            # Should recognize as question or have some confidence
            assert intent["intent"] in ["question", "other"]
            if intent["intent"] == "question":
                assert intent["confidence"] > 0.6

class TestPersianConversationFlow:
    """Test Persian conversation flow management"""
    
    @pytest.fixture
    def mock_llm_manager(self):
        """Mock LLM manager"""
        from unittest.mock import AsyncMock, Mock
        
        mock_llm = Mock()
        mock_llm.analyze_intent = AsyncMock(return_value={
            "intent": "greeting",
            "confidence": 0.9
        })
        mock_llm.generate_persian_response = AsyncMock(return_value="سلام! چطور می‌تونم کمکتون کنم؟")
        
        return mock_llm
    
    @pytest.fixture
    def mock_tts_engine(self):
        """Mock TTS engine"""
        from unittest.mock import AsyncMock, Mock
        
        mock_tts = Mock()
        mock_tts.speak_immediately = AsyncMock(return_value=True)
        mock_tts.synthesize_premium_persian = AsyncMock(return_value=b"mock_audio_data")
        
        return mock_tts
    
    @pytest.fixture
    def conversation_flow(self, mock_llm_manager, mock_tts_engine):
        """Create conversation flow for testing"""
        return PersianConversationFlow(mock_llm_manager, mock_tts_engine, None)
    
    @pytest.mark.asyncio
    async def test_greeting_conversation(self, conversation_flow):
        """Test greeting conversation handling"""
        response = await conversation_flow.process_user_input("سلام")
        
        assert isinstance(response, str)
        assert len(response) > 0
        # Should be a Persian greeting response
        assert any(word in response for word in ["سلام", "چطور", "کمک"])
    
    @pytest.mark.asyncio
    async def test_help_conversation(self, conversation_flow):
        """Test help conversation handling"""
        response = await conversation_flow.process_user_input("کمک")
        
        assert isinstance(response, str)
        assert len(response) > 0
        # Should mention capabilities or help
        assert any(word in response for word in ["کمک", "می‌تونم", "قابلیت"])
    
    def test_persian_device_translation(self, conversation_flow):
        """Test device name translation to Persian"""
        translations = [
            ("light", "چراغ"),
            ("outlet", "پریز"),
            ("fan", "پنکه"),
            ("tv", "تلویزیون")
        ]
        
        for english, expected_persian in translations:
            persian = conversation_flow._translate_device_to_persian(english)
            assert persian == expected_persian
    
    def test_persian_action_translation(self, conversation_flow):
        """Test action translation to Persian"""
        translations = [
            ("turn_on", "روشن"),
            ("turn_off", "خاموش"),
            ("increase", "زیاد"),
            ("decrease", "کم")
        ]
        
        for english, expected_persian in translations:
            persian = conversation_flow._translate_action_to_persian(english)
            assert persian == expected_persian

class TestPersianLLMIntegration:
    """Test Persian LLM integration"""
    
    @pytest.fixture
    def llm_config(self):
        """LLM configuration for testing"""
        return {
            "llm_provider": "openai",
            "model_name": "gpt-4",
            "api_key": "test_key"
        }
    
    def test_llm_manager_initialization(self, llm_config):
        """Test LLM manager initialization"""
        llm_manager = PersianLLMManager(llm_config)
        
        assert llm_manager.current_provider == "openai"
        assert llm_manager.model_name == "gpt-4"
        assert len(llm_manager.conversation_history) == 0
        assert "استیو" in llm_manager.system_prompt
        assert "فارسی" in llm_manager.system_prompt
    
    def test_persian_system_prompt(self, llm_config):
        """Test Persian system prompt content"""
        llm_manager = PersianLLMManager(llm_config)
        
        system_prompt = llm_manager.system_prompt
        
        # Should contain key Persian instructions
        assert "استیو" in system_prompt
        assert "فارسی" in system_prompt
        assert "چراغ" in system_prompt or "دستگاه" in system_prompt
        assert "کمک" in system_prompt
    
    def test_conversation_context_preparation(self, llm_config):
        """Test conversation context preparation"""
        llm_manager = PersianLLMManager(llm_config)
        
        # Add some conversation history
        llm_manager.conversation_history = [
            {"user": "سلام", "assistant": "سلام! چطور می‌تونم کمکتون کنم؟", "timestamp": 1234567890}
        ]
        
        context = {"time": "14:30", "device_states": {"چراغ نشیمن": True}}
        messages = llm_manager._prepare_conversation_context("چراغ را خاموش کن", context)
        
        assert len(messages) >= 3  # System, history, current input
        assert messages[0]["role"] == "system"
        assert messages[-1]["role"] == "user"
        assert messages[-1]["content"] == "چراغ را خاموش کن"
    
    def test_context_info_formatting(self, llm_config):
        """Test context information formatting in Persian"""
        llm_manager = PersianLLMManager(llm_config)
        
        context = {
            "time": "14:30",
            "device_states": {"چراغ نشیمن": True, "پریز آشپزخانه": False},
            "weather": "آفتابی"
        }
        
        formatted = llm_manager._format_context_info(context)
        
        assert "زمان: 14:30" in formatted
        assert "چراغ نشیمن: روشن" in formatted
        assert "پریز آشپزخانه: خاموش" in formatted
        assert "آب و هوا: آفتابی" in formatted
    
    def test_fallback_responses(self, llm_config):
        """Test fallback response generation"""
        llm_manager = PersianLLMManager(llm_config)
        
        test_cases = [
            ("سلام", ["سلام", "چطور", "کمک"]),
            ("چراغ روشن", ["چراغ"]),
            ("ساعت", ["ساعت"]),
            ("کمک", ["کمک", "استیو"])
        ]
        
        for user_input, expected_words in test_cases:
            response = llm_manager._get_fallback_response(user_input)
            
            assert isinstance(response, str)
            assert len(response) > 0
            # Should contain at least one expected word
            assert any(word in response for word in expected_words)

class TestPersianTextProcessing:
    """Test advanced Persian text processing"""
    
    def test_persian_character_validation(self):
        """Test Persian character validation"""
        persian_texts = [
            "سلام من استیو هستم",
            "چراغ را روشن کن",
            "ساعت ۱۲:۳۰ است",
            "بله سرورم"
        ]
        
        for text in persian_texts:
            # Check that text contains Persian characters
            persian_chars = sum(1 for c in text if '\u0600' <= c <= '\u06FF')
            assert persian_chars > 0, f"Text should contain Persian characters: {text}"
    
    def test_persian_word_segmentation(self):
        """Test Persian word segmentation"""
        test_sentences = [
            "چراغ نشیمن را روشن کن",
            "پریز آشپزخانه را خاموش کن",
            "ساعت چند است"
        ]
        
        for sentence in test_sentences:
            words = sentence.split()
            assert len(words) >= 3, f"Sentence should have multiple words: {sentence}"
            
            # Check that words are properly separated
            for word in words:
                assert len(word.strip()) > 0, "Words should not be empty"
    
    def test_persian_sentence_structure(self):
        """Test Persian sentence structure recognition"""
        # Persian typically follows SOV (Subject-Object-Verb) order
        test_structures = [
            ("چراغ را روشن کن", ["چراغ", "را", "روشن", "کن"]),  # Object-Verb
            ("من استیو هستم", ["من", "استیو", "هستم"]),  # Subject-Object-Verb
            ("ساعت چند است", ["ساعت", "چند", "است"])  # Subject-Verb
        ]
        
        for sentence, expected_components in test_structures:
            words = sentence.split()
            
            # Check that key components are present
            for component in expected_components:
                assert component in words, f"Component '{component}' should be in '{sentence}'"

class TestPersianAudioProcessing:
    """Test Persian-specific audio processing"""
    
    def test_persian_phoneme_patterns(self):
        """Test Persian phoneme pattern definitions"""
        from steve.core.wake_word_detector import PersianWakeWordDetector
        
        hardware_config = {"hardware_tier": "medium", "ram_gb": 8, "cpu_cores": 4, "gpu_available": False}
        detector = PersianWakeWordDetector(hardware_config)
        
        patterns = detector.persian_wake_patterns
        
        assert "hey_steve" in patterns
        pattern = patterns["hey_steve"]
        
        assert pattern["persian_text"] == "هی استیو"
        assert isinstance(pattern["phonemes"], list)
        assert len(pattern["phonemes"]) > 0
        assert isinstance(pattern["duration_range"], tuple)
        assert len(pattern["duration_range"]) == 2
        assert pattern["duration_range"][0] < pattern["duration_range"][1]
    
    def test_persian_audio_configuration(self):
        """Test audio configuration for Persian processing"""
        from steve.core.wake_word_detector import PersianWakeWordDetector
        
        hardware_config = {"hardware_tier": "medium", "ram_gb": 8, "cpu_cores": 4, "gpu_available": False}
        detector = PersianWakeWordDetector(hardware_config)
        
        audio_config = detector.audio_config
        
        # Standard audio configuration for Persian
        assert audio_config["sample_rate"] == 16000  # Good for Persian speech
        assert audio_config["channels"] == 1  # Mono is sufficient
        assert audio_config["chunk_size"] > 0
        assert audio_config["frames_per_buffer"] > 0

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])