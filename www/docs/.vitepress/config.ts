import { defineConfig } from "vitepress";

export default defineConfig({
  lang: "en-US",
  title: "sunsynk",
  base: "/sunsynk/",
  description: "Take control of your inverter.",
  lastUpdated: true,
  cleanUrls: true,
  head: [
    [
      "link",
      {
        rel: "apple-touch-icon",
        sizes: "180x180",
        href: "/apple-touch-icon.png",
      },
    ],
    [
      "link",
      {
        rel: "icon",
        type: "image/png",
        sizes: "32x32",
        href: "/favicon-32x32.png",
      },
    ],
    [
      "link",
      {
        rel: "icon",
        type: "image/png",
        sizes: "16x16",
        href: "/favicon-16x16.png",
      },
    ],
    [
      "meta",
      { name: "viewport", content: "width=device-width, initial-scale=1.0" },
    ],
  ],
  // vite: {
  //   buildEnd: buildEnd,
  // },
  themeConfig: {
    logo: "/labctl1.svg",
    nav: [
      {
        text: "Getting started",
        link: "/guide/getting-started",
        activeMatch: "/guide/",
      },
      {
        text: "Reference",
        link: "/reference/multi-options",
        activeMatch: "/reference/",
      },
      {
        text: "Examples",
        link: "/examples/overview",
        activeMatch: "/examples/",
      },
    ],
    sidebar: [
      {
        text: "Guide",
        items: [
          {
            text: "Overview",
            link: "/guide/overview",
            items: [
              {
                text: "Tested Inverters",
                link: "/guide/tested-inverters",
              },
            ],
          },
          {
            text: "Getting Started",
            link: "/guide/getting-started",
            items: [
              {
                text: "Deployment options",
                link: "/guide/deployment-options",
              },
              { text: "Fault Finding", link: "/guide/fault-finding" },
            ],
          },
          { text: "Energy Management", link: "/guide/energy-management" },
        ],
      },
      {
        text: "Reference",
        items: [
          { text: "Addon options", link: "/reference/multi-options" },
          { text: "Modifiers", link: "/reference/sensor-modifiers" },
          { text: "Sensors", link: "/reference/definitions" },
          { text: "Custom sensors", link: "/reference/mysensors" },
        ],
      },
      {
        text: "Examples",
        items: [
          { text: "Overview", link: "/examples/overview" },
          { text: "Lovelace",
            link: "/examples/lovelace",
            items: [
              { text: "Settings", link: "/examples/lovelace-settings" },
            ],
          },
          { text: "Automations", link: "/examples/a-mode" },
          { text: "Templates", link: "/examples/templates" },
        ],
      },
    ],

    editLink: {
      pattern: "https://github.com/kellerza/sunsynk/edit/main/www/docs/:path",
      text: "Edit this page on GitHub",
    },

    socialLinks: [
      { icon: "github", link: "https://github.com/kellerza/sunsynk" },
    ],

    footer: {
      message: "",
      copyright: "Apache 2.0 | Copyright © 2021-2023 Johann Kellerman",
    },

    algolia: {
      appId: "ZZ2YT4M4EY",
      apiKey: "3fda4c9bd770052e9e3ebeb213af2a82",
      indexName: "sunsynk",
    },
  },
  markdown: {
    config: md => {
      md.use(require('markdown-it-imsize'))
    },
  },
});
