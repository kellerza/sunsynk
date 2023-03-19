const sm = require("sitemap-ts");

function buildEnd() {
  const opt = sm.resolveOptions({
    hostname: "https://github.io/kellerza/sunsynk/",
    outDir: "docs/.vitepress/dist",
    exclude: ["/404"],
  });
  // opt.dynamicRoutes = sm.getRoutes(opt);

  // Add "/" to work with VitePress's cleanUrls="with-subfolders"
  // Github pages adds the slash & redirects to folder/
  // opt.dynamicRoutes = opt.dynamicRoutes.map((route) =>
  //   route.endsWith("/") ? route : route + "/"
  // );

  sm.generateSitemap(opt);
}

buildEnd();
