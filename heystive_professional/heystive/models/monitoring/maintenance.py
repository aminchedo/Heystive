#!/usr/bin/env python3
"""
TTS System Maintenance - REAL AUTOMATION
Performs regular maintenance tasks automatically
"""

import os
import shutil
import subprocess
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

def cleanup_old_logs() -> Dict:
    """Clean up REAL old log files"""
    base_path = Path(__file__).parent.parent
    logs_path = base_path / "logs"
    
    if not logs_path.exists():
        return {'status': 'skipped', 'reason': 'logs directory not found'}
    
    # Keep logs newer than 30 days
    cutoff_date = datetime.now() - timedelta(days=30)
    cleaned_files = []
    
    log_patterns = ["*.log", "health_report_*.json", "*.tmp"]
    
    for pattern in log_patterns:
        for log_file in logs_path.glob(pattern):
            try:
                if log_file.stat().st_mtime < cutoff_date.timestamp():
                    log_file.unlink()
                    cleaned_files.append(log_file.name)
            except Exception as e:
                print(f"Failed to remove {log_file}: {e}")
    
    return {'status': 'completed', 'files_cleaned': len(cleaned_files), 'files': cleaned_files}

def cleanup_cache() -> Dict:
    """Clean up REAL cache files"""
    base_path = Path(__file__).parent.parent
    cache_path = base_path / "cache"
    
    if not cache_path.exists():
        return {'status': 'skipped', 'reason': 'cache directory not found'}
    
    # Clean temp files and directories
    temp_items_removed = 0
    
    # Remove temp directories
    temp_dir = cache_path / "temp"
    if temp_dir.exists():
        try:
            shutil.rmtree(temp_dir)
            temp_dir.mkdir(exist_ok=True)  # Recreate empty temp dir
            temp_items_removed += 1
        except Exception as e:
            print(f"Failed to clean temp directory: {e}")
    
    # Remove temporary files
    temp_patterns = ['*.tmp', '*.temp', '*.download']
    for pattern in temp_patterns:
        for temp_file in cache_path.rglob(pattern):
            try:
                if temp_file.is_file():
                    temp_file.unlink()
                    temp_items_removed += 1
            except Exception as e:
                print(f"Failed to remove {temp_file}: {e}")
    
    # Remove __pycache__ directories
    for pycache_dir in cache_path.rglob('__pycache__'):
        try:
            shutil.rmtree(pycache_dir)
            temp_items_removed += 1
        except Exception as e:
            print(f"Failed to remove {pycache_dir}: {e}")
    
    return {'status': 'completed', 'items_removed': temp_items_removed}

def verify_model_integrity() -> Dict:
    """Verify REAL model file integrity"""
    base_path = Path(__file__).parent.parent
    
    # Run the health check
    health_script = Path(__file__).parent / "health_check.py"
    if health_script.exists():
        try:
            result = subprocess.run(['python3', str(health_script)], 
                                  capture_output=True, text=True, timeout=60)
            return {
                'status': 'completed' if result.returncode == 0 else 'issues_found',
                'exit_code': result.returncode,
                'output': result.stdout,
                'errors': result.stderr
            }
        except subprocess.TimeoutExpired:
            return {'status': 'timeout', 'error': 'Health check timed out'}
        except Exception as e:
            return {'status': 'failed', 'error': str(e)}
    else:
        return {'status': 'skipped', 'reason': 'health check script not found'}

def optimize_model_storage() -> Dict:
    """Optimize model storage by removing duplicates and organizing files"""
    base_path = Path(__file__).parent.parent
    persian_tts_path = base_path / "persian_tts"
    
    if not persian_tts_path.exists():
        return {'status': 'skipped', 'reason': 'persian_tts directory not found'}
    
    optimization_results = {
        'duplicates_removed': 0,
        'empty_dirs_removed': 0,
        'space_saved_mb': 0
    }
    
    # Find and remove empty directories
    for root, dirs, files in os.walk(persian_tts_path, topdown=False):
        for dir_name in dirs:
            dir_path = Path(root) / dir_name
            try:
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    optimization_results['empty_dirs_removed'] += 1
            except Exception as e:
                print(f"Failed to remove empty directory {dir_path}: {e}")
    
    # Find potential duplicate files (same size and name)
    file_registry = {}
    for model_file in persian_tts_path.rglob('*'):
        if model_file.is_file():
            file_key = (model_file.name, model_file.stat().st_size)
            if file_key not in file_registry:
                file_registry[file_key] = []
            file_registry[file_key].append(model_file)
    
    # Remove duplicates (keep first occurrence)
    for file_key, file_list in file_registry.items():
        if len(file_list) > 1:
            # Keep the first file, remove others
            for duplicate_file in file_list[1:]:
                try:
                    file_size = duplicate_file.stat().st_size
                    duplicate_file.unlink()
                    optimization_results['duplicates_removed'] += 1
                    optimization_results['space_saved_mb'] += file_size / (1024 * 1024)
                except Exception as e:
                    print(f"Failed to remove duplicate {duplicate_file}: {e}")
    
    return {
        'status': 'completed',
        'optimizations': optimization_results
    }

