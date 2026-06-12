# ============================================================
# Packages Structure Setup - Phase 2 (FINAL FIXED VERSION)
# Project: econojin.com
# ============================================================

$ErrorActionPreference = "Stop"
$projectRoot = "D:\econojin.com"
Set-Location $projectRoot

# Helper function to write file content (FIXED for root-level files)
function Write-FileContent {
    param(
        [string]$Path,
        [string[]]$Lines
    )
    $dir = Split-Path $Path -Parent
    # FIX: Check if $dir is not empty before calling Test-Path
    if ($dir -and -not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
    $Lines -join "`n" | Out-File -FilePath $Path -Encoding UTF8 -NoNewline
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host "   Packages Structure Setup - Phase 2" -ForegroundColor Magenta
Write-Host "============================================================" -ForegroundColor Magenta
Write-Host ""

# ============================================================
# Step 1: Create package directories
# ============================================================
Write-Host "[Step 1/8] Creating package directories..." -ForegroundColor Cyan

$packageDirs = @(
    "packages\lib\src\api",
    "packages\lib\src\utils",
    "packages\lib\src\hooks",
    "packages\lib\src\validation",
    "packages\features\src\gis",
    "packages\features\src\analysis",
    "packages\features\src\soil-water",
    "packages\features\src\iot",
    "packages\features\src\blockchain",
    "packages\features\src\weather",
    "packages\features\src\satellite",
    "packages\features\src\drought",
    "packages\features\src\forest",
    "packages\features\src\carbon",
    "packages\config-typescript"
)

foreach ($dir in $packageDirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "  Created: $dir" -ForegroundColor Green
    } else {
        Write-Host "  Exists:  $dir" -ForegroundColor DarkGray
    }
}

Write-Host ""

# ============================================================
# Step 2: Create packages/lib/package.json
# ============================================================
Write-Host "[Step 2/8] Creating packages/lib/package.json..." -ForegroundColor Cyan

Write-FileContent -Path "packages\lib\package.json" -Lines @(
    '{'
    '  "name": "@econojin/lib",'
    '  "version": "0.1.0",'
    '  "private": true,'
    '  "main": "./src/index.ts",'
    '  "types": "./src/index.ts",'
    '  "exports": {'
    '    ".": "./src/index.ts",'
    '    "./api": "./src/api/index.ts",'
    '    "./utils": "./src/utils/index.ts",'
    '    "./hooks": "./src/hooks/index.ts",'
    '    "./validation": "./src/validation/index.ts"'
    '  },'
    '  "scripts": {'
    '    "lint": "eslint \"src/**/*.ts\","'
    '    "type-check": "tsc --noEmit"'
    '  },'
    '  "dependencies": {'
    '    "axios": "^1.6.0",'
    '    "zod": "^3.22.0"'
    '  },'
    '  "devDependencies": {'
    '    "@types/node": "^20.10.0",'
    '    "typescript": "^5.3.0"'
    '  }'
    '}'
)
Write-Host "  Created: packages/lib/package.json" -ForegroundColor Green

# ============================================================
# Step 3: Create packages/features/package.json
# ============================================================
Write-Host "[Step 3/8] Creating packages/features/package.json..." -ForegroundColor Cyan

Write-FileContent -Path "packages\features\package.json" -Lines @(
    '{'
    '  "name": "@econojin/features",'
    '  "version": "0.1.0",'
    '  "private": true,'
    '  "main": "./src/index.ts",'
    '  "types": "./src/index.ts",'
    '  "exports": {'
    '    ".": "./src/index.ts",'
    '    "./gis": "./src/gis/index.ts",'
    '    "./analysis": "./src/analysis/index.ts",'
    '    "./soil-water": "./src/soil-water/index.ts",'
    '    "./iot": "./src/iot/index.ts",'
    '    "./blockchain": "./src/blockchain/index.ts",'
    '    "./weather": "./src/weather/index.ts",'
    '    "./satellite": "./src/satellite/index.ts",'
    '    "./drought": "./src/drought/index.ts",'
    '    "./forest": "./src/forest/index.ts",'
    '    "./carbon": "./src/carbon/index.ts"'
    '  },'
    '  "scripts": {'
    '    "lint": "eslint \"src/**/*.ts\","'
    '    "type-check": "tsc --noEmit"'
    '  },'
    '  "dependencies": {'
    '    "react": "^18.2.0"'
    '  },'
    '  "devDependencies": {'
    '    "@types/react": "^18.2.0",'
    '    "typescript": "^5.3.0"'
    '  }'
    '}'
)
Write-Host "  Created: packages/features/package.json" -ForegroundColor Green

# ============================================================
# Step 4: Create tsconfig.json files
# ============================================================
Write-Host "[Step 4/8] Creating tsconfig.json files..." -ForegroundColor Cyan

$baseTsConfigLines = @(
    '{'
    '  "compilerOptions": {'
    '    "target": "ES2020",'
    '    "lib": ["ES2020", "DOM", "DOM.Iterable"],'
    '    "module": "ESNext",'
    '    "moduleResolution": "bundler",'
    '    "resolveJsonModule": true,'
    '    "allowJs": true,'
    '    "strict": true,'
    '    "noEmit": true,'
    '    "isolatedModules": true,'
    '    "moduleDetection": "force",'
    '    "skipLibCheck": true,'
    '    "esModuleInterop": true,'
    '    "forceConsistentCasingInFileNames": true,'
    '    "declaration": true,'
    '    "declarationMap": true,'
    '    "sourceMap": true,'
    '    "jsx": "react-jsx"'
    '  },'
    '  "include": ["src/**/*.ts", "src/**/*.tsx"],'
    '  "exclude": ["node_modules", "dist"]'
    '}'
)

Write-FileContent -Path "packages\lib\tsconfig.json" -Lines $baseTsConfigLines
Write-Host "  Created: packages/lib/tsconfig.json" -ForegroundColor Green

Write-FileContent -Path "packages\features\tsconfig.json" -Lines $baseTsConfigLines
Write-Host "  Created: packages/features/tsconfig.json" -ForegroundColor Green

$baseConfigLines = @(
    '{'
    '  "compilerOptions": {'
    '    "target": "ES2020",'
    '    "lib": ["ES2020", "DOM", "DOM.Iterable"],'
    '    "module": "ESNext",'
    '    "moduleResolution": "bundler",'
    '    "resolveJsonModule": true,'
    '    "allowJs": true,'
    '    "strict": true,'
    '    "noEmit": true,'
    '    "isolatedModules": true,'
    '    "moduleDetection": "force",'
    '    "skipLibCheck": true,'
    '    "esModuleInterop": true,'
    '    "forceConsistentCasingInFileNames": true'
    '  }'
    '}'
)

Write-FileContent -Path "packages\config-typescript\base.json" -Lines $baseConfigLines
Write-Host "  Created: packages/config-typescript/base.json" -ForegroundColor Green

# ============================================================
# Step 5: Create index.ts files for lib
# ============================================================
Write-Host "[Step 5/8] Creating lib index.ts files..." -ForegroundColor Cyan

Write-FileContent -Path "packages\lib\src\index.ts" -Lines @(
    '// @econojin/lib - Main entry point'
    'export * from "./api";'
    'export * from "./utils";'
    'export * from "./hooks";'
    'export * from "./validation";'
)

Write-FileContent -Path "packages\lib\src\api\index.ts" -Lines @(
    '// API Client exports'
    '// TODO: Move API client from apps/web/src/lib/api/'
    'export {};'
)

Write-FileContent -Path "packages\lib\src\utils\index.ts" -Lines @(
    '// Utility functions exports'
    '// TODO: Move utils from apps/web/src/lib/utils.ts'
    'export {};'
)

Write-FileContent -Path "packages\lib\src\hooks\index.ts" -Lines @(
    '// Custom hooks exports'
    '// TODO: Move hooks from apps/web/src/hooks/'
    'export {};'
)

Write-FileContent -Path "packages\lib\src\validation\index.ts" -Lines @(
    '// Validation schemas exports'
    '// TODO: Move validation from apps/web/src/lib/validation/'
    'export {};'
)

Write-Host "  Created: packages/lib/src/index.ts and sub-modules" -ForegroundColor Green

# ============================================================
# Step 6: Create index.ts files for features
# ============================================================
Write-Host "[Step 6/8] Creating features index.ts files..." -ForegroundColor Cyan

$featureModules = @("gis", "analysis", "soil-water", "iot", "blockchain", "weather", "satellite", "drought", "forest", "carbon")

$featuresIndexLines = @('// @econojin/features - Main entry point')
foreach ($module in $featureModules) {
    $featuresIndexLines += "export * from ""./$module"";"
}
Write-FileContent -Path "packages\features\src\index.ts" -Lines $featuresIndexLines

foreach ($module in $featureModules) {
    Write-FileContent -Path "packages\features\src\$module\index.ts" -Lines @(
        "// $module feature exports"
        "// TODO: Move components from apps/web/src/components/$module/"
        "export {};"
    )
}

Write-Host "  Created: packages/features/src/index.ts and all feature modules" -ForegroundColor Green

# ============================================================
# Step 7: Update pnpm-workspace.yaml
# ============================================================
Write-Host "[Step 7/8] Updating pnpm-workspace.yaml..." -ForegroundColor Cyan

if (Test-Path "pnpm-workspace.yaml") {
    Copy-Item "pnpm-workspace.yaml" "pnpm-workspace.yaml.backup" -Force
    Write-Host "  Backup created: pnpm-workspace.yaml.backup" -ForegroundColor Yellow
}

Write-FileContent -Path "pnpm-workspace.yaml" -Lines @(
    'packages:'
    '  - "apps/*"'
    '  - "packages/*"'
    '  - "econojin-library/frontend"'
)
Write-Host "  Updated: pnpm-workspace.yaml" -ForegroundColor Green

# ============================================================
# Step 8: Create turbo.json
# ============================================================
Write-Host "[Step 8/8] Creating turbo.json..." -ForegroundColor Cyan

Write-FileContent -Path "turbo.json" -Lines @(
    '{'
    '  "$schema": "https://turbo.build/schema.json",'
    '  "globalDependencies": ["**/.env.*local"],'
    '  "pipeline": {'
    '    "build": {'
    '      "dependsOn": ["^build"],'
    '      "outputs": [".next/**", "!.next/cache/**", "dist/**"]'
    '    },'
    '    "lint": {'
    '      "dependsOn": ["^lint"]'
    '    },'
    '    "type-check": {'
    '      "dependsOn": ["^type-check"]'
    '    },'
    '    "dev": {'
    '      "cache": false,'
    '      "persistent": true'
    '    },'
    '    "clean": {'
    '      "cache": false'
    '    }'
    '  }'
    '}'
)
Write-Host "  Created: turbo.json" -ForegroundColor Green

# ============================================================
# Bonus: Create packages README
# ============================================================
Write-Host ""
Write-Host "[Bonus] Creating packages/README.md..." -ForegroundColor Cyan

Write-FileContent -Path "packages\README.md" -Lines @(
    '# Packages'
    ''
    'This directory contains shared packages used across the monorepo.'
    ''
    '## Structure'
    ''
    '### `@econojin/lib`'
    'Shared utilities, API clients, hooks, and validation schemas.'
    ''
    '### `@econojin/features`'
    'Feature-specific components and logic (GIS, Analysis, IoT, etc.).'
    ''
    '### `@econojin/ui`'
    'Shared UI components (shadcn/ui based).'
    ''
    '### `@econojin/types`'
    'Shared TypeScript type definitions.'
    ''
    '### `config-eslint`'
    'Shared ESLint configuration.'
    ''
    '### `config-typescript`'
    'Shared TypeScript configuration.'
    ''
    '## Usage'
    ''
    'In your app''s `package.json`:'
    ''
    '```json'
    '{'
    '  "dependencies": {'
    '    "@econojin/lib": "workspace:*",'
    '    "@econojin/features": "workspace:*"'
    '  }'
    '}'
    '```'
    ''
    'Then import in your code:'
    ''
    '```typescript'
    'import { useAuth } from "@econojin/lib/hooks";'
    'import { GisMap } from "@econojin/features/gis";'
    '```'
)
Write-Host "  Created: packages/README.md" -ForegroundColor Green

# ============================================================
# Final Report
# ============================================================
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "                  PHASE 2 COMPLETE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Created packages:" -ForegroundColor White
Write-Host "  - packages/lib (API, utils, hooks, validation)" -ForegroundColor Cyan
Write-Host "  - packages/features (GIS, Analysis, IoT, etc.)" -ForegroundColor Cyan
Write-Host "  - packages/config-typescript (base tsconfig)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Updated files:" -ForegroundColor White
Write-Host "  - pnpm-workspace.yaml" -ForegroundColor Cyan
Write-Host "  - turbo.json (new)" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Commit: git add -A && git commit -m 'phase2: setup packages structure'" -ForegroundColor White
Write-Host "  2. Install: pnpm install" -ForegroundColor White
Write-Host "  3. Proceed to Phase 3: Move code from apps/web to packages/" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green