import type { NextConfig } from "next";

// Site tamamen statiktir: veriler build sırasında src/data/*.json dosyalarından okunur
// (bkz. ../scripts/export_web_data.py). `next build` çıktısı `out/` klasörüne yazılır.
const nextConfig: NextConfig = {
  output: "export",
  trailingSlash: true,
  images: { unoptimized: true },
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
