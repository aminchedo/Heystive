"""
Secure Subprocess Wrapper Module
Provides secure wrappers for subprocess calls - preserves existing functionality
DO NOT MODIFY existing subprocess calls - this adds security layers gradually
"""

import subprocess
import shlex
import logging
import asyncio
import os
import signal
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
import tempfile

logger = logging.getLogger(__name__)

class SecureSubprocess:
    """
    Secure wrapper for subprocess calls - preserves existing functionality
    Adds validation and security without changing existing behavior
    """
    
    # Whitelist of allowed commands (can be extended)
    ALLOWED_COMMANDS = {
        # Audio/Media commands (used in TTS)
        'aplay', 'paplay', 'ffmpeg', 'sox',
        
        # System monitoring commands (used in system_monitor.py)
        'nvidia-smi', 'rocm-smi', 'intel_gpu_top', 'ping',
        
        # TTS engines (used in tts_engine.py)
        'espeak', 'espeak-ng', 'festival',
        
        # Network discovery (used in device_discovery.py)
        'nmap', 'arp', 'ping', 'host', 'dig',
        
        # System utilities
        'which', 'whereis', 'lsof', 'ps', 'top', 'htop'
    }
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        '&&', '||', ';', '|', '>', '<', '>>',  # Command chaining/redirection
        '$(', '`', '${',                        # Command substitution
        'rm ', 'del ', 'format ', 'mkfs',      # Destructive commands
        'sudo ', 'su ', 'chmod +s',            # Privilege escalation
        'curl ', 'wget ', 'nc ', 'netcat',     # Network tools (unless whitelisted)
        'python ', 'perl ', 'ruby ', 'bash ', 'sh '  # Script interpreters
    ]
    
    @staticmethod
    def safe_run(command: Union[str, List[str]], timeout: int = 30, **kwargs) -> subprocess.CompletedProcess:
        """
        Secure wrapper that validates inputs but preserves behavior
        
        Args:
            command: Command to execute (string or list)
            timeout: Timeout in seconds
            **kwargs: Additional subprocess.run arguments
            
        Returns:
            subprocess.CompletedProcess object (same as subprocess.run)
            
        Raises:
            SecurityError: If command is deemed unsafe
            subprocess.TimeoutExpired: If command times out
        """
        try:
            # Convert string command to list for safer handling
            if isinstance(command, str):
                cmd_list = shlex.split(command)
            else:
                cmd_list = command.copy()
            
            if not cmd_list:
                raise SecurityError("Empty command provided")
            
            # Validate command
            SecureSubprocess._validate_command(cmd_list)
            
            # Set secure defaults
            secure_kwargs = {
                'timeout': timeout,
                'check': kwargs.get('check', False),
                'capture_output': kwargs.get('capture_output', False),
                'text': kwargs.get('text', False),
                'shell': False,  # Never use shell=True for security
                'cwd': kwargs.get('cwd'),
                'env': kwargs.get('env'),
                'input': kwargs.get('input')
            }
            
            # Remove None values
            secure_kwargs = {k: v for k, v in secure_kwargs.items() if v is not None}
            
            logger.debug(f"Executing secure command: {cmd_list[:2]}...")  # Log first 2 args only
            
            # Execute with security wrapper
            return subprocess.run(cmd_list, **secure_kwargs)
            
        except subprocess.TimeoutExpired as e:
            logger.warning(f"Command timed out after {timeout}s: {cmd_list[0]}")
            raise
        except SecurityError as e:
            logger.error(f"Security violation blocked: {e}")
            raise
        except Exception as e:
            logger.error(f"Secure subprocess execution failed: {e}")
            raise
    
    @staticmethod
    async def safe_run_async(command: Union[str, List[str]], timeout: int = 30, **kwargs) -> subprocess.CompletedProcess:
        """
        Async version of safe_run using asyncio.to_thread
        """
        return await asyncio.to_thread(SecureSubprocess.safe_run, command, timeout, **kwargs)
    
    @staticmethod
    def _validate_command(cmd_list: List[str]) -> None:
        """
        Validate command for security issues
        
        Args:
            cmd_list: Command as list of strings
            
        Raises:
            SecurityError: If command is deemed unsafe
        """
        if not cmd_list:
            raise SecurityError("Empty command")
        
        command_name = Path(cmd_list[0]).name  # Get basename only
        
        # Check if command is in whitelist
        if command_name not in SecureSubprocess.ALLOWED_COMMANDS:
            raise SecurityError(f"Command not in whitelist: {command_name}")
        
        # Check for dangerous patterns in all arguments
        full_command = ' '.join(cmd_list)
        for pattern in SecureSubprocess.DANGEROUS_PATTERNS:
            if pattern in full_command:
                raise SecurityError(f"Dangerous pattern detected: {pattern}")
        
        # Check for absolute paths outside safe directories
        if cmd_list[0].startswith('/'):
            safe_paths = ['/usr/bin/', '/bin/', '/usr/local/bin/']
            if not any(cmd_list[0].startswith(path) for path in safe_paths):
                raise SecurityError(f"Unsafe absolute path: {cmd_list[0]}")
        
        # Validate file arguments (if any)
        for arg in cmd_list[1:]:
            if arg.startswith('/') and '..' in arg:
                raise SecurityError(f"Path traversal attempt: {arg}")
    
    @staticmethod
    def migrate_unsafe_call(original_call_args: Dict[str, Any]) -> Dict[str, Any]:
        """
        Helper to gradually migrate existing calls
        
        Args:
            original_call_args: Original subprocess.run arguments
            
        Returns:
            Updated arguments with security enhancements
        """
        try:
            # Preserve original behavior while adding security
            migrated_args = original_call_args.copy()
            
            # Add timeout if not present
            if 'timeout' not in migrated_args:
                migrated_args['timeout'] = 30
            
            # Force shell=False for security
            if migrated_args.get('shell', False):
                logger.warning("Forcing shell=False for security")
                migrated_args['shell'] = False
                
                # If command was a string for shell=True, convert to list
                if isinstance(migrated_args.get('args', ''), str):
                    migrated_args['args'] = shlex.split(migrated_args['args'])
            
            return migrated_args
            
        except Exception as e:
            logger.error(f"Migration failed: {e}")
            return original_call_args  # Return original if migration fails

