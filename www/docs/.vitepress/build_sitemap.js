const sm = require("sitemap-ts");

function buildEnd() {
  const opt = sm.resolveOptions({
    hostname: "https://kellerza.github.io/",
    basePath: "/sunsynk",
    outDir: "docs/.vitepress/dist",
    exclude: ["/404"],
    readable: true,
  });

  sm.generateSitemap(opt);
}

buildEnd();
