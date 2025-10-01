@echo off
setlocal
set "REPO=%~dp0..\..\.."
pushd "%REPO%"
start "" /B pythonw "agents\resident\windows\watcher_win.py"
popd
endlocal