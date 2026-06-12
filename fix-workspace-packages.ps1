$ErrorActionPreference = "Continue"
Set-Location "D:\econojin.com"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "   FIX WORKSPACE PACKAGES" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""

$root = (Get-Location).Path
$utf8NoBom = New-Object System.Text.UTF8Encoding $false

# ====================================================================
# STEP 1: Check pnpm-workspace.yaml
# ====================================================================
Write-Host "[STEP 1] Checking pnpm-workspace.yaml..." -ForegroundColor Cyan
Write-Host ""

$workspacePath = "pnpm-workspace.yaml"
if (Test-Path -LiteralPath $workspacePath) {
    $content = [System.IO.File]::ReadAllText((Join-Path $root $workspacePath))
    Write-Host "  Content:" -ForegroundColor Gray
    $content.Split("`n") | ForEach-Object { Write-Host "    $_" -ForegroundColor White }
    
    # Ensure packages/* is included
    if ($content -notmatch 'packages/\*') {
        Write-Host ""
        Write-Host "  [WARN] 'packages/*' not found in workspace!" -ForegroundColor Yellow
        
        $newContent = @"
packages:
  - 'apps/*'
  - 'packages/*'
"@
        [System.IO.File]::WriteAllText((Join-Path $root $workspacePath), $newContent, $utf8NoBom)
        Write-Host "  [FIXED] Added 'packages/*' to workspace" -ForegroundColor Green
    } else {
        Write-Host "  [OK]   Workspace configuration is correct" -ForegroundColor Green
    }
} else {
    Write-Host "  [ERR]  pnpm-workspace.yaml not found!" -ForegroundColor Red
}

Write-Host ""

# ====================================================================
# STEP 2: Check packages/lib/package.json
# ====================================================================
Write-Host "[STEP 2] Checking packages/lib/package.json..." -ForegroundColor Cyan
Write-Host ""

$libPackagePath = "packages\lib\package.json"
if (Test-Path -LiteralPath $libPackagePath) {
    $content = [System.IO.File]::ReadAllText((Join-Path $root $libPackagePath))
    
    # Remove BOM if exists
    if ($content.Length -gt 0 -and [int]$content[0] -eq 65279) {
        $content = $content.Substring(1)
        Write-Host "  [WARN] BOM detected and removed" -ForegroundColor Yellow
    }
    
    try {
        $packageJson = $content | ConvertFrom-Json
        Write-Host "  name: $($packageJson.name)" -ForegroundColor White
        Write-Host "  version: $($packageJson.version)" -ForegroundColor White
        
        if ($packageJson.name -ne "@econojin/lib") {
            Write-Host "  [WARN] Package name is not @econojin/lib!" -ForegroundColor Yellow
            $packageJson.name = "@econojin/lib"
            $newContent = $packageJson | ConvertTo-Json -Depth 10
            [System.IO.File]::WriteAllText((Join-Path $root $libPackagePath), $newContent, $utf8NoBom)
            Write-Host "  [FIXED] Updated package name" -ForegroundColor Green
        } else {
            Write-Host "  [OK]   Package name is correct" -ForegroundColor Green
        }
    } catch {
        Write-Host "  [ERR]  Failed to parse: $_" -ForegroundColor Red
    }
} else {
    Write-Host "  [ERR]  packages/lib/package.json not found!" -ForegroundColor Red
}

Write-Host ""

# ====================================================================
# STEP 3: Check all packages in workspace
# ====================================================================
Write-Host "[STEP 3] Checking all packages..." -ForegroundColor Cyan
Write-Host ""

$packagesDir = "packages"
if (Test-Path -LiteralPath $packagesDir) {
    $packages = Get-ChildItem -LiteralPath $packagesDir -Directory
    
    foreach ($pkg in $packages) {
        $pkgJsonPath = Join-Path $pkg.FullName "package.json"
        if (Test-Path -LiteralPath $pkgJsonPath) {
            $content = [System.IO.File]::ReadAllText($pkgJsonPath)
            
            # Remove BOM
            if ($content.Length -gt 0 -and [int]$content[0] -eq 65279) {
                $content = $content.Substring(1)
                [System.IO.File]::WriteAllText($pkgJsonPath, $content, $utf8NoBom)
            }
            
            try {
                $packageJson = $content | ConvertFrom-Json
                Write-Host "  [OK]   $($pkg.Name): $($packageJson.name)" -ForegroundColor Green
            } catch {
                Write-Host "  [ERR]  $($pkg.Name): Invalid JSON" -ForegroundColor Red
            }
        } else {
            Write-Host "  [WARN] $($pkg.Name): No package.json" -ForegroundColor Yellow
        }
    }
} else {
    Write-Host "  [ERR]  packages directory not found!" -ForegroundColor Red
}

