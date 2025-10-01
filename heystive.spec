from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT
a = Analysis(['server/main.py'])
pyz = PYZ(a.pure)
exe = EXE(pyz, a.scripts, name='heystive', console=True)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=False, name='dist')