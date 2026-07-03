// @ts-check
import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

// GitHub Pages: tkbstore.github.io/marketing-ai-iv-consulting
// カスタムドメイン設定後は SITE_URL を差し替え、base を削除する
const SITE_URL = "https://tkbstore.github.io";
const BASE_PATH = "/marketing-ai-iv-consulting";

export default defineConfig({
  site: SITE_URL,
  base: BASE_PATH,
  trailingSlash: "never",
  integrations: [sitemap()],
  build: {
    inlineStylesheets: "auto",
  },
});
