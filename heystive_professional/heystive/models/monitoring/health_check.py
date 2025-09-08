#!/usr/bin/env python3
"""
TTS System Health Check - REAL MONITORING
Automatically checks system health and generates alerts
"""

import json
import subprocess
import os
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

def check_disk_space() -> Dict:
    """Check REAL disk space"""
    try:
        # Get disk usage for workspace
        result = subprocess.run(['df', '-h', '/workspace'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                parts = lines[1].split()
                if len(parts) >= 5:
                    total = parts[1]
                    used = parts[2]
                    available = parts[3]
                    percent_used = float(parts[4].replace('%', ''))
                    
                    return {
                        'total': total,
                        'used': used,
                        'available': available,
                        'percent_used': percent_used,
                        'status': 'critical' if percent_used > 90 else 'warning' if percent_used > 80 else 'ok'
                    }
        
        # Fallback method
        statvfs = os.statvfs('/workspace')
        total_bytes = statvfs.f_frsize * statvfs.f_blocks
        free_bytes = statvfs.f_frsize * statvfs.f_bavail
        used_bytes = total_bytes - free_bytes
        percent_used = (used_bytes / total_bytes) * 100
        
        return {
            'total': f"{total_bytes // (1024**3)}G",
            'used': f"{used_bytes // (1024**3)}G", 
            'available': f"{free_bytes // (1024**3)}G",
            'percent_used': round(percent_used, 1),
            'status': 'critical' if percent_used > 90 else 'warning' if percent_used > 80 else 'ok'
        }
        
    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def check_model_files() -> Dict:
    """Check REAL model files integrity"""
    base_path = Path(__file__).parent.parent
    registry_path = base_path / "COMPREHENSIVE_MODEL_REGISTRY.json"
    
    if not registry_path.exists():
        return {'status': 'critical', 'error': 'Comprehensive model registry missing'}
    
    try:
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        missing_engines = []
        available_engines = []
        total_files = 0
        
        for engine in registry.get('available_engines', []):
            engine_path = Path(registry['model_paths'][engine])
            if not engine_path.exists():
                missing_engines.append(engine)
            else:
                available_engines.append(engine)
                # Count files in engine directory
                file_count = len([f for f in engine_path.rglob('*') if f.is_file()])
                total_files += file_count
        
        return {
            'status': 'critical' if missing_engines else 'ok',
            'total_files': total_files,
            'missing_engines': missing_engines,
            'available_engines': available_engines,
            'total_engines': len(registry.get('available_engines', []))
        }
        
    except Exception as e:
        return {'status': 'critical', 'error': str(e)}

def check_imports() -> Dict:
    """Check REAL import functionality"""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    import_tests = [
        ('unified_loader', 'from models.unified_tts_loader import get_unified_tts_loader'),
        ('tts_manager', 'from engines.tts.persian_multi_tts_manager import PersianMultiTTSManager')
    ]
    
    results = {}
    for name, import_cmd in import_tests:
        try:
            exec(import_cmd)
            results[name] = {'status': 'ok'}
        except Exception as e:
            results[name] = {'status': 'critical', 'error': str(e)}
    
    return results

def check_model_accessibility() -> Dict:
    """Check if models are accessible through unified loader"""
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        
        from models.unified_tts_loader import get_unified_tts_loader
        
        loader = get_unified_tts_loader()
        engines = loader.get_available_engines()
        
        accessible_engines = 0
        engine_details = {}
        
        for engine in engines:
            is_available = loader.is_engine_available(engine)
            model_count = len(loader.list_models(engine))
            
            engine_details[engine] = {
                'available': is_available,
                'model_count': model_count,
                'path': str(loader.get_model_path(engine))
            }
            
            if is_available:
                accessible_engines += 1
        
        return {
            'status': 'ok' if accessible_engines > 0 else 'warning',
            'total_engines': len(engines),
            'accessible_engines': accessible_engines,
            'engine_details': engine_details,
            'recommended_engine': loader.get_recommended_engine()
        }
        
    except Exception as e:
        return {'status': 'critical', 'error': str(e)}

def generate_health_report() -> Dict:
    """Generate REAL health report"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'disk_space': check_disk_space(),
        'model_files': check_model_files(),
        'imports': check_imports(),
        'model_accessibility': check_model_accessibility()
    }
    
    # Determine overall status
    critical_issues = []
    warning_issues = []
    
    # Check each component
    if report['disk_space'].get('status') == 'critical':
        critical_issues.append('disk_space')
    elif report['disk_space'].get('status') == 'warning':
        warning_issues.append('disk_space')
        
    if report['model_files'].get('status') == 'critical':
        critical_issues.append('model_files')
        
    for name, result in report['imports'].items():
        if result.get('status') == 'critical':
            critical_issues.append(f'import_{name}')
            
    if report['model_accessibility'].get('status') == 'critical':
        critical_issues.append('model_accessibility')
    elif report['model_accessibility'].get('status') == 'warning':
        warning_issues.append('model_accessibility')
    
    # Overall status
    if critical_issues:
        report['overall_status'] = 'critical'
    elif warning_issues:
        report['overall_status'] = 'warning'
    else:
        report['overall_status'] = 'ok'
    
    report['critical_issues'] = critical_issues
    report['warning_issues'] = warning_issues
    
    return report

def save_health_report(report: Dict) -> str:
    """Save health report to file"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = Path(__file__).parent.parent / "logs" / f"health_report_{timestamp}.json"
    
    # Ensure logs directory exists
    report_path.parent.mkdir(exist_ok=True)
    
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    return str(report_path)

def print_health_summary(report: Dict):
    """Print health summary to console"""
    status_emoji = {
        'ok': '✅',
        'warning': '⚠️', 
        'critical': '❌',
        'error': '💥'
    }
    
    overall_status = report.get('overall_status', 'unknown')
    print(f"\n🏥 TTS SYSTEM HEALTH CHECK")
    print(f"Status: {status_emoji.get(overall_status, '❓')} {overall_status.upper()}")
    print(f"Timestamp: {report.get('timestamp', 'Unknown')}")
    print("=" * 50)
    
    # Disk Space
    disk = report.get('disk_space', {})
    disk_status = disk.get('status', 'unknown')
    print(f"💾 Disk Space: {status_emoji.get(disk_status, '❓')} {disk_status.upper()}")
    if 'percent_used' in disk:
        print(f"   Used: {disk.get('used', 'Unknown')} / {disk.get('total', 'Unknown')} ({disk['percent_used']}%)")
        print(f"   Available: {disk.get('available', 'Unknown')}")
    
    # Model Files
    models = report.get('model_files', {})
    models_status = models.get('status', 'unknown')
    print(f"📦 Model Files: {status_emoji.get(models_status, '❓')} {models_status.upper()}")
    if 'total_files' in models:
        print(f"   Total Files: {models['total_files']}")
        print(f"   Available Engines: {len(models.get('available_engines', []))}/{models.get('total_engines', 0)}")
        if models.get('missing_engines'):
            print(f"   Missing Engines: {', '.join(models['missing_engines'])}")
    
    # Imports
    imports = report.get('imports', {})
    print(f"📥 Import Tests:")
    for name, result in imports.items():
        import_status = result.get('status', 'unknown')
        print(f"   {name}: {status_emoji.get(import_status, '❓')} {import_status.upper()}")
        if 'error' in result:
            print(f"     Error: {result['error']}")
    
    # Model Accessibility
    access = report.get('model_accessibility', {})
    access_status = access.get('status', 'unknown')
    print(f"🔗 Model Access: {status_emoji.get(access_status, '❓')} {access_status.upper()}")
    if 'accessible_engines' in access:
        print(f"   Accessible: {access['accessible_engines']}/{access.get('total_engines', 0)} engines")
        if access.get('recommended_engine'):
            print(f"   Recommended: {access['recommended_engine']}")
    
    # Issues Summary
    if report.get('critical_issues'):
        print(f"\n❌ Critical Issues: {', '.join(report['critical_issues'])}")
    if report.get('warning_issues'):
        print(f"⚠️ Warning Issues: {', '.join(report['warning_issues'])}")
    
    if overall_status == 'ok':
        print(f"\n🎉 All systems operational!")

if __name__ == "__main__":
    print("🚀 Running TTS System Health Check...")
    
    # Generate health report
    report = generate_health_report()
    
    # Save report
    report_path = save_health_report(report)
    
    # Print summary
    print_health_summary(report)
    
    print(f"\n📄 Detailed report saved: {report_path}")
    
    # Exit with appropriate code
    overall_status = report.get('overall_status', 'unknown')
    if overall_status == 'critical':
        exit(1)
    elif overall_status == 'warning':
        exit(2)
    else:
        exit(0)