import {resolveOptions, generateSitemap} from "sitemap-ts";

function buildEnd() {
  const opt = resolveOptions({
    hostname: "https://kellerza.github.io/",
    basePath: "/sunsynk",
    outDir: "docs/.vitepress/dist",
    exclude: ["/404"],
    readable: true,
  });

  generateSitemap(opt);
}

buildEnd();
