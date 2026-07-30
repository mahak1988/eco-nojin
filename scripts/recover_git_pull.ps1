#Requires -Version 5.1
# Fix: untracked .devcontainer/devcontainer.json blocks git pull
$ErrorActionPreference = "Stop"
$Root = if (Test-Path ".\apps\main.py") { (Get-Location).Path } else { Split-Path $PSScriptRoot -Parent }
Set-Location $Root
Write-Host "Repo: $Root"

$dc = Join-Path $Root ".devcontainer\devcontainer.json"
if (Test-Path $dc) {
  $bak = Join-Path $Root ".devcontainer\devcontainer.json.localbak"
  Write-Host "Backing up local devcontainer -> $bak"
  Move-Item -Force $dc $bak
}

Write-Host "git fetch + pull origin main"
git fetch origin
git pull origin main

Write-Host "Done. Next: .\scripts\run_local.ps1"
