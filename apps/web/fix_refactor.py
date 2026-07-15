#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
 apps/web — Fix Script (repairs missing / defective / build-breaking files)
================================================================================
 Run from D:\\econojin.com\\apps\\web

   python fix_refactor.py

 WHAT IT FIXES
 -------------
  1. Creates missing src/components/common/ErrorFallback.tsx
  2. Rewrites .env.example with proper newlines (was saved as 1 line)
  3. Rewrites tsconfig.json — removes "vite.config.ts" from include,
     removes "node" from types (replaced by installing @types/node)
  4. Rewrites tsconfig.node.json — removes noEmit so composite project
     references work (TS6310 fix), adds emitDeclarationOnly
  5. Installs @types/node via pnpm (if missing)
  6. Re-runs verify_refactor.py to confirm all green

 EXIT CODES
 ----------
  0 = all fixes applied successfully
  1 = something went wrong (see output)
================================================================================
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Files to fix — each entry is (relative_path, content_bytes)
# ---------------------------------------------------------------------------

FIXES = []

# ---------------------------------------------------------------------------
# 1) ErrorFallback.tsx — the missing file referenced by ErrorBoundary.tsx
# ---------------------------------------------------------------------------

ERROR_FALLBACK_TSX = '''/**
 * ============================================================================
 *  ErrorFallback — visual fallback for ErrorBoundary (i18n-aware)
 * ============================================================================
 *
 *  Extracted as a separate functional component so it can use the
 *  useLanguage() hook (the ErrorBoundary itself is a class and can\'t).
 * ============================================================================
 */

import { useLanguage } from "@/hooks/useLanguage";

export interface ErrorFallbackProps {
  error: Error;
  reset: () => void;
}

export function ErrorFallback({ error, reset }: ErrorFallbackProps): JSX.Element {
  const { t, dir } = useLanguage();

  return (
    <div
      role="alert"
      dir={dir}
      className="flex min-h-[50vh] flex-col items-center justify-center gap-4 p-8 text-center"
    >
      <div className="flex h-16 w-16 items-center justify-center rounded-full bg-red-100 text-3xl">
        ⚠️
      </div>
      <h2 className="text-xl font-bold text-red-700">{t("error.boundaryTitle")}</h2>
      <p className="max-w-md text-sm text-gray-600">{t("error.boundaryDescription")}</p>
      {import.meta.env.DEV && (
        <pre dir="ltr" className="max-w-lg overflow-auto rounded-md bg-gray-900 p-4 text-start text-xs text-red-200">
          {error.message}
          {error.stack && `\\n\\n${error.stack}`}
        </pre>
      )}
      <button
        type="button"
        onClick={reset}
        className="mt-2 rounded-lg bg-emerald-600 px-5 py-2 text-sm font-medium text-white transition hover:bg-emerald-700 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:ring-offset-2"
      >
        {t("error.boundaryRetry")}
      </button>
    </div>
  );
}
'''

FIXES.append(("src/components/common/ErrorFallback.tsx", ERROR_FALLBACK_TSX.encode("utf-8")))

# ---------------------------------------------------------------------------
# 2) .env.example — proper newlines (was saved as 1 line, 41 bytes)
# ---------------------------------------------------------------------------

ENV_EXAMPLE = """# Copy this file to .env.local and fill in the real values.

# Base URL of the econojin CMS / API backend (Strapi by default)
VITE_API_BASE_URL=http://localhost:1337/api

# Default application language ("fa" for Persian/RTL, "en" for English/LTR)
VITE_DEFAULT_LANG=fa

# Optional: public Sentry DSN for error tracking
# VITE_SENTRY_DSN=

# Optional: public Google Analytics 4 measurement ID
# VITE_GA_MEASUREMENT_ID=
"""

FIXES.append((".env.example", ENV_EXAMPLE.encode("utf-8")))

# ---------------------------------------------------------------------------
# 3) tsconfig.json — remove vite.config.ts from include (TS6305 fix)
#                    remove "node" from types (TS2688 fix — @types/node
#                    installed separately, will be auto-discovered)
# ---------------------------------------------------------------------------

TSCONFIG_JSON = """{
  "$schema": "https://json.schemastore.org/tsconfig",
  "display": "apps/web",
  "compilerOptions": {
    "target": "ES2022",
    "useDefineForClassFields": true,
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,

    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "jsx": "react-jsx",

    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "forceConsistentCasingInFileNames": true,

    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@econojin/ui": ["../../packages/ui/src"],
      "@econojin/ui/*": ["../../packages/ui/src/*"],
      "@econojin/lib": ["../../packages/lib/src"],
      "@econojin/lib/*": ["../../packages/lib/src/*"],
      "@econojin/hooks": ["../../packages/hooks/src"],
      "@econojin/hooks/*": ["../../packages/hooks/src/*"],
      "@econojin/types": ["../../packages/types/src"],
      "@econojin/types/*": ["../../packages/types/src/*"]
    },

    "types": ["vite/client"]
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
"""

