/**
 * ============================================================================
 *  Layout — shell that composes Header + Sidebar + content + Footer + CommandPalette
 * ============================================================================
 */

import { useState, type ReactNode } from "react";

import { Footer } from "@/components/Layout/Footer";
import { Header } from "@/components/Layout/Header";
import { Sidebar } from "@/components/Layout/Sidebar";
import { CommandPalette } from "@/components/CommandPalette/CommandPalette";
import { useLanguage } from "@/hooks/useLanguage";
import { useCommandPalette } from "@/hooks/useCommandPalette";

export interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps): JSX.Element {
  const { dir } = useLanguage();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const palette = useCommandPalette();

  return (
    <div dir={dir} className="flex min-h-screen flex-col bg-gray-50">
      <Header onToggleSidebar={() => setSidebarOpen((v) => !v)} />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <main className="flex-1 overflow-y-auto" role="main">
          {children}
          <Footer />
        </main>
      </div>

      {/* Global Command Palette (Ctrl+K) */}
      <CommandPalette isOpen={palette.isOpen} onClose={palette.close} />
    </div>
  );
}
