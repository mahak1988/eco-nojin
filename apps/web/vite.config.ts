import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

/** Always proxy to loopback — avoid LAN IP / dual-stack issues on Windows. */
const API = process.env.VITE_PROXY_TARGET || "http://127.0.0.1:8000";

function apiProxy() {
  return {
    target: API,
    changeOrigin: true,
    secure: false,
    timeout: 60_000,
    proxyTimeout: 60_000,
    configure: (proxy: { on: (ev: string, fn: (...args: unknown[]) => void) => void }) => {
      proxy.on("error", (err: unknown) => {
        console.warn("[vite proxy] API error →", API, err);
      });
      proxy.on("proxyReq", () => {
        /* keep connection alive for long NDVI */
      });
    },
  };
}

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    // Use localhost only — opening via 192.168.x.x often breaks HMR/proxy on Windows
    host: "127.0.0.1",
    port: 5173,
    strictPort: false,
    proxy: {
      "/api": apiProxy(),
      "/health": apiProxy(),
      "/modules": apiProxy(),
      "/docs": apiProxy(),
      "/openapi.json": apiProxy(),
    },
  },
});
