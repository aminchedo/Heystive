@echo off
set LOGDIR=.logs
if not exist %LOGDIR% mkdir %LOGDIR%
set LOG=%LOGDIR%\backend.log
set PIDFILE=.run_backend.pid
if "%1"=="start" (
  if exist %PIDFILE% ( echo already running & exit /b 0 )
  powershell -Command "Get-Content -Path NUL" >nul 2>&1
  start /B cmd /c "python heystive_professional\backend_min.py >> %LOG% 2>&1"
  for /f "tokens=2" %%a in ('wmic process where "CommandLine like '%%backend_min.py%%'" get ProcessId ^| findstr /r "[0-9]"') do (echo %%a>%PIDFILE%)
  echo started
  exit /b 0
) else if "%1"=="stop" (
  if exist %PIDFILE% ( for /f %%a in (%PIDFILE%) do taskkill /PID %%a /F >nul 2>&1 & del %PIDFILE% & echo stopped ) else ( echo not running )
  exit /b 0
) else if "%1"=="status" (
  if exist %PIDFILE% ( echo running ) else ( echo stopped )
  exit /b 0
) else if "%1"=="restart" (
  call %0 stop
  timeout /t 1 >nul
  call %0 start
  exit /b 0
) else (
  echo usage: service_win.bat ^<start^|stop^|restart^|status^>
  exit /b 1
)