/**
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
