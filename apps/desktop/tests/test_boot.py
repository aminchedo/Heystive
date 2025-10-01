"""
Desktop app boot tests
"""

import sys
import os
from pathlib import Path

def test_desktop_imports():
    """Test that desktop app can be imported"""
    # Add the workspace root to path
    workspace_root = Path(__file__).parent.parent.parent.parent
    sys.path.insert(0, str(workspace_root))
    
    try:
        from apps.desktop.main import HeystiveDesktopApp
        from apps.desktop.components.main_window import ModernMainWindow
        from apps.desktop.components.command_palette import CommandPalette
        from apps.desktop.components.voice_control_widget import VoiceControlWidget
        from apps.desktop.components.persian_text_widget import PersianTextWidget
        from apps.desktop.components.voice_visualizer import VoiceVisualizer
        from apps.desktop.hotkeys import GlobalHotkeys
        
        # Test that classes can be instantiated (without GUI)
        assert HeystiveDesktopApp is not None
        assert ModernMainWindow is not None
        assert CommandPalette is not None
        assert VoiceControlWidget is not None
        assert PersianTextWidget is not None
        assert VoiceVisualizer is not None
        assert GlobalHotkeys is not None
        
    except ImportError as e:
        assert False, f"Failed to import desktop components: {e}"

def test_desktop_assets():
    """Test that desktop assets exist"""
    workspace_root = Path(__file__).parent.parent.parent.parent
    assets_dir = workspace_root / "apps" / "desktop" / "assets"
    
    # Check that style.qss exists
    style_file = assets_dir / "style.qss"
    assert style_file.exists(), f"Style file not found: {style_file}"
    
    # Check that style file has content
    with open(style_file, 'r', encoding='utf-8') as f:
        content = f.read()
        assert len(content) > 100, "Style file seems empty or too short"
        assert "QMainWindow" in content, "Style file missing basic styles"

def test_desktop_structure():
    """Test desktop app directory structure"""
    workspace_root = Path(__file__).parent.parent.parent.parent
    desktop_dir = workspace_root / "apps" / "desktop"
    
    # Check main files exist
    assert (desktop_dir / "main.py").exists(), "main.py not found"
    assert (desktop_dir / "hotkeys.py").exists(), "hotkeys.py not found"
    
    # Check components directory
    components_dir = desktop_dir / "components"
    assert components_dir.exists(), "components directory not found"
    assert components_dir.is_dir(), "components is not a directory"
    
    # Check required components
    required_components = [
        "main_window.py",
        "command_palette.py", 
        "voice_control_widget.py",
        "persian_text_widget.py",
        "voice_visualizer.py"
    ]
    
    for component in required_components:
        component_file = components_dir / component
        assert component_file.exists(), f"Component {component} not found"

def test_placeholder():
    """Placeholder test to ensure test file is valid"""
    assert True