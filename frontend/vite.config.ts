import { defineConfig } from "vite";
import preact from "@preact/preset-vite";

export default defineConfig({
  plugins: [preact()],
  server: {
    host: "0.0.0.0",
    port: 3400,
    strictPort: true,
    allowedHosts: ["s2.local"],
  },
});
