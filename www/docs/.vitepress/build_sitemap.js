import {resolveOptions, generateSitemap} from "sitemap-ts";

function buildEnd() {
  const opt = resolveOptions({
    hostname: "https://sunsynk.wectrl.net",
    basePath: "/",
    outDir: "docs/.vitepress/dist",
    exclude: ["/404"],
    readable: true,
    transformURL: (url) => {
      return url.replace(/([^:])\/+/g, '$1/');
    }
  });

  generateSitemap(opt);
}

buildEnd();
