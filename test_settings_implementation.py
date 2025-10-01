#!/usr/bin/env python3
"""
Quick test script to verify settings and brain implementation
"""
import sys
import os
sys.path.append('/workspace')

def test_settings_store():
    print("Testing settings store...")
    try:
        from server.settings_store import load, save, Settings
        s = load()
        print(f"✓ Settings loaded: theme={s.theme}, stt={s.stt_engine}")
        
        # Test save
        s.theme = "dark"
        save(s)
        s2 = load()
        assert s2.theme == "dark"
        print("✓ Settings save/load works")
        return True
    except Exception as e:
        print(f"✗ Settings store failed: {e}")
        return False

def test_brain_imports():
    print("Testing brain imports...")
    try:
        from heystive_professional.heystive.brain.model_llm import get_llm, generate
        from heystive_professional.heystive.brain.tools import tool_search_memory, tool_list_whitelist_root
        from heystive_professional.heystive.brain.planner import plan
        from heystive_professional.heystive.brain.executor import run
        print("✓ All brain modules import successfully")
        return True
    except Exception as e:
        print(f"✗ Brain imports failed: {e}")
        return False

def test_orchestrator():
    print("Testing orchestrator...")
    try:
        from heystive_professional.heystive.core.orchestrator import choose_stt, choose_tts, choose_llm, model_path
        stt = choose_stt()
        tts = choose_tts()
        llm = choose_llm()
        path = model_path()
        print(f"✓ Orchestrator: STT={stt}, TTS={tts}, LLM={llm}, Path={path}")
        return True
    except Exception as e:
        print(f"✗ Orchestrator failed: {e}")
        return False

def main():
    print("=== Heystive Settings + Brain Implementation Test ===\n")
    
    tests = [
        test_settings_store,
        test_brain_imports,
        test_orchestrator
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
        print()
    
    print(f"Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All tests passed! Implementation is ready.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Start server: python server/main.py")
        print("3. Open: http://127.0.0.1:8765/settings")
        print("4. Place GGUF model at: models/llm/gguf/model.gguf")
    else:
        print("❌ Some tests failed. Check dependencies and imports.")

if __name__ == "__main__":
    main()