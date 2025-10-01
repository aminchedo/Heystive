$ErrorActionPreference = "Stop"
$TaskName = "HeystiveResident"
$RepoRoot = (Resolve-Path "$PSScriptRoot\..\..\..").Path
$BatPath = Join-Path $RepoRoot "agents\resident\windows\run_resident.bat"
if (-not (Test-Path $BatPath)) { throw "run_resident.bat not found at $BatPath" }
$Action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument "/c `"$BatPath`""
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -MultipleInstances IgnoreNew
try { Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue } catch {}
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "Heystive resident wake-word listener" -Force
Write-Host "Installed task '$TaskName'. It will start on next logon."