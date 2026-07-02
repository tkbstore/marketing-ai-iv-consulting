# Marketing AI — IV Consulting

Marketing AI platform for IV Consulting.

## Setup

```bash
pip install -e .
cp .env.example .env  # Fill in API keys
python -m web         # http://localhost:8501
```

## Features

- Hypothesis Lab: 仮説・実験・エビデンスのグラフDB管理
- Kanban Board: ステータス別カンバンビュー
- AEO Dashboard: AI検索引用エビデンス管理
- MCP Servers: GA4 / GSC / Meta Ads 接続（独立起動可能）

## Development

```bash
pip install -e ".[dev]"
ruff check .
pytest tests/
```
