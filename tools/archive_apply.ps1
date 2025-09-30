param(
  [string]$Plan = $(Get-Date -Format 'archive_plan_yyyy-MM-dd') + '.csv',
  [string]$ArchiveDir = ("archive/" + (Get-Date -Format 'yyyy-MM-dd')),
  [switch]$DryRun
)
if (!(Test-Path $Plan)) { Write-Error "Plan not found: $Plan"; exit 1 }
New-Item -ItemType Directory -Force -Path $ArchiveDir | Out-Null
$inGit = $false
try { $null = git rev-parse --is-inside-work-tree; $inGit = $true } catch {}
Import-Csv $Plan | ForEach-Object {
  $dst = Join-Path $ArchiveDir $_.path
  New-Item -ItemType Directory -Force -Path (Split-Path $dst) | Out-Null
  if ($DryRun) {
    Write-Host "[DRY] mv -- '$($_.path)' '$dst'"
  } else {
    if ($inGit) {
      try { git mv -f -- "$($_.path)" "$dst" } catch { Move-Item -Force -Path "$($_.path)" -Destination "$dst" }
    } else {
      Move-Item -Force -Path "$($_.path)" -Destination "$dst"
    }
  }
}
Write-Host "Archive complete → $ArchiveDir"