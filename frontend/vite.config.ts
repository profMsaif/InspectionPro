import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      app: fileURLToPath(new URL("./src/app", import.meta.url)),
      features: fileURLToPath(new URL("./src/features", import.meta.url)),
      pages: fileURLToPath(new URL("./src/pages", import.meta.url)),
      shared: fileURLToPath(new URL("./src/shared", import.meta.url)),
      widgets: fileURLToPath(new URL("./src/widgets", import.meta.url)),
    },
  },
  server: {
    port: 5173,
    host: "0.0.0.0",
    proxy: {
      "/api": {
        target: "http://backend:8000",
        changeOrigin: true,
      },
    },
  },
});
