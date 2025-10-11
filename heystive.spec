from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
import os

# Desktop app entry point
a = Analysis(['apps/desktop/main.py'])

# Add desktop app components
a.datas += [
    ('apps/desktop/assets/style.qss', 'apps/desktop/assets'),
    ('apps/desktop/components', 'apps/desktop/components'),
]

# Add knowledge directory if it exists
if os.path.exists('knowledge'):
    a.datas += [('knowledge', 'knowledge')]

# Add server components
a.datas += [
    ('server', 'server'),
]

# Add other necessary files
a.datas += [
    ('settings.json', '.'),
    ('config', 'config'),
]

pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, name='heystive-desktop', console=False, icon=None)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=False, name='dist')