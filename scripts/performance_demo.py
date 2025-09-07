#!/usr/bin/env python3
"""
Performance Monitoring Demonstration
Shows how performance monitoring is added as overlay without changing core logic
"""

import asyncio
import time
import sys
import random
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from steve.utils.performance_monitor import (
    monitor_performance,
    monitor_performance_async,
    PerformanceContext,
    start_performance_monitoring,
    stop_performance_monitoring,
    get_performance_summary,
    get_component_performance,
    export_performance_metrics,
    global_performance_monitor
)

def demo_sync_monitoring():
    """Demonstrate synchronous function monitoring"""
    print("🔄 Synchronous Function Monitoring Demo")
    print("-" * 40)
    
    @monitor_performance("TTS", track_resources=True)
    def simulate_tts_synthesis(text: str, voice: str = "default"):
        """Simulate TTS synthesis with variable performance"""
        # Simulate processing time based on text length
        processing_time = len(text) * 0.01 + random.uniform(0.1, 0.5)
        time.sleep(processing_time)
        
        # Simulate occasional failures
        if random.random() < 0.1:  # 10% failure rate
            raise Exception("TTS synthesis failed")
        
        return f"Synthesized: {text[:20]}..."
    
    @monitor_performance("TTS", track_resources=True)
    def simulate_tts_voice_loading(voice_model: str):
        """Simulate voice model loading"""
        # Simulate model loading time
        time.sleep(random.uniform(0.2, 0.8))
        return f"Loaded voice model: {voice_model}"
    
    # Run multiple TTS operations
    texts = [
        "سلام، من استیو هستم",
        "امروز هوا چطور است؟",
        "لطفاً چراغ‌های خانه را روشن کنید",
        "موسیقی آرام‌بخش پخش کنید",
        "فردا جلسه مهمی دارم"
    ]
    
    voices = ["female_persian", "male_persian", "neutral"]
    
    print("🎤 Running TTS operations...")
    for i, text in enumerate(texts):
        try:
            voice = voices[i % len(voices)]
            
            # Load voice model (first time)
            if i % 3 == 0:
                result = simulate_tts_voice_loading(voice)
                print(f"   Voice Loading {i+1}: {result}")
            
            # Synthesize speech
            result = simulate_tts_synthesis(text, voice)
            print(f"   TTS Operation {i+1}: {result}")
            
        except Exception as e:
            print(f"   TTS Operation {i+1}: Failed - {e}")

async def demo_async_monitoring():
    """Demonstrate asynchronous function monitoring"""
    print("\n🎧 Asynchronous Function Monitoring Demo")
    print("-" * 40)
    
    @monitor_performance_async("STT", track_resources=True)
    async def simulate_stt_transcription(audio_duration: float):
        """Simulate STT transcription with variable performance"""
        # Simulate processing time (real-time factor)
        processing_time = audio_duration * random.uniform(0.3, 0.8)
        await asyncio.sleep(processing_time)
        
        # Simulate occasional failures
        if random.random() < 0.05:  # 5% failure rate
            raise Exception("STT transcription failed")
        
        return f"Transcribed {audio_duration}s audio"
    
    @monitor_performance_async("STT", track_resources=True)
    async def simulate_stt_model_loading():
        """Simulate STT model loading"""
        await asyncio.sleep(random.uniform(0.5, 1.2))
        return "STT model loaded"
    
    print("🎧 Running STT operations...")
    
    # Load STT model
    try:
        result = await simulate_stt_model_loading()
        print(f"   Model Loading: {result}")
    except Exception as e:
        print(f"   Model Loading: Failed - {e}")
    
    # Run multiple transcription operations
    audio_durations = [2.5, 1.8, 4.2, 3.1, 2.9, 5.0]
    
    for i, duration in enumerate(audio_durations):
        try:
            result = await simulate_stt_transcription(duration)
            print(f"   STT Operation {i+1}: {result}")
        except Exception as e:
            print(f"   STT Operation {i+1}: Failed - {e}")

def demo_context_monitoring():
    """Demonstrate context-based monitoring"""
    print("\n📊 Context-Based Monitoring Demo")
    print("-" * 40)
    
    # Simulate voice pipeline processing
    with PerformanceContext("voice_pipeline_init", "VoicePipeline"):
        print("   🔧 Initializing voice pipeline...")
        time.sleep(0.3)
    
    with PerformanceContext("wake_word_detection", "VoicePipeline"):
        print("   👂 Detecting wake word...")
        time.sleep(0.1)
    
    with PerformanceContext("audio_preprocessing", "VoicePipeline"):
        print("   🎵 Preprocessing audio...")
        time.sleep(0.2)
    
    with PerformanceContext("intent_recognition", "VoicePipeline"):
        print("   🧠 Recognizing intent...")
        time.sleep(0.4)
    
    with PerformanceContext("response_generation", "VoicePipeline"):
        print("   💬 Generating response...")
        time.sleep(0.3)
    
    print("   ✅ Voice pipeline processing completed")

