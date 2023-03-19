import DefaultTheme from "vitepress/theme";

import { App } from "vue";
import JsonViewer from "vue3-json-viewer";
import "vue3-json-viewer/dist/index.css";
import "./custom.css";

export default {
  ...DefaultTheme,
  enhanceApp({ app }) {
    app.use(JsonViewer);
    // app.component("json-viewer", VueClickAwayExample);
  },
};
