// @ts-check
import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

// TODO: 本番ドメイン確定後にここを差し替える（llms.txt / robots.txt 内のURLも同様）
const SITE_URL = "https://www.iv-consulting.jp";

export default defineConfig({
  site: SITE_URL,
  trailingSlash: "never",
  integrations: [sitemap()],
  build: {
    inlineStylesheets: "auto",
  },
});
