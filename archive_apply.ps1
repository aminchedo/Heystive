param(
  [string]$Plan = "archive_plan_2025-09-30.csv",
  [string]$ArchiveDir = "archive/2025-09-30",
  [switch]$DryRun
)
if (!(Test-Path $Plan)) { Write-Error "Plan not found: $Plan"; exit 1 }
New-Item -ItemType Directory -Force -Path $ArchiveDir | Out-Null
$inGit = (& git rev-parse --is-inside-work-tree) -ne $null

Import-Csv $Plan | ForEach-Object {
  $path = $_.path
  $dst = Join-Path $ArchiveDir $path
  New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
  if ($DryRun) {
    Write-Host "[DRY] mv -- '$path' '$dst'"
  } else {
    if ($inGit) {
      try { git mv -f -- "$path" "$dst" } catch { Move-Item -Force -Path "$path" -Destination "$dst" }
    } else {
      Move-Item -Force -Path "$path" -Destination "$dst"
    }
  }
}
Write-Host "Archive complete → $ArchiveDir"
