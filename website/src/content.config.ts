import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

/**
 * リサーチノート（バークシャー・ハサウェイ研究）。
 * 記事を追加するには src/content/research/ に .md ファイルを置くだけでよい。
 */
const research = defineCollection({
  loader: glob({ pattern: "**/*.md", base: "./src/content/research" }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    pubDate: z.coerce.date(),
    updatedDate: z.coerce.date().optional(),
    /** 一次資料へのリンク */
    sources: z
      .array(z.object({ label: z.string(), url: z.string().url() }))
      .default([]),
  }),
});

export const collections = { research };
