import DefaultTheme from "vitepress/theme";

import JsonViewer from "vue3-json-viewer";
import "vue3-json-viewer/dist/vue3-json-viewer.css";
import "./custom.css";
import type { EnhanceAppContext } from "vitepress";

export default {
  ...DefaultTheme,
  enhanceApp(ctx:EnhanceAppContext) {
    ctx.app.use(JsonViewer);
    // app.component("json-viewer", VueClickAwayExample);
  },
};