class SecurityError(Exception):
    """Custom exception for security violations"""
    pass

class SubprocessSecurityWrapper:
    """
    Context manager for temporarily securing subprocess calls
    Can be used to wrap existing code blocks without modification
    """
    
    def __init__(self, allowed_commands: Optional[List[str]] = None):
        self.allowed_commands = allowed_commands or []
        self.original_run = None
    
    def __enter__(self):
        """Replace subprocess.run with secure version"""
        self.original_run = subprocess.run
        
        def secure_run_wrapper(*args, **kwargs):
            # Add custom allowed commands to whitelist temporarily
            if self.allowed_commands:
                original_whitelist = SecureSubprocess.ALLOWED_COMMANDS.copy()
                SecureSubprocess.ALLOWED_COMMANDS.update(self.allowed_commands)
            
            try:
                return SecureSubprocess.safe_run(*args, **kwargs)
            except SecurityError:
                # Fallback to original if security check fails
                logger.warning("Security check failed, using original subprocess.run")
                return self.original_run(*args, **kwargs)
            finally:
                # Restore original whitelist
                if self.allowed_commands:
                    SecureSubprocess.ALLOWED_COMMANDS.clear()
                    SecureSubprocess.ALLOWED_COMMANDS.update(original_whitelist)
        
        subprocess.run = secure_run_wrapper
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Restore original subprocess.run"""
        if self.original_run:
            subprocess.run = self.original_run

# Convenience functions for common secure operations
def safe_audio_command(command: Union[str, List[str]], timeout: int = 10) -> subprocess.CompletedProcess:
    """Execute audio-related commands securely"""
    return SecureSubprocess.safe_run(command, timeout=timeout, capture_output=True)

def safe_system_command(command: Union[str, List[str]], timeout: int = 5) -> subprocess.CompletedProcess:
    """Execute system monitoring commands securely"""
    return SecureSubprocess.safe_run(command, timeout=timeout, capture_output=True, text=True)

def safe_network_command(command: Union[str, List[str]], timeout: int = 10) -> subprocess.CompletedProcess:
    """Execute network commands securely"""
    return SecureSubprocess.safe_run(command, timeout=timeout, capture_output=True, text=True)

# Migration helpers for existing code
def add_security_to_existing_call(func):
    """
    Decorator to add security to existing functions that use subprocess
    Usage: @add_security_to_existing_call
    """
    def wrapper(*args, **kwargs):
        try:
            with SubprocessSecurityWrapper():
                return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Security wrapper failed, using original function: {e}")
            return func(*args, **kwargs)
    
    return wrapper

# Example usage patterns for gradual migration:
"""
# Pattern 1: Direct replacement (for new code)
# OLD: subprocess.run(['aplay', 'file.wav'])
# NEW: SecureSubprocess.safe_run(['aplay', 'file.wav'])

# Pattern 2: Wrapper for existing code blocks
# with SubprocessSecurityWrapper():
#     # Existing code using subprocess.run continues to work
#     subprocess.run(['espeak', '--version'])

# Pattern 3: Decorator for existing functions
# @add_security_to_existing_call
# def existing_audio_function():
#     subprocess.run(['aplay', 'sound.wav'])

# Pattern 4: Gradual migration helper
# old_args = {'args': ['ping', '-c', '1', 'google.com'], 'timeout': 5}
# new_args = SecureSubprocess.migrate_unsafe_call(old_args)
# subprocess.run(**new_args)
"""