Write-Host ""

# ====================================================================
# STEP 4: Remove @econojin/lib and @econojin/features from apps/web
# ====================================================================
Write-Host "[STEP 4] Removing workspace dependencies from apps/web..." -ForegroundColor Cyan
Write-Host ""

$webPackagePath = "apps\web\package.json"
if (Test-Path -LiteralPath $webPackagePath) {
    $content = [System.IO.File]::ReadAllText((Join-Path $root $webPackagePath))
    
    if ($content.Length -gt 0 -and [int]$content[0] -eq 65279) {
        $content = $content.Substring(1)
    }
    
    $packageJson = $content | ConvertFrom-Json
    
    # Remove workspace dependencies
    if ($packageJson.dependencies.PSObject.Properties.Name -contains '@econojin/lib') {
        $packageJson.dependencies.PSObject.Properties.Remove('@econojin/lib')
        Write-Host "  [DEL]  @econojin/lib from dependencies" -ForegroundColor Yellow
    }
    
    if ($packageJson.dependencies.PSObject.Properties.Name -contains '@econojin/features') {
        $packageJson.dependencies.PSObject.Properties.Remove('@econojin/features')
        Write-Host "  [DEL]  @econojin/features from dependencies" -ForegroundColor Yellow
    }
    
    if ($packageJson.dependencies.PSObject.Properties.Name -contains '@econojin/ui') {
        $packageJson.dependencies.PSObject.Properties.Remove('@econojin/ui')
        Write-Host "  [DEL]  @econojin/ui from dependencies" -ForegroundColor Yellow
    }
    
    $newContent = $packageJson | ConvertTo-Json -Depth 10
    [System.IO.File]::WriteAllText((Join-Path $root $webPackagePath), $newContent, $utf8NoBom)
    Write-Host "  [OK]   Updated apps/web/package.json" -ForegroundColor Green
}

Write-Host ""

# ====================================================================
# STEP 5: Reinstall dependencies
# ====================================================================
Write-Host "[STEP 5] Reinstalling dependencies..." -ForegroundColor Cyan
Write-Host ""

try {
    pnpm install
    Write-Host ""
    Write-Host "  [OK]   pnpm install completed" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] pnpm install had warnings: $_" -ForegroundColor Yellow
}

Write-Host ""

# ====================================================================
# STEP 6: Test build
# ====================================================================
Write-Host "[STEP 6] Testing build..." -ForegroundColor Cyan
Write-Host ""

try {
    $output = pnpm --filter @econojin/web build 2>&1 | Out-String
    Write-Host $output
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host "  BUILD SUCCESSFUL!" -ForegroundColor Green
        Write-Host "================================================================" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Red
        Write-Host "  BUILD FAILED" -ForegroundColor Red
        Write-Host "================================================================" -ForegroundColor Red
    }
} catch {
    Write-Host "  [ERR]  Build failed: $_" -ForegroundColor Red
}

Write-Host ""

# ====================================================================
# STEP 7: Commit and push
# ====================================================================
Write-Host "[STEP 7] Committing changes..." -ForegroundColor Cyan
Write-Host ""

git add -A
git commit -m "fix: resolve workspace package issues"
git push

Write-Host ""

# ====================================================================
# STEP 8: Node.js recommendation
# ====================================================================
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "  IMPORTANT: Node.js Version" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""
Write-Host "  You are using Node.js v24 which has compatibility issues." -ForegroundColor Yellow
Write-Host ""
Write-Host "  RECOMMENDATION: Downgrade to Node.js 22 LTS" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Download: https://nodejs.org/dist/v22.16.0/node-v22.16.0-x64.msi" -ForegroundColor White
Write-Host ""
Write-Host "  After installation:" -ForegroundColor Yellow
Write-Host "  1. Close PowerShell" -ForegroundColor White
Write-Host "  2. Reopen PowerShell" -ForegroundColor White
Write-Host "  3. Run: node --version (should show v22.16.0)" -ForegroundColor White
Write-Host "  4. Run: pnpm install" -ForegroundColor White
Write-Host "  5. Run: pnpm dev" -ForegroundColor White
Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "  COMPLETE" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta