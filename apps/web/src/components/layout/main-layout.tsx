"use client";

import { motion } from "framer-motion";
import { Sidebar } from "./sidebar";
import { Header } from "./header";
import { useAppStore } from "@/store/useAppStore";
import { cn } from "@/lib/utils";

export function MainLayout({ children }: { children: React.ReactNode }) {
  const { sidebarOpen } = useAppStore();
  
  return (
    <div className="min-h-screen relative flex overflow-hidden">
      {/* ================================================================== */}
      {/* 🌿 Ambient Background - Nature Distilled */}
      {/* ================================================================== */}
      <div className="fixed inset-0 -z-10 pointer-events-none">
        {/* Base color - ارگانیک و عمیق */}
        <div className="absolute inset-0 bg-[#0a0a0c]" />
        
        {/* Mesh gradient - حس طبیعت و تکنولوژی */}
        <div 
          className="absolute inset-0 opacity-50"
          style={{
            backgroundImage: `
              radial-gradient(at 15% 15%, rgba(16, 185, 129, 0.12) 0px, transparent 50%),
              radial-gradient(at 85% 25%, rgba(59, 130, 246, 0.1) 0px, transparent 50%),
              radial-gradient(at 50% 85%, rgba(139, 92, 246, 0.08) 0px, transparent 50%),
              radial-gradient(at 25% 75%, rgba(20, 184, 166, 0.1) 0px, transparent 50%)
            `
          }}
        />
        
        {/* Noise texture - Tactile Maximalism */}
        <div 
          className="absolute inset-0 opacity-[0.025] mix-blend-overlay"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E")`
          }}
        />
      </div>

      {/* ================================================================== */}
      {/* 📱 Sidebar - با انیمیشن نرم */}
      {/* ================================================================== */}
      <Sidebar />

      {/* ================================================================== */}
      {/* 📄 Main Content Area */}
      {/* ================================================================== */}
      <motion.div 
        className={cn(
          "flex-1 flex flex-col min-w-0 relative",
          sidebarOpen && "lg:mr-72"
        )}
        initial={false}
        animate={{
          marginRight: sidebarOpen ? "18rem" : "0rem"
        }}
        transition={{
          type: "spring",
          stiffness: 300,
          damping: 30
        }}
      >
        <Header />
        
        {/* Main Content - با spacing تنفس‌پذیر */}
        <main className="flex-1 p-5 lg:p-8 overflow-auto relative">
          {/* Content wrapper با انیمیشن ورود */}
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.1 }}
            className="h-full"
          >
            {children}
          </motion.div>
        </main>
      </motion.div>
    </div>
  );
}