import type { NextConfig } from "next";

// Static export for GitHub Pages.
// - output: "export"   -> `next build` emits a static site into `out/`
// - basePath           -> GitHub *project* pages serve under /<repo>/, set via
//                         NEXT_PUBLIC_BASE_PATH in the deploy workflow (empty
//                         locally, so `npm run dev` / local build stay at "/")
// - images.unoptimized -> required: the Next image optimizer needs a server
// - trailingSlash      -> emit /ask/index.html so paths resolve as static files
const basePath = process.env.NEXT_PUBLIC_BASE_PATH || "";

const nextConfig: NextConfig = {
  output: "export",
  images: { unoptimized: true },
  trailingSlash: true,
  ...(basePath ? { basePath, assetPrefix: basePath } : {}),
};

export default nextConfig;
