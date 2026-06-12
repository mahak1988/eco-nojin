$ErrorActionPreference = "Stop"
Set-Location "D:\econojin.com"

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "   PROVE IMPORT ISSUE - Scientific Test" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host ""

# ====================================================================
# TEST 1: Create minimal page.tsx without imports
# ====================================================================
Write-Host "[TEST 1] Creating minimal login/page.tsx (no imports)..." -ForegroundColor Cyan

$loginPagePath = "apps\web\src\app\(auth)\login\page.tsx"

# Backup original
Copy-Item -LiteralPath $loginPagePath "$loginPagePath.original" -Force
Write-Host "  [BACKUP] Original saved" -ForegroundColor Yellow

# Create minimal version
$minimalPage = @"
export default function LoginPage() {
  return <div>Login Page - Minimal Test</div>;
}
"@

$utf8NoBom = New-Object System.Text.UTF8Encoding $false
[System.IO.File]::WriteAllText("$PWD\$loginPagePath", $minimalPage, $utf8NoBom)

Write-Host "  [OK]   Minimal page created" -ForegroundColor Green
Write-Host ""

# ====================================================================
# TEST 2: Try build with minimal page
# ====================================================================
Write-Host "[TEST 2] Building with minimal page..." -ForegroundColor Cyan
Write-Host ""

$buildSuccess = $false
try {
    pnpm build 2>&1 | Out-String | Write-Host
    
    if ($LASTEXITCODE -eq 0) {
        $buildSuccess = $true
        Write-Host ""
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host "  BUILD SUCCESSFUL!" -ForegroundColor Green
        Write-Host "  This PROVES the issue is with imports!" -ForegroundColor Green
        Write-Host "================================================================" -ForegroundColor Green
    }
} catch {
    Write-Host "  Build failed" -ForegroundColor Red
}

Write-Host ""

# ====================================================================
# TEST 3: If build succeeded, restore original and check imports
# ====================================================================
if ($buildSuccess) {
    Write-Host "[TEST 3] Analyzing broken imports..." -ForegroundColor Cyan
    Write-Host ""
    
    # Restore original
    Copy-Item -LiteralPath "$loginPagePath.original" $loginPagePath -Force
    Write-Host "  [RESTORED] Original login/page.tsx" -ForegroundColor Yellow
    Write-Host ""
    
    # Extract all imports
    $content = Get-Content -LiteralPath $loginPagePath -Raw
    $imports = [regex]::Matches($content, 'import\s+.*?from\s+["\x27]([^"\x27]+)["\x27]')
    
    Write-Host "  Imports in login/page.tsx:" -ForegroundColor Gray
    foreach ($imp in $imports) {
        $module = $imp.Groups[1].Value
        Write-Host "    - $module" -ForegroundColor White
    }
    Write-Host ""
    
    # Check which imports are broken
    Write-Host "  Checking import resolution:" -ForegroundColor Gray
    
    $brokenImports = @()
    foreach ($imp in $imports) {
        $module = $imp.Groups[1].Value
        
        if ($module.StartsWith('@/')) {
            # Convert @/ to actual path
            $relativePath = $module -replace '@\/', 'src/'
            $fullPath = "apps\web\$relativePath"
            
            # Check if file or folder exists
            $found = $false
            
            # Try as file with various extensions
            foreach ($ext in @('.ts', '.tsx', '.js', '.jsx', '')) {
                if (Test-Path -LiteralPath "$fullPath$ext") {
                    $found = $true
                    break
                }
            }
            
            # Try as folder with index file
            if (-not $found -and (Test-Path -LiteralPath $fullPath -PathType Container)) {
                foreach ($ext in @('.ts', '.tsx', '.js', '.jsx')) {
                    if (Test-Path -LiteralPath "$fullPath\index$ext") {
                        $found = $true
                        break
                    }
                }
            }
            
            if ($found) {
                Write-Host "    [OK]   $module" -ForegroundColor Green
            } else {
                Write-Host "    [BROKEN] $module" -ForegroundColor Red
                $brokenImports += $module
            }
        } else {
            # External package - check node_modules
            $packageName = if ($module.StartsWith('@')) {
                ($module -split '/')[0..1] -join '/'
            } else {
                ($module -split '/')[0]
            }
            
            if (Test-Path "node_modules\$packageName") {
                Write-Host "    [OK]   $module (external)" -ForegroundColor Green
            } else {
                Write-Host "    [WARN] $module (not in node_modules)" -ForegroundColor Yellow
            }
        }
    }
    
    Write-Host ""
    
    if ($brokenImports.Count -gt 0) {
        Write-Host "================================================================" -ForegroundColor Red
        Write-Host "  FOUND $($brokenImports.Count) BROKEN IMPORTS!" -ForegroundColor Red
        Write-Host "================================================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "  Broken imports:" -ForegroundColor Yellow
        $brokenImports | ForEach-Object { Write-Host "    - $_" -ForegroundColor Red }
        Write-Host ""
        Write-Host "  These imports point to files that were moved to packages/" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  SOLUTION OPTIONS:" -ForegroundColor Cyan
        Write-Host "  1. Update tsconfig.json paths to point to packages/" -ForegroundColor White
        Write-Host "  2. Update imports to use @econojin/lib and @econojin/features" -ForegroundColor White
        Write-Host "  3. Add packages as dependencies in apps/web/package.json" -ForegroundColor White
    } else {
        Write-Host "================================================================" -ForegroundColor Green
        Write-Host "  All imports resolved!" -ForegroundColor Green
        Write-Host "  Issue might be elsewhere..." -ForegroundColor Yellow
        Write-Host "================================================================" -ForegroundColor Green
    }
} else {
    Write-Host "================================================================" -ForegroundColor Red
    Write-Host "  BUILD FAILED even with minimal page!" -ForegroundColor Red
    Write-Host "  Issue is NOT with imports." -ForegroundColor Red
    Write-Host "  Need further investigation..." -ForegroundColor Red
    Write-Host "================================================================" -ForegroundColor Red
    
    # Restore original
    Copy-Item -LiteralPath "$loginPagePath.original" $loginPagePath -Force
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Magenta
Write-Host "  TEST COMPLETE" -ForegroundColor Magenta
Write-Host "================================================================" -ForegroundColor Magenta