def update_model_registry() -> Dict:
    """Update model registry with current state"""
    try:
        base_path = Path(__file__).parent.parent
        registry_path = base_path / "COMPREHENSIVE_MODEL_REGISTRY.json"
        
        if not registry_path.exists():
            return {'status': 'skipped', 'reason': 'registry file not found'}
        
        # Load existing registry
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        # Update timestamp
        registry['last_maintenance'] = datetime.now().isoformat()
        
        # Recalculate model sizes
        for engine, path_str in registry.get('model_paths', {}).items():
            engine_path = Path(path_str)
            if engine_path.exists():
                total_size = sum(f.stat().st_size for f in engine_path.rglob('*') if f.is_file())
                registry['model_sizes'][engine] = f"{total_size / (1024*1024):.1f}MB"
        
        # Update disk space info
        try:
            statvfs = os.statvfs(base_path)
            free_gb = (statvfs.f_frsize * statvfs.f_bavail) / (1024**3)
            registry['system_info']['disk_space_gb'] = free_gb
        except Exception as e:
            print(f"Failed to update disk space info: {e}")
        
        # Save updated registry
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
        
        return {'status': 'completed', 'registry_updated': True}
        
    except Exception as e:
        return {'status': 'failed', 'error': str(e)}

def generate_maintenance_report(results: Dict) -> str:
    """Generate maintenance report"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    base_path = Path(__file__).parent.parent
    report_path = base_path / "logs" / f"maintenance_report_{timestamp}.md"
    
    # Ensure logs directory exists
    report_path.parent.mkdir(exist_ok=True)
    
    report_content = f"""# TTS System Maintenance Report

**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Maintenance Type**: Automated System Maintenance

## Maintenance Tasks Summary

"""
    
    for task_name, task_result in results.items():
        status = task_result.get('status', 'unknown')
        status_emoji = {'completed': '✅', 'skipped': '⏭️', 'failed': '❌', 'issues_found': '⚠️'}.get(status, '❓')
        
        report_content += f"### {task_name.replace('_', ' ').title()}\n"
        report_content += f"**Status**: {status_emoji} {status.upper()}\n\n"
        
        if status == 'completed':
            if task_name == 'log_cleanup':
                files_cleaned = task_result.get('files_cleaned', 0)
                report_content += f"- Files cleaned: {files_cleaned}\n"
                if task_result.get('files'):
                    report_content += f"- Cleaned files: {', '.join(task_result['files'][:5])}\n"
                    if len(task_result['files']) > 5:
                        report_content += f"  ... and {len(task_result['files']) - 5} more\n"
                        
            elif task_name == 'cache_cleanup':
                items_removed = task_result.get('items_removed', 0)
                report_content += f"- Cache items removed: {items_removed}\n"
                
            elif task_name == 'storage_optimization':
                opt = task_result.get('optimizations', {})
                report_content += f"- Duplicates removed: {opt.get('duplicates_removed', 0)}\n"
                report_content += f"- Empty directories removed: {opt.get('empty_dirs_removed', 0)}\n"
                report_content += f"- Space saved: {opt.get('space_saved_mb', 0):.1f} MB\n"
                
            elif task_name == 'integrity_check':
                exit_code = task_result.get('exit_code', -1)
                if exit_code == 0:
                    report_content += "- All integrity checks passed\n"
                elif exit_code == 2:
                    report_content += "- Minor issues found (warnings)\n"
                else:
                    report_content += f"- Issues detected (exit code: {exit_code})\n"
                    
        elif status == 'skipped':
            reason = task_result.get('reason', 'Unknown reason')
            report_content += f"- Reason: {reason}\n"
            
        elif status == 'failed':
            error = task_result.get('error', 'Unknown error')
            report_content += f"- Error: {error}\n"
        
        report_content += "\n"
    
    # Add recommendations
    report_content += """## Recommendations

### Regular Maintenance
- Run this maintenance script weekly
- Monitor disk space regularly
- Check health status daily

### Manual Actions (if needed)
- Review and clean old backup files
- Update model configurations if new models are added
- Monitor system performance during TTS operations

### Next Maintenance
Recommended next maintenance: """ + (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d') + """

---
*Report generated by TTS System Maintenance*
"""
    
    # Write report
    with open(report_path, 'w') as f:
        f.write(report_content)
    
    return str(report_path)

def run_maintenance() -> Dict:
    """Execute REAL maintenance tasks"""
    print("🔧 STARTING TTS SYSTEM MAINTENANCE")
    print("=" * 50)
    
    results = {
        'maintenance_timestamp': datetime.now().isoformat(),
        'tasks': {}
    }
    
    # Define maintenance tasks
    maintenance_tasks = [
        ('log_cleanup', 'Cleaning old log files', cleanup_old_logs),
        ('cache_cleanup', 'Cleaning cache files', cleanup_cache),
        ('storage_optimization', 'Optimizing model storage', optimize_model_storage),
        ('registry_update', 'Updating model registry', update_model_registry),
        ('integrity_check', 'Verifying model integrity', verify_model_integrity)
    ]
    
    # Run maintenance tasks
    for task_id, task_desc, task_func in maintenance_tasks:
        print(f"\n🔄 {task_desc}...")
        try:
            task_result = task_func()
            results['tasks'][task_id] = task_result
            
            status = task_result.get('status', 'unknown')
            status_emoji = {'completed': '✅', 'skipped': '⏭️', 'failed': '❌', 'issues_found': '⚠️'}.get(status, '❓')
            print(f"   {status_emoji} {status.upper()}")
            
        except Exception as e:
            results['tasks'][task_id] = {'status': 'failed', 'error': str(e)}
            print(f"   ❌ FAILED: {e}")
    
    # Generate maintenance report
    try:
        report_path = generate_maintenance_report(results['tasks'])
        results['report_path'] = report_path
        print(f"\n📄 Maintenance report: {report_path}")
    except Exception as e:
        print(f"\n⚠️ Failed to generate report: {e}")
    
    # Summary
    completed_tasks = sum(1 for task in results['tasks'].values() if task.get('status') == 'completed')
    total_tasks = len(results['tasks'])
    
    print(f"\n📊 MAINTENANCE SUMMARY")
    print(f"Completed: {completed_tasks}/{total_tasks} tasks")
    print("🔧 Maintenance completed!")
    
    return results

if __name__ == "__main__":
    run_maintenance()