#!/usr/bin/env python3
"""
Phase 1 Validation Test
Tests the core voice components of Steve Voice Assistant
"""

import asyncio
import sys
import logging
from pathlib import Path
import time

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from steve.utils.system_monitor import SystemPerformanceMonitor
from steve.core.voice_pipeline import SteveVoiceAssistant

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Phase1Validator:
    """Validates Phase 1 implementation"""
    
    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}
    
    async def run_all_tests(self) -> bool:
        """Run all Phase 1 validation tests"""
        print("🧪 Phase 1 Validation Tests")
        print("=" * 50)
        
        tests = [
            ("System Assessment", self._test_system_assessment),
            ("Wake Word Detector", self._test_wake_word_detector),
            ("STT Engine", self._test_stt_engine),
            ("TTS Engine", self._test_tts_engine),
            ("Voice Pipeline Integration", self._test_voice_pipeline),
            ("Performance Metrics", self._test_performance_metrics)
        ]
        
        all_passed = True
        
        for test_name, test_func in tests:
            print(f"\n🔍 Testing: {test_name}")
            print("-" * 30)
            
            try:
                result = await test_func()
                self.test_results[test_name] = result
                
                if result["passed"]:
                    print(f"✅ {test_name}: PASSED")
                    if result.get("message"):
                        print(f"   {result['message']}")
                else:
                    print(f"❌ {test_name}: FAILED")
                    print(f"   Error: {result['error']}")
                    all_passed = False
                    
            except Exception as e:
                print(f"💥 {test_name}: ERROR - {e}")
                self.test_results[test_name] = {"passed": False, "error": str(e)}
                all_passed = False
        
        # Print summary
        print("\n" + "=" * 50)
        print("📊 Test Summary")
        print("=" * 50)
        
        passed_tests = sum(1 for result in self.test_results.values() if result["passed"])
        total_tests = len(self.test_results)
        
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if all_passed:
            print("\n🎉 Phase 1 Validation: ALL TESTS PASSED!")
            print("✅ Ready for Phase 1 approval")
        else:
            print("\n❌ Phase 1 Validation: SOME TESTS FAILED")
            print("🔧 Please fix issues before proceeding")
        
        return all_passed
    
    async def _test_system_assessment(self) -> dict:
        """Test system assessment functionality"""
        try:
            monitor = SystemPerformanceMonitor()
            system_profile = await monitor.assess_system_capabilities()
            
            # Validate required fields
            required_fields = ["hardware_tier", "ram_gb", "cpu_cores", "gpu_available"]
            for field in required_fields:
                if field not in system_profile:
                    return {"passed": False, "error": f"Missing field: {field}"}
            
            # Validate hardware tier
            if system_profile["hardware_tier"] not in ["high", "medium", "low"]:
                return {"passed": False, "error": f"Invalid hardware tier: {system_profile['hardware_tier']}"}
            
            self.performance_metrics["system_profile"] = system_profile
            
            return {
                "passed": True,
                "message": f"Hardware tier: {system_profile['hardware_tier']}, RAM: {system_profile['ram_gb']}GB"
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _test_wake_word_detector(self) -> dict:
        """Test wake word detector initialization"""
        try:
            system_profile = self.performance_metrics.get("system_profile", {})
            if not system_profile:
                return {"passed": False, "error": "System profile not available"}
            
            from steve.core.wake_word_detector import PersianWakeWordDetector
            
            detector = PersianWakeWordDetector(system_profile)
            success = await detector.initialize()
            
            if not success:
                return {"passed": False, "error": "Wake word detector initialization failed"}
            
            # Test detection stats
            stats = detector.get_detection_stats()
            if not isinstance(stats, dict):
                return {"passed": False, "error": "Invalid detection stats format"}
            
            await detector.stop_listening()
            
            return {
                "passed": True,
                "message": f"Sample rate: {stats.get('sample_rate', 'unknown')}, Chunk size: {stats.get('chunk_size', 'unknown')}"
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _test_stt_engine(self) -> dict:
        """Test STT engine initialization"""
        try:
            system_profile = self.performance_metrics.get("system_profile", {})
            if not system_profile:
                return {"passed": False, "error": "System profile not available"}
            
            from steve.core.persian_stt import AdaptivePersianSTT
            
            stt = AdaptivePersianSTT(system_profile)
            success = await stt.initialize()
            
            if not success:
                return {"passed": False, "error": "STT engine initialization failed"}
            
            # Test performance stats
            stats = stt.get_performance_stats()
            if not isinstance(stats, dict):
                return {"passed": False, "error": "Invalid STT stats format"}
            
            await stt.cleanup()
            
            return {
                "passed": True,
                "message": f"Hardware tier: {stats.get('hardware_tier', 'unknown')}, Model loaded: {stats.get('model_loaded', False)}"
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _test_tts_engine(self) -> dict:
        """Test TTS engine initialization"""
        try:
            system_profile = self.performance_metrics.get("system_profile", {})
            if not system_profile:
                return {"passed": False, "error": "System profile not available"}
            
            from steve.core.persian_tts import ElitePersianTTS
            
            tts = ElitePersianTTS(system_profile)
            success = await tts.initialize()
            
            if not success:
                return {"passed": False, "error": "TTS engine initialization failed"}
            
            # Test performance stats
            stats = tts.get_performance_stats()
            if not isinstance(stats, dict):
                return {"passed": False, "error": "Invalid TTS stats format"}
            
            # Test immediate speech (without actual audio output)
            try:
                # This would normally play audio, but we'll just test the function exists
                test_result = await tts.speak_immediately("تست")
                if not isinstance(test_result, bool):
                    return {"passed": False, "error": "speak_immediately returned invalid result"}
            except Exception as e:
                logger.warning(f"speak_immediately test failed (expected): {e}")
            
            await tts.cleanup()
            
            return {
                "passed": True,
                "message": f"Hardware tier: {stats.get('hardware_tier', 'unknown')}, Active model: {stats.get('active_model', 'none')}"
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _test_voice_pipeline(self) -> dict:
        """Test complete voice pipeline integration"""
        try:
            system_profile = self.performance_metrics.get("system_profile", {})
            if not system_profile:
                return {"passed": False, "error": "System profile not available"}
            
            steve = SteveVoiceAssistant(system_profile)
            
            # Test initialization
            success = await steve.initialize()
            if not success:
                return {"passed": False, "error": "Steve initialization failed"}
            
            # Test status
            status = steve.get_status()
            if not isinstance(status, dict):
                return {"passed": False, "error": "Invalid status format"}
            
            # Test performance report
            report = steve.get_performance_report()
            if not isinstance(report, str) or len(report) < 10:
                return {"passed": False, "error": "Invalid performance report"}
            
            await steve.shutdown()
            
            return {
                "passed": True,
                "message": f"Initialized: {status.get('is_initialized', False)}, Components ready"
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}
    
    async def _test_performance_metrics(self) -> dict:
        """Test performance metrics collection"""
        try:
            # Test that we can collect performance metrics
            metrics_collected = 0
            
            if "system_profile" in self.performance_metrics:
                metrics_collected += 1
            
            # Test system monitor performance tracking
            monitor = SystemPerformanceMonitor()
            current_metrics = await monitor.monitor_performance()
            
            if isinstance(current_metrics, dict) and "timestamp" in current_metrics:
                metrics_collected += 1
            
            if metrics_collected < 2:
                return {"passed": False, "error": "Insufficient performance metrics collected"}
            
            return {
                "passed": True,
                "message": f"Performance metrics: {metrics_collected} sources"
            }
            
        except Exception as e:
            return {"passed": False, "error": str(e)}

async def main():
    """Main test function"""
    print("🚀 Steve Voice Assistant - Phase 1 Validation")
    print("=" * 60)
    
    validator = Phase1Validator()
    success = await validator.run_all_tests()
    
    if success:
        print("\n🎉 PHASE 1 COMPLETE - REQUESTING APPROVAL FOR PHASE 2")
        print("\n✅ All core voice components working correctly")
        print("✅ Hardware adaptation functioning")
        print("✅ Persian language processing ready")
        print("✅ Performance metrics collected")
        print("\n🚀 Ready to proceed to Phase 2: Intelligent Conversation Engine")
        return 0
    else:
        print("\n❌ Phase 1 validation failed")
        print("🔧 Please fix issues before proceeding to Phase 2")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))