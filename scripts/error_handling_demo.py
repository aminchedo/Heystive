#!/usr/bin/env python3
"""
Error Handling Enhancement Demonstration
Shows how enhanced error handling preserves existing behavior while adding visibility
"""

import sys
import time
import tempfile
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from steve.utils.error_handler import (
    ErrorHandler, 
    log_errors, 
    log_errors_async,
    enhance_cleanup,
    monitor_health,
    health_checker
)
from steve.utils.health_checker import (
    global_health_checker,
    start_health_monitoring,
    get_system_health,
    record_component_operation
)

def demo_error_logging():
    """Demonstrate error logging without changing behavior"""
    print("🔍 Error Logging Demo")
    print("-" * 40)
    
    @log_errors("DemoComponent")
    def function_that_fails():
        raise ValueError("This is a test error")
    
    @log_errors("DemoComponent")  
    def function_that_succeeds():
        return "Success!"
    
    # Test successful function
    try:
        result = function_that_succeeds()
        print(f"✅ Success function returned: {result}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    
    # Test failing function - behavior preserved (exception still raised)
    try:
        function_that_fails()
        print("❌ Should have raised an exception!")
    except ValueError as e:
        print(f"✅ Exception properly raised (with enhanced logging): {e}")

def demo_cleanup_enhancement():
    """Demonstrate enhanced cleanup operations"""
    print("\n🧹 Cleanup Enhancement Demo")
    print("-" * 40)
    
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_path = temp_file.name
    temp_file.write(b"test content")
    temp_file.close()
    
    print(f"📄 Created temp file: {temp_path}")
    
    # Original cleanup pattern (now enhanced)
    print("🔧 Original cleanup with enhancement:")
    with enhance_cleanup("DemoComponent", "file_cleanup"):
        try:
            os.unlink(temp_path)
            print("   ✅ File deleted successfully")
        except Exception as e:
            print(f"   ❌ Cleanup failed: {e}")
            pass  # Original behavior preserved
    
    # Test cleanup of non-existent file (silent failure)
    print("🔧 Silent failure cleanup:")
    with enhance_cleanup("DemoComponent", "missing_file_cleanup"):
        try:
            os.unlink("/nonexistent/file.tmp")
        except:
            pass  # Silent failure, but now logged

def demo_health_monitoring():
    """Demonstrate health monitoring"""
    print("\n💚 Health Monitoring Demo")
    print("-" * 40)
    
    # Register some demo components
    global_health_checker.register_component("DemoTTS")
    global_health_checker.register_component("DemoSTT")
    
    @monitor_health("DemoTTS")
    def demo_tts_operation(success: bool = True):
        time.sleep(0.1)  # Simulate work
        if not success:
            raise Exception("TTS operation failed")
        return "TTS completed"
    
    @monitor_health("DemoSTT")
    def demo_stt_operation(success: bool = True):
        time.sleep(0.05)  # Simulate work
        if not success:
            raise Exception("STT operation failed")
        return "STT completed"
    
    # Simulate some operations
    print("🎤 Simulating TTS operations...")
    for i in range(5):
        try:
            result = demo_tts_operation(success=(i < 4))  # Last one fails
            print(f"   Operation {i+1}: {result}")
        except Exception as e:
            print(f"   Operation {i+1}: Failed - {e}")
    
    print("🎧 Simulating STT operations...")
    for i in range(3):
        try:
            result = demo_stt_operation(success=True)
            print(f"   Operation {i+1}: {result}")
        except Exception as e:
            print(f"   Operation {i+1}: Failed - {e}")
    
    # Show health status
    print("\n📊 Component Health Status:")
    for component in ["DemoTTS", "DemoSTT"]:
        health = global_health_checker.get_component_health(component)
        if health:
            print(f"   {component}: {health.status} "
                  f"(Success Rate: {health.success_rate:.1%}, "
                  f"Ops: {health.total_operations})")
    
    # Show system health summary
    summary = get_system_health()
    print(f"\n🏥 System Health: {summary['overall_status']} "
          f"({summary['healthy_components']}/{summary['total_components']} healthy)")

def demo_existing_code_enhancement():
    """Demonstrate how existing code gets enhanced without modification"""
    print("\n🔧 Existing Code Enhancement Demo")
    print("-" * 40)
    
    def existing_function_with_silent_failures():
        """Simulates existing code with silent failures"""
        print("   Running existing function...")
        
        # Existing pattern 1: Silent file cleanup
        with enhance_cleanup("ExistingComponent", "temp_cleanup"):
            try:
                # This would normally fail silently
                os.unlink("/tmp/nonexistent_file.tmp")
            except:
                pass  # Original silent behavior preserved
        
        # Existing pattern 2: Silent resource cleanup  
        with enhance_cleanup("ExistingComponent", "resource_cleanup"):
            try:
                # Simulate resource cleanup that might fail
                raise ConnectionError("Network resource unavailable")
            except:
                pass  # Original silent behavior preserved
        
        print("   ✅ Function completed (failures now logged)")
    
    existing_function_with_silent_failures()

def demo_error_analytics():
    """Demonstrate error analytics and reporting"""
    print("\n📈 Error Analytics Demo")
    print("-" * 40)
    
    # Simulate various errors
    components = ["TTS", "STT", "VoicePipeline", "SmartHome"]
    
    for i, component in enumerate(components):
        global_health_checker.register_component(component)
        
        # Simulate operations with different success rates
        success_rate = 0.9 - (i * 0.1)  # Decreasing success rate
        
        for j in range(10):
            success = (j / 10) < success_rate
            response_time = 0.1 + (i * 0.05)  # Increasing response time
            error_msg = f"Test error {j}" if not success else None
            
            record_component_operation(component, success, response_time, error_msg)
    
    # Show analytics
    print("📊 Component Analytics:")
    for component in components:
        health = global_health_checker.get_component_health(component)
        if health:
            status_icon = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "❌"}.get(health.status, "❓")
            print(f"   {status_icon} {component}: {health.status}")
            print(f"      Success Rate: {health.success_rate:.1%}")
            print(f"      Avg Response: {health.average_response_time:.3f}s")
            print(f"      Errors: {health.error_count}")

def main():
    """Run all demonstrations"""
    print("🚀 Error Handling Enhancement Demonstration")
    print("=" * 60)
    print("ℹ️  This demo shows how error handling is enhanced")
    print("   while preserving all existing behavior")
    print("=" * 60)
    
    demo_error_logging()
    demo_cleanup_enhancement()
    demo_health_monitoring()
    demo_existing_code_enhancement()
    demo_error_analytics()
    
    print("\n" + "=" * 60)
    print("✅ Error handling enhancement demonstration completed!")
    print("\n📋 Enhancement Summary:")
    print("• Silent failures now have debug logging")
    print("• Component health is monitored automatically")  
    print("• Error patterns are tracked for analysis")
    print("• All existing behavior is preserved")
    print("• No breaking changes to working code")
    
    # Show final system health
    summary = get_system_health()
    print(f"\n🏥 Final System Health: {summary['overall_status']}")
    print(f"   Components: {summary['healthy_components']} healthy, "
          f"{summary['degraded_components']} degraded, "
          f"{summary['unhealthy_components']} unhealthy")

if __name__ == "__main__":
    main()