def demo_smart_home_monitoring():
    """Demonstrate smart home component monitoring"""
    print("\n🏠 Smart Home Monitoring Demo")
    print("-" * 40)
    
    @monitor_performance("SmartHome", track_resources=False)
    def simulate_device_discovery():
        """Simulate device discovery"""
        time.sleep(random.uniform(0.5, 1.5))
        return f"Found {random.randint(3, 8)} devices"
    
    @monitor_performance("SmartHome", track_resources=False)
    def simulate_device_control(device: str, action: str):
        """Simulate device control"""
        time.sleep(random.uniform(0.1, 0.3))
        
        # Simulate network issues
        if random.random() < 0.15:  # 15% failure rate
            raise Exception(f"Network timeout controlling {device}")
        
        return f"{device} {action} successful"
    
    devices = ["living_room_lights", "bedroom_ac", "kitchen_tv", "front_door_lock"]
    actions = ["turn_on", "turn_off", "adjust", "status_check"]
    
    print("🔍 Running device discovery...")
    try:
        result = simulate_device_discovery()
        print(f"   Discovery: {result}")
    except Exception as e:
        print(f"   Discovery: Failed - {e}")
    
    print("🎛️  Running device control operations...")
    for i in range(8):
        device = random.choice(devices)
        action = random.choice(actions)
        
        try:
            result = simulate_device_control(device, action)
            print(f"   Control {i+1}: {result}")
        except Exception as e:
            print(f"   Control {i+1}: Failed - {e}")

def show_performance_metrics():
    """Display collected performance metrics"""
    print("\n📈 Performance Metrics Summary")
    print("=" * 60)
    
    # Overall summary
    summary = get_performance_summary()
    print(f"📊 Overall Performance:")
    print(f"   Total Functions Monitored: {summary['total_functions_monitored']}")
    print(f"   Total Function Calls: {summary['total_function_calls']}")
    print(f"   Total Execution Time: {summary['total_execution_time']:.2f}s")
    print(f"   Average Call Time: {summary['average_call_time']:.3f}s")
    
    # Component breakdown
    print(f"\n🏗️  Component Breakdown:")
    for component, stats in summary['component_breakdown'].items():
        avg_time = stats['time'] / stats['calls'] if stats['calls'] > 0 else 0
        print(f"   {component}:")
        print(f"     Functions: {stats['functions']}")
        print(f"     Total Calls: {stats['calls']}")
        print(f"     Total Time: {stats['time']:.2f}s")
        print(f"     Avg Time/Call: {avg_time:.3f}s")
    
    # Slowest functions
    print(f"\n🐌 Slowest Functions:")
    for func_key, avg_time in summary['slowest_functions'][:5]:
        print(f"   {func_key}: {avg_time:.3f}s average")
    
    # Component-specific metrics
    components = ["TTS", "STT", "VoicePipeline", "SmartHome"]
    for component in components:
        metrics = get_component_performance(component)
        if metrics:
            print(f"\n🔧 {component} Component Metrics:")
            for func_name, metric in metrics.items():
                success_rate = metric.success_rate * 100
                print(f"   {func_name}:")
                print(f"     Calls: {metric.call_count}")
                print(f"     Success Rate: {success_rate:.1f}%")
                print(f"     Avg Time: {metric.average_time:.3f}s")
                print(f"     Throughput: {metric.throughput_per_second:.1f} ops/sec")

async def main():
    """Run all performance monitoring demonstrations"""
    print("⚡ Performance Monitoring Demonstration")
    print("=" * 60)
    print("ℹ️  This demo shows performance monitoring overlays")
    print("   that don't change existing core logic")
    print("=" * 60)
    
    # Start resource monitoring
    start_performance_monitoring(resource_interval=2.0)
    print("🚀 Background resource monitoring started")
    
    try:
        # Run demonstrations
        demo_sync_monitoring()
        await demo_async_monitoring()
        demo_context_monitoring()
        demo_smart_home_monitoring()
        
        # Wait a bit for resource monitoring
        print("\n⏱️  Collecting resource metrics...")
        await asyncio.sleep(3)
        
        # Show metrics
        show_performance_metrics()
        
        # Export metrics
        export_path = "logs/demo_performance_metrics.json"
        export_performance_metrics(export_path)
        print(f"\n💾 Performance metrics exported to {export_path}")
        
    finally:
        # Stop monitoring
        stop_performance_monitoring()
        print("🛑 Background resource monitoring stopped")
    
    print("\n" + "=" * 60)
    print("✅ Performance monitoring demonstration completed!")
    print("\n📋 Monitoring Features Demonstrated:")
    print("• Function-level performance tracking")
    print("• Async function monitoring")
    print("• Context-based code block monitoring")
    print("• Resource usage tracking")
    print("• Success rate and error tracking")
    print("• Throughput measurement")
    print("• Performance analytics and reporting")
    print("• Metrics export for analysis")
    print("\n🎯 All monitoring is non-intrusive:")
    print("• No changes to existing function logic")
    print("• Decorators preserve original behavior")
    print("• Context managers add monitoring only")
    print("• Background monitoring doesn't affect performance")

if __name__ == "__main__":
    asyncio.run(main())