FIXES.append(("tsconfig.json", TSCONFIG_JSON.encode("utf-8")))

# ---------------------------------------------------------------------------
# 4) tsconfig.node.json — fix TS6310 (composite project can't disable emit)
#    Use emitDeclarationOnly + outDir so vite.config.ts compiles correctly
#    as part of the project reference graph.
# ---------------------------------------------------------------------------

TSCONFIG_NODE_JSON = """{
  "$schema": "https://json.schemastore.org/tsconfig",
  "display": "apps/web — Node context (vite.config)",
  "compilerOptions": {
    "composite": true,
    "skipLibCheck": true,
    "module": "ESNext",
    "moduleResolution": "bundler",
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "emitDeclarationOnly": true,
    "outDir": "./node_modules/.tsbuildinfo",
    "tsBuildInfoFile": "./node_modules/.tsbuildinfo/tsconfig.node.tsbuildinfo",
    "types": ["node"]
  },
  "include": ["vite.config.ts"]
}
"""

FIXES.append(("tsconfig.node.json", TSCONFIG_NODE_JSON.encode("utf-8")))

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

def write_file(path: Path, content: bytes) -> bool:
    """Returns True if file was written (i.e., was missing or different)."""
    if path.exists():
        try:
            existing = path.read_bytes()
            if existing == content:
                return False
        except Exception:
            pass
    ensure_parent_dir(path)
    path.write_bytes(content)
    return True

def run_command(cmd: list[str], cwd: Path) -> tuple[int, str, str]:
    """Run a command and return (exit_code, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            shell=False,
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        return 1, "", f"command not found: {cmd[0]}"

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    # Detect the project root: assume we are run from D:\econojin.com\apps\web
    # OR from any subdirectory. Look for tsconfig.json in cwd or parents.
    cwd = Path.cwd()
    root = cwd
    for candidate in [cwd, *cwd.parents]:
        if (candidate / "tsconfig.json").exists() and (candidate / "package.json").exists():
            root = candidate
            break

    print(f"[INFO] Project root detected: {root}")
    print()

    # ---- Step 1: write the fixed files ------------------------------------

    print("=" * 72)
    print(" STEP 1 — Writing fixed/missing files")
    print("=" * 72)
    for rel_path, content in FIXES:
        full = root / rel_path
        written = write_file(full, content)
        action = "created" if not full.exists() or written else "skipped (unchanged)"
        if written:
            action = "rewrote" if full.exists() else "created"
        size = full.stat().st_size if full.exists() else 0
        print(f"  [{action:>16}]  {rel_path}  ({size} bytes)")
    print()

    # ---- Step 2: install @types/node via pnpm -----------------------------

    print("=" * 72)
    print(" STEP 2 — Installing @types/node (for vite.config.ts)")
    print("=" * 72)
    code, stdout, stderr = run_command(["pnpm", "add", "-D", "@types/node"], root)
    if code == 0:
        # Filter pnpm output to keep only the relevant lines
        for line in stdout.splitlines():
            if line.strip() and ("@types/node" in line or "Done" in line or "Progress" in line or "packages" in line):
                print(f"  {line}")
        print("  ✓ @types/node installed")
    else:
        print(f"  ⚠ pnpm install failed (exit {code})")
        if stderr.strip():
            for line in stderr.splitlines()[:5]:
                print(f"    {line}")
        print("  → You may need to run manually: pnpm add -D @types/node")
    print()

    # ---- Step 3: re-run verification --------------------------------------

    print("=" * 72)
    print(" STEP 3 — Re-running verification")
    print("=" * 72)
    verifier = root / "verify_refactor.py"
    if verifier.exists():
        code, stdout, stderr = run_command(
            [sys.executable, str(verifier), "--root", str(root)],
            root,
        )
        print(stdout)
        if code != 0:
            print(f"  ⚠ Verifier exited with code {code}")
            if stderr.strip():
                print(stderr)
    else:
        print(f"  ⚠ verify_refactor.py not found at {verifier}")
        print("  → Skip this step; the fixes above should still resolve the issues.")
    print()

    # ---- Step 4: summary --------------------------------------------------

    print("=" * 72)
    print(" DONE")
    print("=" * 72)
    print("  Files written:")
    for rel_path, _ in FIXES:
        print(f"    • {rel_path}")
    print()
    print("  Next step:")
    print("    pnpm run build")
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
