import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

// BEGIN: VITE_CONFIG

export default defineConfig({
  plugins: [react()],
  root: __dirname,
  build: {
    // Output to ../static (shared parent folder)
    outDir: path.resolve(__dirname, "../static"),
    emptyOutDir: false, // don't clear other folders
    rollupOptions: {
      // two entry points
      input: {
        repdeck: path.resolve(__dirname, "src/main.tsx"),
        home: path.resolve(__dirname, "src/home.tsx"),
      },
      output: {
        // ✅ keep folder structure flat under /static
        entryFileNames: (chunkInfo) => {
          // Put each entry in its own top-level folder
          if (chunkInfo.name === "repdeck") return "repdeck/index.js";
          if (chunkInfo.name === "home") return "home/index.js";
          return "assets/[name]-[hash].js";
        },
        chunkFileNames: "assets/[name]-[hash].js",
        assetFileNames: "assets/[name]-[hash][extname]",
        // ✅ Important fix: prevent double nesting
        manualChunks: undefined,
      },
    },
  },
});

// END: VITE_CONFIG