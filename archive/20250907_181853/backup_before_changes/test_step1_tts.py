#!/usr/bin/env python3
"""
STEP 1 VERIFICATION TEST
MANDATORY verification that Step 1 actually works
Must pass before proceeding to Step 2
"""

import sys
import os
from pathlib import Path

# Add the heystive module to path
sys.path.insert(0, '/workspace')

from heystive.voice.persian_tts import PersianVoiceEngine

def verify_step1_completion():
    """
    MANDATORY verification that Step 1 actually works
    Must pass before proceeding to Step 2
    """
    print("🔍 VERIFYING STEP 1 COMPLETION...")
    print("=" * 50)
    
    verification_results = {
        "engine_creation": False,
        "audio_files_exist": False,
        "on_demand_generation": False,
        "file_count": 0,
        "total_size": 0
    }
    
    # Test 1: Can we create TTS engine?
    try:
        print("🧪 Test 1: TTS Engine Creation")
        tts = PersianVoiceEngine()
        verification_results["engine_creation"] = True
        print("   ✅ TTS Engine creation: PASSED")
    except Exception as e:
        print(f"   ❌ TTS Engine creation: FAILED - {e}")
        return False, verification_results
    
    # Test 2: Are audio files actually generated?
    print("\n🧪 Test 2: Audio File Generation Check")
    audio_dir = "/workspace/heystive_audio_output"
    if os.path.exists(audio_dir):
        audio_files = [f for f in os.listdir(audio_dir) if f.endswith('.mp3')]
        verification_results["file_count"] = len(audio_files)
        
        if audio_files:
            # Calculate total size
            total_size = sum(os.path.getsize(os.path.join(audio_dir, f)) for f in audio_files)
            verification_results["total_size"] = total_size
            verification_results["audio_files_exist"] = True
            
            print(f"   ✅ Audio generation: PASSED - {len(audio_files)} files found")
            print(f"   📊 Total size: {total_size} bytes")
            
            # List all files
            for i, audio_file in enumerate(sorted(audio_files), 1):
                file_path = os.path.join(audio_dir, audio_file)
                file_size = os.path.getsize(file_path)
                print(f"   📁 {i}. {audio_file} ({file_size} bytes)")
        else:
            print("   ❌ Audio generation: FAILED - No .mp3 files found")
            return False, verification_results
    else:
        print("   ❌ Audio generation: FAILED - No output directory")
        return False, verification_results
    
    # Test 3: Can we generate new audio on demand?
    print("\n🧪 Test 3: On-Demand Generation Test")
    test_file = f"{audio_dir}/verification_test.mp3"
    test_phrase = "این یک تست تایید است"
    
    try:
        success = tts.speak_and_save(test_phrase, test_file)
        
        if success and os.path.exists(test_file):
            file_size = os.path.getsize(test_file)
            verification_results["on_demand_generation"] = True
            print(f"   ✅ On-demand generation: PASSED ({file_size} bytes)")
        else:
            print("   ❌ On-demand generation: FAILED")
            return False, verification_results
            
    except Exception as e:
        print(f"   ❌ On-demand generation: ERROR - {e}")
        return False, verification_results
    
    # Final verification
    print("\n📊 STEP 1 VERIFICATION SUMMARY:")
    print("=" * 50)
    all_passed = all([
        verification_results["engine_creation"],
        verification_results["audio_files_exist"],
        verification_results["on_demand_generation"]
    ])
    
    if all_passed:
        print("🎉 STEP 1 VERIFICATION: ALL TESTS PASSED!")
        print(f"✅ Generated {verification_results['file_count']} audio files")
        print(f"✅ Total audio data: {verification_results['total_size']} bytes")
        print("✅ On-demand generation works")
        print("\n🚀 READY TO PROCEED TO STEP 2 (Persian STT)")
        return True, verification_results
    else:
        print("❌ STEP 1 VERIFICATION: SOME TESTS FAILED!")
        print("🛑 Cannot proceed to Step 2 until all tests pass")
        return False, verification_results

def generate_step1_report(results):
    """Generate a detailed report of Step 1 results."""
    print("\n📋 STEP 1 DETAILED REPORT:")
    print("=" * 60)
    print(f"Engine Creation: {'✅ PASS' if results['engine_creation'] else '❌ FAIL'}")
    print(f"Audio Files Generated: {'✅ PASS' if results['audio_files_exist'] else '❌ FAIL'}")
    print(f"On-Demand Generation: {'✅ PASS' if results['on_demand_generation'] else '❌ FAIL'}")
    print(f"Total Files: {results['file_count']}")
    print(f"Total Size: {results['total_size']} bytes")
    
    if results['file_count'] >= 5 and results['total_size'] > 100000:  # At least 100KB total
        print("\n🏆 STEP 1 QUALITY ASSESSMENT: EXCELLENT!")
        print("   - Multiple audio files generated")
        print("   - Substantial audio content created")
        print("   - All systems functional")
    elif results['file_count'] >= 3:
        print("\n👍 STEP 1 QUALITY ASSESSMENT: GOOD!")
        print("   - Adequate audio files generated")
        print("   - Basic functionality confirmed")
    else:
        print("\n⚠️ STEP 1 QUALITY ASSESSMENT: NEEDS IMPROVEMENT")
        print("   - Insufficient audio files generated")

if __name__ == "__main__":
    print("🚀 STEP 1 VERIFICATION STARTING...")
    print("Checking if Persian TTS implementation actually works")
    
    success, results = verify_step1_completion()
    generate_step1_report(results)
    
    if success:
        print("\n🎯 VERDICT: STEP 1 SUCCESSFULLY COMPLETED!")
        print("Persian TTS is working and generating real audio files.")
        exit(0)
    else:
        print("\n🚫 VERDICT: STEP 1 FAILED!")
        print("Must fix issues before proceeding to Step 2.")
        exit(1)