import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

const API = process.env.VITE_PROXY_TARGET || "http://127.0.0.1:8000";

function apiProxy() {
  return {
    target: API,
    changeOrigin: true,
    secure: false,
    timeout: 20_000,
    configure: (proxy: {
      on: (ev: string, fn: (...args: unknown[]) => void) => void;
    }) => {
      proxy.on("error", (err: unknown) => {
        console.warn("[vite proxy] backend unreachable at", API, err);
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
    port: 5173,
    host: true,
    proxy: {
      "/api": apiProxy(),
      "/health": apiProxy(),
      "/modules": apiProxy(),
      "/docs": apiProxy(),
      "/openapi.json": apiProxy(),
    },
  },
});
