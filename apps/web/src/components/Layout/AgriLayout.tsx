/**
 * ============================================================================
 *  AgriLayout — Layout wrapper with AgriSidebar for agriculture pages
 *  Inspired by agri-moon layout patterns
 * ============================================================================
 */

import { type ReactNode } from "react";

import { AgriSidebar } from "@/components/Layout/AgriSidebar";
import { Header } from "@/components/Layout/Header";
import { cn } from "@/lib/utils";

interface AgriLayoutProps {
  children: ReactNode;
}

export function AgriLayout({ children }: AgriLayoutProps): JSX.Element {
  return (
    <div className="flex min-h-screen flex-col bg-gray-50 dark:bg-gray-950">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <AgriSidebar />
        <main className="flex-1 overflow-y-auto" role="main">
          {children}
        </main>
      </div>
    </div>
  );
}