#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Eco Nojin - Complete main.tsx Rewrite
======================================
بازنویسی کامل main.tsx با QueryClientProvider در جای درست

این اسکریپت:
✅ فایل main.tsx را کاملاً بازنویسی می‌کند
✅ QueryClientProvider را در parent chain قرار می‌دهد
✅ ترتیب صحیح Providerها را حفظ می‌کند
✅ خطای "No QueryClient set" را رفع می‌کند
"""

from pathlib import Path
import shutil

PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAIN_TSX = PROJECT_ROOT / "apps" / "web" / "src" / "main.tsx"

NEW_MAIN_TSX = '''/**
 * ============================================================================
 *  main.tsx — application entry point (Vite + React 18 + i18n)
 * ============================================================================
 *
 *  Provider order (outer → inner):
 *    1. StrictMode        (React strict mode)
 *    2. ErrorBoundary     (catches render errors from any child)
 *    3. QueryClientProvider (React Query - MUST be before AuthProvider)
 *    4. BrowserRouter     (URL ↔ UI sync)
 *    5. AuthProvider      (session state — needed by router guards)
 *    6. App               (routes + layout)
 *
 *  i18n is initialized by importing @/i18n (side-effect import).
 * ============================================================================
 */

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { QueryClientProvider } from "@tanstack/react-query";

// Side-effect import — initializes i18n BEFORE React mounts
import "@/i18n";

import { App } from "@/App";
import { AuthProvider } from "@/hooks/useAuth";
import { ErrorBoundary } from "@/components/common/ErrorBoundary";
import { queryClient } from "@/lib/query-client";
import "@/styles/index.css";

// ---------------------------------------------------------------------------
// Root element
// ---------------------------------------------------------------------------

const container = document.getElementById("root");

if (!container) {
  throw new Error(
    "Root element #root not found. Ensure index.html contains <div id='root'></div>.",
  );
}

// ---------------------------------------------------------------------------
// Render
// ---------------------------------------------------------------------------

createRoot(container).render(
  <StrictMode>
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>
          <AuthProvider>
            <App />
          </AuthProvider>
        </BrowserRouter>
      </QueryClientProvider>
    </ErrorBoundary>
  </StrictMode>,
);
'''


def main():
    print("\n" + "=" * 70)
    print("🔧 Complete main.tsx Rewrite")
    print("=" * 70)
    
    if not MAIN_TSX.exists():
        print(f"\n❌ main.tsx not found at: {MAIN_TSX}")
        return
    
    # Backup
    backup_path = MAIN_TSX.with_suffix(".tsx.backup_final")
    try:
        shutil.copy2(MAIN_TSX, backup_path)
        print(f"\n💾 Backup created: {backup_path.name}")
    except Exception as e:
        print(f"\n⚠️  Backup failed: {e}")
    
    # Write new content
    try:
        MAIN_TSX.write_text(NEW_MAIN_TSX, encoding="utf-8")
        print(f"\n✅ main.tsx rewritten successfully")
        
        print(f"\n📝 Key changes:")
        print(f"   1. Added QueryClientProvider to JSX tree")
        print(f"   2. Placed it BEFORE AuthProvider (required)")
        print(f"   3. Maintained correct provider order:")
        print(f"      StrictMode → ErrorBoundary → QueryClientProvider")
        print(f"      → BrowserRouter → AuthProvider → App")
    except Exception as e:
        print(f"\n❌ Failed to write main.tsx: {e}")
        return
    
    print("\n" + "=" * 70)
    print("✅ Rewrite completed!")
    print("=" * 70)
    
    print("\n📌 Next steps:")
    print("   1. Restart dev server: Ctrl+C, then pnpm dev")
    print("   2. Check browser console - error should be gone")
    print("   3. Login page should render correctly")


if __name__ == "__main__":
    main()