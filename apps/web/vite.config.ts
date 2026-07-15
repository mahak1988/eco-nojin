/**
 * Vite configuration — apps/web
 * Path aliases MUST match tsconfig.json `paths`.
 * @type {import('vite').UserConfig}
 */
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "src"),
      "@econojin/ui": path.resolve(__dirname, "../../packages/ui/src"),
      "@econojin/lib": path.resolve(__dirname, "../../packages/lib/src"),
      "@econojin/hooks": path.resolve(__dirname, "../../packages/hooks/src"),
      "@econojin/types": path.resolve(__dirname, "../../packages/types/src"),
    },
  },
  server: {
    port: 5173,
    strictPort: false,
  },
  build: {
    outDir: "dist",
    sourcemap: true,
    target: "es2022",
  },
});
