# Marketing AI — IV Consulting

スタンドアロン型マーケティングAI MVPプラットフォーム。
仮説検証ラボ + GA4/GSC/Meta Ads接続 + AEO(AI検索最適化) + 広告効果ダッシュボード。

クライアント: IV Consulting（コンサルティング会社）
代表: 大島 俊哉（Toshiya Oshima）
LinkedIn: https://www.linkedin.com/in/toshiya-oshima-95220958/
ドメイン: TBD

## Quick Start

```bash
pip install -e .
cp .env.example .env  # Fill in API keys
python -m web         # http://localhost:8501
```

## MCP Servers

| Server | Module | Tools | Purpose |
|--------|--------|-------|---------|
| ga4 | `mcp_servers.ga4` | 8 | GA4レポート、リアルタイム、地域別分析 |
| search-console | `mcp_servers.search_console` | 8 | 検索パフォーマンス、URL検査 |
| meta-ads | `mcp_servers.meta_ads` | 7 | キャンペーン管理、インサイト |

## Web UI Pages

| Page | Path | Description |
|------|------|-------------|
| Dashboard | `/` | 仮説・実験結果・エビデンス統計 |
| Board | `/board` | カンバンボード |
| Experiments | `/experiments` | ガントチャート（依存関係付き） |
| Ad Effectiveness | `/ad-effectiveness` | Meta Ads + GA4統合ダッシュボード |
| AEO | `/aeo` | AI検索引用エビデンス管理 |
| Map | `/map` | GPRテリトリーマップ（sighted-mcp-platform連携） |
| Node Detail | `/node/{id}` | 仮説/実験/エビデンス詳細 + 実験生成 |

## Architecture

- **MCP Servers**: 各プラットフォームのAPI接続（独立起動可能）
- **Shared Utils**: rate_limiter, retry, events(ログ), auth
- **Hypothesis Lab**: SQLiteグラフDB + FastAPI + Jinja2テンプレート
- **AEO Module**: sighted-qa MCP連携 or 手動エビデンス入力

## Client Info (TODO)

- [ ] 会社概要・事業内容
- [ ] ターゲット顧客層
- [ ] 競合他社
- [ ] 現在のウェブサイトURL
- [ ] SNSアカウント
- [ ] 業界特有のKPI
- [ ] マーケティング課題・目標

## Environment Variables

### Required (Google)
- `GOOGLE_APPLICATION_CREDENTIALS` — GCPサービスアカウントJSON
- `GA4_PROPERTY_ID` — GA4プロパティID
- `GSC_SITE_URL` — IV ConsultingサイトURL

### Meta Ads
- `META_APP_ID`, `META_APP_SECRET`, `META_ACCESS_TOKEN`, `META_AD_ACCOUNT_ID`

### Optional
- `SIGHTED_QA_MCP_URL` — AEO用sighted-qa MCP URL
- `SIGHTED_PLATFORM_URL` — テリトリーマップ用sighted-mcp-platform URL

## Conventions

- All tool returns are JSON strings
- `json.dumps(result, ensure_ascii=False, default=str)` for serialization
- Each server independently runnable: `python -m mcp_servers.<name>.server`
- Config via environment variables only
- All API calls go through rate_limiter and retry decorators

## Development

- Python 3.12+
- Install: `pip install -e ".[dev]"`
- Lint: `ruff check .`
- Test: `pytest tests/`
