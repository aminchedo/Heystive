#!/usr/bin/env python3
"""
Test Runner for Steve Voice Assistant
Runs comprehensive tests for existing functionality and new utilities
"""

import sys
import subprocess
import argparse
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, shell=True, check=True, cwd=project_root)
        print(f"✅ {description} - PASSED")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - FAILED (exit code: {e.returncode})")
        return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Run tests for Steve Voice Assistant")
    parser.add_argument("--existing", action="store_true", 
                       help="Run tests for existing functionality only")
    parser.add_argument("--new", action="store_true",
                       help="Run tests for new utilities only")
    parser.add_argument("--integration", action="store_true",
                       help="Run integration tests only")
    parser.add_argument("--unit", action="store_true", 
                       help="Run unit tests only")
    parser.add_argument("--regression", action="store_true",
                       help="Run regression tests only")
    parser.add_argument("--all", action="store_true",
                       help="Run all tests (default)")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--coverage", action="store_true",
                       help="Run with coverage reporting")
    
    args = parser.parse_args()
    
    # Default to all tests if no specific category selected
    if not any([args.existing, args.new, args.integration, args.unit, args.regression]):
        args.all = True
    
    print("🚀 Steve Voice Assistant Test Runner")
    print("=" * 60)
    print("ℹ️  Testing existing functionality and new utilities")
    print("   All tests preserve existing behavior")
    print("=" * 60)
    
    # Check if pytest is available
    try:
        import pytest
        print(f"✅ pytest version: {pytest.__version__}")
    except ImportError:
        print("❌ pytest not available. Install with: pip install pytest")
        return 1
    
    results = []
    
    # Base pytest command
    base_cmd = "python -m pytest"
    if args.verbose:
        base_cmd += " -v"
    if args.coverage:
        base_cmd += " --cov=steve --cov-report=html --cov-report=term"
    
    # Run existing functionality tests
    if args.existing or args.all:
        cmd = f"{base_cmd} tests/test_existing_functionality.py -m existing_behavior"
        results.append(run_command(cmd, "Testing Existing Functionality (Behavior Preservation)"))
    
    # Run new utilities tests
    if args.new or args.all:
        cmd = f"{base_cmd} tests/unit/test_new_utilities.py"
        results.append(run_command(cmd, "Testing New Utility Modules"))
    
    # Run integration tests
    if args.integration or args.all:
        cmd = f"{base_cmd} tests/integration/ -m integration"
        results.append(run_command(cmd, "Testing Integration (Existing + New)"))
    
    # Run unit tests
    if args.unit or args.all:
        cmd = f"{base_cmd} tests/unit/ -m unit"
        results.append(run_command(cmd, "Testing Unit Tests"))
    
    # Run regression tests
    if args.regression or args.all:
        cmd = f"{base_cmd} tests/ -m regression"
        results.append(run_command(cmd, "Testing Regression Prevention"))
    
    # Run original existing tests
    if args.all:
        original_tests = [
            "tests/test_voice_pipeline.py",
            "tests/test_smart_home.py", 
            "tests/test_persian_processing.py"
        ]
        
        for test_file in original_tests:
            if Path(project_root / test_file).exists():
                cmd = f"{base_cmd} {test_file}"
                results.append(run_command(cmd, f"Testing Original: {test_file}"))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    failed = total - passed
    
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Success Rate: {(passed/total*100):.1f}%" if total > 0 else "No tests run")
    
    if failed == 0:
        print("\n🎉 All tests passed! Existing functionality preserved.")
        print("   New utilities integrated successfully.")
    else:
        print(f"\n⚠️  {failed} test suite(s) failed. Check output above.")
        print("   Existing functionality may have regressions.")
    
    # Additional validation
    print("\n" + "=" * 60)
    print("🔍 Additional Validation")
    print("=" * 60)
    
    # Test imports
    validation_results = []
    
    try:
        print("📦 Testing package imports...")
        import steve
        from steve import core, utils, ui, intelligence, smart_home, models
        print("   ✅ All core packages import successfully")
        validation_results.append(True)
    except ImportError as e:
        print(f"   ❌ Package import failed: {e}")
        validation_results.append(False)
    
    # Test new utilities
    try:
        print("🔧 Testing new utility imports...")
        from steve.utils import error_handler, performance_monitor, secure_subprocess, model_downloader, health_checker
        print("   ✅ All new utilities import successfully")
        validation_results.append(True)
    except ImportError as e:
        print(f"   ❌ New utility import failed: {e}")
        validation_results.append(False)
    
    # Test existing functionality
    try:
        print("🎯 Testing existing functionality...")
        from steve.models.download_models import PersianModelDownloader
        from steve.utils.system_monitor import SystemPerformanceMonitor
        
        # Test basic initialization
        downloader = PersianModelDownloader()
        monitor = SystemPerformanceMonitor()
        
        print("   ✅ Existing functionality initializes correctly")
        validation_results.append(True)
    except Exception as e:
        print(f"   ❌ Existing functionality test failed: {e}")
        validation_results.append(False)
    
    validation_passed = sum(validation_results)
    validation_total = len(validation_results)
    
    print(f"\n📋 Validation Results: {validation_passed}/{validation_total} passed")
    
    # Final result
    overall_success = failed == 0 and validation_passed == validation_total
    
    if overall_success:
        print("\n🎉 SUCCESS: All tests and validations passed!")
        print("   ✅ Existing functionality preserved")
        print("   ✅ New utilities working correctly")
        print("   ✅ No regressions detected")
        return 0
    else:
        print("\n❌ FAILURE: Some tests or validations failed")
        print("   Please review the output above for details")
        return 1

if __name__ == "__main__":
    sys.exit(main())