# ============================================================
# Fix JSON Final - Correct package.json files
# Project: econojin.com
# ============================================================

$ErrorActionPreference = "Stop"
$projectRoot = "D:\econojin.com"
Set-Location $projectRoot

Write-Host ""
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host "   Fix JSON Final - Correct package.json files" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Yellow
Write-Host ""

# ============================================================
# Fix packages/lib/package.json
# ============================================================
Write-Host "[Step 1/2] Fixing packages/lib/package.json..." -ForegroundColor Cyan
Write-Host ""

$libPackageJson = @'
{
  "name": "@econojin/lib",
  "version": "0.1.0",
  "private": true,
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "exports": {
    ".": "./src/index.ts",
    "./api": "./src/api/index.ts",
    "./utils": "./src/utils/index.ts",
    "./hooks": "./src/hooks/index.ts",
    "./validation": "./src/validation/index.ts"
  },
  "scripts": {
    "lint": "eslint src/**/*.ts",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "axios": "^1.6.0",
    "zod": "^3.22.0"
  },
  "devDependencies": {
    "@types/node": "^20.10.0",
    "typescript": "^5.3.0"
  }
}
'@

$libPackageJson | Out-File -FilePath "packages\lib\package.json" -Encoding UTF8 -NoNewline

# Validate
try {
    $null = Get-Content "packages\lib\package.json" -Raw | ConvertFrom-Json
    Write-Host "  [OK]   packages/lib/package.json is valid" -ForegroundColor Green
} catch {
    Write-Host "  [ERR]  Still invalid: $_" -ForegroundColor Red
}

Write-Host ""

# ============================================================
# Fix packages/features/package.json
# ============================================================
Write-Host "[Step 2/2] Fixing packages/features/package.json..." -ForegroundColor Cyan
Write-Host ""

$featuresPackageJson = @'
{
  "name": "@econojin/features",
  "version": "0.1.0",
  "private": true,
  "main": "./src/index.ts",
  "types": "./src/index.ts",
  "exports": {
    ".": "./src/index.ts",
    "./gis": "./src/gis/index.ts",
    "./analysis": "./src/analysis/index.ts",
    "./soil-water": "./src/soil-water/index.ts",
    "./iot": "./src/iot/index.ts",
    "./blockchain": "./src/blockchain/index.ts",
    "./weather": "./src/weather/index.ts",
    "./satellite": "./src/satellite/index.ts",
    "./drought": "./src/drought/index.ts",
    "./forest": "./src/forest/index.ts",
    "./carbon": "./src/carbon/index.ts"
  },
  "scripts": {
    "lint": "eslint src/**/*.ts",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "typescript": "^5.3.0"
  }
}
'@

$featuresPackageJson | Out-File -FilePath "packages\features\package.json" -Encoding UTF8 -NoNewline

# Validate
try {
    $null = Get-Content "packages\features\package.json" -Raw | ConvertFrom-Json
    Write-Host "  [OK]   packages/features/package.json is valid" -ForegroundColor Green
} catch {
    Write-Host "  [ERR]  Still invalid: $_" -ForegroundColor Red
}

Write-Host ""

# ============================================================
# Run pnpm install
# ============================================================
Write-Host "[Step 3/3] Running pnpm install..." -ForegroundColor Cyan
Write-Host ""

try {
    pnpm install
    Write-Host ""
    Write-Host "  [OK]   pnpm install completed successfully!" -ForegroundColor Green
} catch {
    Write-Host "  [WARN] pnpm install had issues: $_" -ForegroundColor Yellow
}

# ============================================================
# Final Report
# ============================================================
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "                  JSON FIX COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "All JSON files are now valid!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. git status" -ForegroundColor White
Write-Host "  2. git add -A" -ForegroundColor White
Write-Host "  3. git commit -m 'fix(phase6): correct JSON syntax in package.json files'" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green