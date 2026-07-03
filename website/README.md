# IV Consulting コーポレートサイト

株式会社IV Consulting の公式Webサイト。[Astro](https://astro.build) 製の完全静的サイト（高速・安全・AEO最適）。

## デザインコンセプト: "The Annual Report"

バークシャー・ハサウェイの年次報告書を想起させる、紙のエディトリアルデザイン。

- **素材**: クリーム紙 × インク黒 × オックスブラッド（報告書表紙の臙脂）× 控えめな金
- **構造**: 帳簿の罫線、番号付きセクション、財務諸表風テーブル、表紙風ヒーロー（"IV" 透かし + Est. 2025 メタ情報）
- **タイポグラフィ**: しっぽり明朝（見出し・本文）+ サンセリフ（ラベル・ナビ）の2書体構成
- **動き**: 「ページをめくる」ように静かに。スクロール連動フェードアップ（IntersectionObserver）、ナビの下線、帳簿行のホバー（臙脂の付箋線）、FAQの高さ補間。すべて `transform` / `opacity` のみで、`prefers-reduced-motion` 時は全停止
- **JavaScript**: スクロールリビール用の数行のインラインJSのみ（外部ライブラリなし）。JS無効環境でも全コンテンツが表示される

## 起動方法

```bash
cd website
npm install
npm run dev      # http://localhost:4321
npm run build    # dist/ に静的ファイルを出力
```

## 管理者向け: コンテンツの更新方法

コードを書かなくても、以下のファイルを編集するだけでサイト全体が更新されます。

| 更新したい内容 | 編集するファイル |
|---|---|
| 会社情報・代表経歴・サービス・FAQ | `src/data/company.ts`（全ページと構造化データに自動反映） |
| リサーチ記事の追加 | `src/content/research/` に `.md` ファイルを追加するだけ |
| リサーチ記事の修正 | 該当の `.md` ファイルを編集 |
| デザイン（色・フォント・余白） | `src/styles/global.css` の `:root` トークン |

### リサーチ記事の書き方

`src/content/research/新しい記事.md` を作成:

```markdown
---
title: 記事タイトル
description: 記事の要約（AI検索の引用に使われるため、自己完結した1〜2文で）
pubDate: 2026-01-15
sources:
  - label: 参考資料の名前
    url: https://example.com
---

本文をMarkdownで書く。
```

保存してビルド（またはgit push）すれば、一覧・サイトマップ・構造化データすべてに自動反映されます。

## ホスティング（推奨: Cloudflare Pages）

完全静的サイトなので、無料枠で運用できます。

### Cloudflare Pages（推奨・無料）

1. GitHubリポジトリを接続
2. Build command: `npm run build` ／ Build output: `dist` ／ Root directory: `website`
3. カスタムドメインを設定

**注意**: Cloudflareの「AI bot をブロック」設定は必ず **オフ** にすること（AEOの前提が崩れます）。

### Vercel / Netlify

同様の設定で動作します（フレームワークプリセット: Astro）。

## ドメイン確定後にやること

現在は仮URL `https://www.iv-consulting.jp` を使用。確定後に以下を置換:

1. `astro.config.mjs` の `SITE_URL`
2. `src/data/company.ts` の `SITE_URL`
3. `public/robots.txt` の Sitemap 行

## AEO（AI検索最適化）実装済み項目

- **JSON-LD構造化データ**: Organization / Person（代表） / WebSite（全ページ）、FAQPage（/faq）、Article + BreadcrumbList（リサーチ記事）、Service（/services）
- **robots.txt**: GPTBot / ClaudeBot / PerplexityBot / Google-Extended 等を明示的に許可
- **sitemap**: `@astrojs/sitemap` で自動生成（`/sitemap-index.xml`）
- **セマンティックHTML**: 見出し階層・`<time>`・`<details>` によるQ&A構造
- **自己完結型コンテンツ**: FAQと記事冒頭は、単独で引用されても意味が通る文章で記述
- **ゼロJS・静的HTML**: クローラーはレンダリング不要で全文を取得可能

## コンテンツ上の注意（重要）

- 代表経歴は **LinkedIn公開情報に基づく事実のみ** を記載する
- 光通信の株式保有に関する記述は **一切入れない**
- ファームとしての過去実績は捏造しない（研究公開で信頼を担保する方針）
