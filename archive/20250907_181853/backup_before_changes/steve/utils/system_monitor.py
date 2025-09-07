"""
System Performance Monitor
Hardware detection and optimization for Steve Voice Assistant
"""

import asyncio
import psutil
import platform
import subprocess
import logging
from typing import Dict, Any, Optional, List
import time
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class SystemPerformanceMonitor:
    """
    Comprehensive system performance monitoring and hardware detection
    Optimizes Steve Voice Assistant for any hardware configuration
    """
    
    def __init__(self):
        self.system_info = {}
        self.performance_metrics = {}
        self.optimization_recommendations = []
        
    async def assess_system_capabilities(self) -> Dict[str, Any]:
        """Comprehensive system capability assessment"""
        try:
            logger.info("Assessing system capabilities...")
            
            # Basic system information
            self.system_info = await self._gather_system_info()
            
            # Hardware performance testing
            self.performance_metrics = await self._benchmark_hardware()
            
            # Generate optimization recommendations
            self.optimization_recommendations = await self._generate_optimization_recommendations()
            
            # Determine hardware tier
            hardware_tier = self._determine_hardware_tier()
            
            system_profile = {
                "hardware_tier": hardware_tier,
                "system_info": self.system_info,
                "performance_metrics": self.performance_metrics,
                "optimization_recommendations": self.optimization_recommendations,
                "ram_gb": self.system_info["ram_gb"],
                "cpu_cores": self.system_info["cpu_cores"],
                "gpu_available": self.system_info["gpu_available"],
                "os_type": self.system_info["os_type"],
                "architecture": self.system_info["architecture"]
            }
            
            logger.info(f"System assessment complete - Hardware tier: {hardware_tier}")
            return system_profile
            
        except Exception as e:
            logger.error(f"System assessment failed: {e}")
            return self._get_fallback_system_profile()
    
    async def _gather_system_info(self) -> Dict[str, Any]:
        """Gather comprehensive system information"""
        try:
            # CPU information
            cpu_info = {
                "cores": psutil.cpu_count(logical=False),
                "logical_cores": psutil.cpu_count(logical=True),
                "frequency": psutil.cpu_freq()._asdict() if psutil.cpu_freq() else {},
                "usage": psutil.cpu_percent(interval=1)
            }
            
            # Memory information
            memory = psutil.virtual_memory()
            memory_info = {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_percent": memory.percent,
                "ram_gb": round(memory.total / (1024**3))
            }
            
            # Disk information
            disk = psutil.disk_usage('/')
            disk_info = {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "used_percent": round((disk.used / disk.total) * 100, 2)
            }
            
            # GPU information
            gpu_info = await self._detect_gpu()
            
            # Network information
            network_info = await self._assess_network()
            
            # Audio information
            audio_info = await self._detect_audio_devices()
            
            system_info = {
                "os_type": platform.system(),
                "os_version": platform.version(),
                "architecture": platform.machine(),
                "hostname": platform.node(),
                "python_version": platform.python_version(),
                "cpu_info": cpu_info,
                "memory_info": memory_info,
                "disk_info": disk_info,
                "gpu_info": gpu_info,
                "network_info": network_info,
                "audio_info": audio_info,
                "cpu_cores": cpu_info["cores"],
                "ram_gb": memory_info["ram_gb"],
                "gpu_available": gpu_info["available"]
            }
            
            return system_info
            
        except Exception as e:
            logger.error(f"System info gathering failed: {e}")
            return self._get_basic_system_info()
    
    async def _detect_gpu(self) -> Dict[str, Any]:
        """Detect GPU availability and capabilities"""
        try:
            gpu_info = {
                "available": False,
                "type": None,
                "memory_gb": 0,
                "driver_version": None
            }
            
            # Check for NVIDIA GPU
            try:
                result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,driver_version', '--format=csv,noheader,nounits'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if lines and lines[0]:
                        gpu_info["available"] = True
                        gpu_info["type"] = "nvidia"
                        gpu_info["memory_gb"] = int(lines[0].split(',')[1].strip()) / 1024
                        gpu_info["driver_version"] = lines[0].split(',')[2].strip()
            except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
                pass
            
            # Check for AMD GPU
            if not gpu_info["available"]:
                try:
                    result = subprocess.run(['rocm-smi', '--showmeminfo', 'vram'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        gpu_info["available"] = True
                        gpu_info["type"] = "amd"
                except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
                    pass
            
            # Check for Intel GPU
            if not gpu_info["available"]:
                try:
                    result = subprocess.run(['intel_gpu_top', '-l'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        gpu_info["available"] = True
                        gpu_info["type"] = "intel"
                except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
                    pass
            
            return gpu_info
            
        except Exception as e:
            logger.error(f"GPU detection failed: {e}")
            return {"available": False, "type": None, "memory_gb": 0}
    
    async def _assess_network(self) -> Dict[str, Any]:
        """Assess network connectivity and speed"""
        try:
            network_info = {
                "connected": False,
                "speed_mbps": 0,
                "latency_ms": 0,
                "interfaces": []
            }
            
            # Get network interfaces
            interfaces = psutil.net_if_addrs()
            for interface, addresses in interfaces.items():
                if interface != 'lo':  # Skip loopback
                    for addr in addresses:
                        if addr.family == 2:  # IPv4
                            network_info["interfaces"].append({
                                "name": interface,
                                "ip": addr.address,
                                "netmask": addr.netmask
                            })
                            network_info["connected"] = True
                            break
            
            # Test internet connectivity
            if network_info["connected"]:
                try:
                    # Simple ping test
                    result = subprocess.run(['ping', '-c', '1', '8.8.8.8'], 
                                          capture_output=True, text=True, timeout=5)
                    if result.returncode == 0:
                        # Extract latency from ping output
                        output = result.stdout
                        if 'time=' in output:
                            latency_str = output.split('time=')[1].split()[0]
                            network_info["latency_ms"] = float(latency_str)
                except (subprocess.TimeoutExpired, Exception):
                    pass
            
            return network_info
            
        except Exception as e:
            logger.error(f"Network assessment failed: {e}")
            return {"connected": False, "speed_mbps": 0, "latency_ms": 0, "interfaces": []}
    
    async def _detect_audio_devices(self) -> Dict[str, Any]:
        """Detect available audio devices"""
        try:
            audio_info = {
                "input_devices": [],
                "output_devices": [],
                "default_input": None,
                "default_output": None
            }
            
            try:
                import pyaudio
                p = pyaudio.PyAudio()
                
                device_count = p.get_device_count()
                for i in range(device_count):
                    device_info = p.get_device_info_by_index(i)
                    
                    if device_info['maxInputChannels'] > 0:
                        audio_info["input_devices"].append({
                            "index": i,
                            "name": device_info['name'],
                            "channels": device_info['maxInputChannels'],
                            "sample_rate": device_info['defaultSampleRate']
                        })
                    
                    if device_info['maxOutputChannels'] > 0:
                        audio_info["output_devices"].append({
                            "index": i,
                            "name": device_info['name'],
                            "channels": device_info['maxOutputChannels'],
                            "sample_rate": device_info['defaultSampleRate']
                        })
                
                # Get default devices
                try:
                    default_input = p.get_default_input_device_info()
                    audio_info["default_input"] = default_input['index']
                except:
                    pass
                
                try:
                    default_output = p.get_default_output_device_info()
                    audio_info["default_output"] = default_output['index']
                except:
                    pass
                
                p.terminate()
                
            except ImportError:
                logger.warning("PyAudio not available for audio device detection")
            
            return audio_info
            
        except Exception as e:
            logger.error(f"Audio device detection failed: {e}")
            return {"input_devices": [], "output_devices": [], "default_input": None, "default_output": None}
    
    async def _benchmark_hardware(self) -> Dict[str, Any]:
        """Benchmark hardware performance"""
        try:
            benchmarks = {
                "cpu_score": 0,
                "memory_score": 0,
                "disk_score": 0,
                "overall_score": 0,
                "benchmark_time": 0
            }
            
            start_time = time.time()
            
            # CPU benchmark
            cpu_score = await self._benchmark_cpu()
            benchmarks["cpu_score"] = cpu_score
            
            # Memory benchmark
            memory_score = await self._benchmark_memory()
            benchmarks["memory_score"] = memory_score
            
            # Disk benchmark
            disk_score = await self._benchmark_disk()
            benchmarks["disk_score"] = disk_score
            
            # Calculate overall score
            benchmarks["overall_score"] = (cpu_score + memory_score + disk_score) / 3
            benchmarks["benchmark_time"] = time.time() - start_time
            
            return benchmarks
            
        except Exception as e:
            logger.error(f"Hardware benchmarking failed: {e}")
            return {"cpu_score": 5, "memory_score": 5, "disk_score": 5, "overall_score": 5, "benchmark_time": 0}
    
    async def _benchmark_cpu(self) -> float:
        """Benchmark CPU performance"""
        try:
            # Simple CPU benchmark - calculate prime numbers
            start_time = time.time()
            
            def is_prime(n):
                if n < 2:
                    return False
                for i in range(2, int(n**0.5) + 1):
                    if n % i == 0:
                        return False
                return True
            
            # Count primes up to 10000
            prime_count = sum(1 for i in range(2, 10000) if is_prime(i))
            
            elapsed_time = time.time() - start_time
            
            # Score based on time (lower is better)
            if elapsed_time < 1.0:
                return 10.0
            elif elapsed_time < 2.0:
                return 8.0
            elif elapsed_time < 3.0:
                return 6.0
            elif elapsed_time < 5.0:
                return 4.0
            else:
                return 2.0
                
        except Exception as e:
            logger.error(f"CPU benchmark failed: {e}")
            return 5.0
    
    async def _benchmark_memory(self) -> float:
        """Benchmark memory performance"""
        try:
            # Simple memory benchmark - allocate and access large arrays
            start_time = time.time()
            
            # Allocate 100MB array
            import numpy as np
            array_size = 100 * 1024 * 1024 // 8  # 100MB in double precision
            test_array = np.random.random(array_size)
            
            # Perform operations
            result = np.sum(test_array)
            result = np.mean(test_array)
            result = np.std(test_array)
            
            elapsed_time = time.time() - start_time
            
            # Score based on time (lower is better)
            if elapsed_time < 0.5:
                return 10.0
            elif elapsed_time < 1.0:
                return 8.0
            elif elapsed_time < 2.0:
                return 6.0
            elif elapsed_time < 3.0:
                return 4.0
            else:
                return 2.0
                
        except Exception as e:
            logger.error(f"Memory benchmark failed: {e}")
            return 5.0
    
    async def _benchmark_disk(self) -> float:
        """Benchmark disk performance"""
        try:
            # Simple disk benchmark - write and read test file
            start_time = time.time()
            
            test_file = Path("/tmp/steve_disk_test.tmp")
            test_data = b"0" * (10 * 1024 * 1024)  # 10MB
            
            # Write test
            with open(test_file, 'wb') as f:
                f.write(test_data)
            
            # Read test
            with open(test_file, 'rb') as f:
                read_data = f.read()
            
            # Clean up
            test_file.unlink()
            
            elapsed_time = time.time() - start_time
            
            # Score based on time (lower is better)
            if elapsed_time < 0.5:
                return 10.0
            elif elapsed_time < 1.0:
                return 8.0
            elif elapsed_time < 2.0:
                return 6.0
            elif elapsed_time < 3.0:
                return 4.0
            else:
                return 2.0
                
        except Exception as e:
            logger.error(f"Disk benchmark failed: {e}")
            return 5.0
    
    async def _generate_optimization_recommendations(self) -> List[str]:
        """Generate optimization recommendations based on system assessment"""
        recommendations = []
        
        try:
            # CPU recommendations
            if self.performance_metrics.get("cpu_score", 0) < 6:
                recommendations.append("Consider using lightweight models due to CPU limitations")
            
            # Memory recommendations
            if self.system_info.get("ram_gb", 0) < 8:
                recommendations.append("Limited RAM detected - using memory-efficient models")
            
            # GPU recommendations
            if not self.system_info.get("gpu_available", False):
                recommendations.append("No GPU detected - using CPU-optimized models")
            else:
                recommendations.append("GPU available - enabling hardware acceleration")
            
            # Audio recommendations
            if not self.system_info.get("audio_info", {}).get("input_devices"):
                recommendations.append("No audio input devices detected - check microphone connection")
            
            # Network recommendations
            if not self.system_info.get("network_info", {}).get("connected"):
                recommendations.append("No network connection - offline mode only")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Optimization recommendations failed: {e}")
            return ["Using default configuration"]
    
    def _determine_hardware_tier(self) -> str:
        """Determine hardware tier based on system capabilities"""
        try:
            overall_score = self.performance_metrics.get("overall_score", 5)
            ram_gb = self.system_info.get("ram_gb", 4)
            cpu_cores = self.system_info.get("cpu_cores", 2)
            gpu_available = self.system_info.get("gpu_available", False)
            
            # High tier criteria
            if (overall_score >= 8 and ram_gb >= 16 and cpu_cores >= 8 and gpu_available):
                return "high"
            
            # Medium tier criteria
            elif (overall_score >= 6 and ram_gb >= 8 and cpu_cores >= 4):
                return "medium"
            
            # Low tier (default)
            else:
                return "low"
                
        except Exception as e:
            logger.error(f"Hardware tier determination failed: {e}")
            return "low"
    
    def _get_fallback_system_profile(self) -> Dict[str, Any]:
        """Get fallback system profile when assessment fails"""
        return {
            "hardware_tier": "low",
            "system_info": self._get_basic_system_info(),
            "performance_metrics": {"overall_score": 5},
            "optimization_recommendations": ["Using fallback configuration"],
            "ram_gb": 4,
            "cpu_cores": 2,
            "gpu_available": False,
            "os_type": "unknown",
            "architecture": "unknown"
        }
    
    def _get_basic_system_info(self) -> Dict[str, Any]:
        """Get basic system information as fallback"""
        try:
            return {
                "os_type": platform.system(),
                "architecture": platform.machine(),
                "cpu_cores": psutil.cpu_count(logical=False) or 2,
                "ram_gb": round(psutil.virtual_memory().total / (1024**3)) or 4,
                "gpu_available": False
            }
        except Exception:
            return {
                "os_type": "unknown",
                "architecture": "unknown",
                "cpu_cores": 2,
                "ram_gb": 4,
                "gpu_available": False
            }
    
    async def monitor_performance(self) -> Dict[str, Any]:
        """Monitor real-time system performance"""
        try:
            current_metrics = {
                "timestamp": time.time(),
                "cpu_usage": psutil.cpu_percent(interval=1),
                "memory_usage": psutil.virtual_memory().percent,
                "disk_usage": psutil.disk_usage('/').percent,
                "network_io": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {}
            }
            
            return current_metrics
            
        except Exception as e:
            logger.error(f"Performance monitoring failed: {e}")
            return {"timestamp": time.time(), "error": str(e)}
    
    def get_system_summary(self) -> str:
        """Get human-readable system summary"""
        try:
            summary = f"""
System Summary:
- Hardware Tier: {self.system_info.get('hardware_tier', 'unknown')}
- OS: {self.system_info.get('os_type', 'unknown')} {self.system_info.get('architecture', 'unknown')}
- CPU: {self.system_info.get('cpu_cores', 0)} cores
- RAM: {self.system_info.get('ram_gb', 0)} GB
- GPU: {'Available' if self.system_info.get('gpu_available', False) else 'Not Available'}
- Performance Score: {self.performance_metrics.get('overall_score', 0):.1f}/10
"""
            return summary.strip()
            
        except Exception as e:
            logger.error(f"System summary generation failed: {e}")
            return "System summary unavailable"