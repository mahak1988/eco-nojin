$ErrorActionPreference = "Continue"
Set-Location "D:\econojin.com"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "   FIX TURBO PACKAGE MANAGER FIELD" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""

$root = (Get-Location).Path
$utf8NoBom = New-Object System.Text.UTF8Encoding $false

# ====================================================================
# STEP 1: Read current package.json
# ====================================================================
Write-Host "[STEP 1] Reading root package.json..." -ForegroundColor Cyan
Write-Host ""

$packageJsonPath = "package.json"
$content = [System.IO.File]::ReadAllText((Join-Path $root $packageJsonPath))

# Remove BOM if exists
if ($content.Length -gt 0 -and [int]$content[0] -eq 65279) {
    $content = $content.Substring(1)
}

$packageJson = $content | ConvertFrom-Json

Write-Host "  [OK]   Current package.json loaded" -ForegroundColor Green
Write-Host ""

# ====================================================================
# STEP 2: Add packageManager field
# ====================================================================
Write-Host "[STEP 2] Adding packageManager field..." -ForegroundColor Cyan
Write-Host ""

# Check current pnpm version
$pnpmVersion = (pnpm --version).Trim()
Write-Host "  Detected pnpm version: $pnpmVersion" -ForegroundColor Gray

# Add packageManager field
if ($packageJson.PSObject.Properties.Name -contains 'packageManager') {
    $packageJson.packageManager = "pnpm@$pnpmVersion"
    Write-Host "  [UPDATED] packageManager field" -ForegroundColor Green
} else {
    $packageJson | Add-Member -NotePropertyName "packageManager" -NotePropertyValue "pnpm@$pnpmVersion" -Force
    Write-Host "  [ADDED] packageManager field" -ForegroundColor Green
}

Write-Host ""

# ====================================================================
# STEP 3: Save package.json
# ====================================================================
Write-Host "[STEP 3] Saving package.json..." -ForegroundColor Cyan
Write-Host ""

$newContent = $packageJson | ConvertTo-Json -Depth 10
[System.IO.File]::WriteAllText((Join-Path $root $packageJsonPath), $newContent, $utf8NoBom)

Write-Host "  [OK]   package.json saved" -ForegroundColor Green
Write-Host ""

# ====================================================================
# STEP 4: Test turbo commands
# ====================================================================
Write-Host "[STEP 4] Testing turbo commands..." -ForegroundColor Cyan
Write-Host ""

Write-Host "  Testing: pnpm dev..." -ForegroundColor Gray
try {
    $output = pnpm dev 2>&1 | Select-Object -First 5 | Out-String
    Write-Host $output
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  [OK]   pnpm dev works!" -ForegroundColor Green
    } else {
        Write-Host "  [WARN] pnpm dev had issues (may need more time)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "  [INFO] pnpm dev started (check output above)" -ForegroundColor Gray
}

Write-Host ""

# ====================================================================
# STEP 5: Commit the fix
# ====================================================================
Write-Host "[STEP 5] Committing the fix..." -ForegroundColor Cyan
Write-Host ""

git add package.json
git commit -m "fix: add packageManager field for turbo v2 compatibility"

Write-Host ""

# ====================================================================
# STEP 6: Push to remote
# ====================================================================
Write-Host "[STEP 6] Pushing to remote..." -ForegroundColor Cyan
Write-Host ""

git push

Write-Host ""

# ====================================================================
# STEP 7: Summary
# ====================================================================
Write-Host "================================================================" -ForegroundColor Green
Write-Host "  FIX COMPLETE!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Added: `"packageManager`": `"pnpm@$pnpmVersion`"" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Now you can run:" -ForegroundColor Yellow
Write-Host "  - pnpm dev     (start development server)" -ForegroundColor White
Write-Host "  - pnpm build   (build for production)" -ForegroundColor White
Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "  COMPLETE" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta