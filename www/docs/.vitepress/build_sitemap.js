import {resolveOptions, generateSitemap} from "sitemap-ts";

function buildEnd() {
  const opt = resolveOptions({
    hostname: "https://sunsynk.wectrl.net/",
    basePath: "/",
    outDir: "docs/.vitepress/dist",
    exclude: ["/404"],
    readable: true,
  });

  generateSitemap(opt);
}

buildEnd();
