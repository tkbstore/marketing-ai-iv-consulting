"""Seed data for IV Consulting hypothesis lab."""

from web import db


def seed_all() -> None:
    """Create initial hypotheses for IV Consulting marketing."""

    h1 = db.create_node(
        "hypothesis",
        "コンサルティング業界でのAI検索最適化（AEO）は新規リード獲得に有効",
        description="AI検索エンジン（ChatGPT, Perplexity等）で「コンサルティング」関連クエリに引用されることで、"
                    "従来のSEOでは到達できない層へのリーチが可能になる仮説。",
        status="draft",
        tags=["aeo", "lead-gen"],
    )

    h2 = db.create_node(
        "hypothesis",
        "LinkedInコンテンツ発信が代表のパーソナルブランディングとリード獲得を同時に実現",
        description="大島氏のLinkedInでの業界知見発信が、IV Consultingの認知度向上と"
                    "インバウンドリード獲得の両方に寄与する仮説。",
        status="draft",
        tags=["linkedin", "personal-branding", "lead-gen"],
    )

    h3 = db.create_node(
        "hypothesis",
        "業界特化コンテンツ（ケーススタディ・ホワイトペーパー）がCVRを改善",
        description="汎用的なコンサルティング紹介ではなく、業界特化の具体的な成功事例や"
                    "ホワイトペーパーを公開することで、サイト訪問者のコンバージョン率が向上する仮説。",
        status="draft",
        tags=["content", "cvr", "case-study"],
    )

    # Create experiments linked to hypotheses
    e1 = db.create_node(
        "experiment",
        "GPR実験: コンサルティング関連クエリ20件でのAI検索引用調査",
        description="ChatGPT, Perplexity, Geminiで「経営コンサルティング」「業務改善コンサルティング」等の"
                    "クエリを実行し、IV Consultingまたは競合の引用状況を調査。",
        status="draft",
        parent_id=h1["id"],
        tags=["gpr", "aeo"],
    )

    e2 = db.create_node(
        "experiment",
        "LinkedIn投稿テスト: 週3回×4週間の業界知見投稿",
        description="大島氏のLinkedInアカウントで業界知見を週3回投稿し、"
                    "インプレッション・エンゲージメント・プロフィール訪問数の変化を計測。",
        status="draft",
        parent_id=h2["id"],
        tags=["linkedin", "content"],
    )

    # Link experiments to hypotheses
    db.create_edge(h1["id"], e1["id"], "tests")
    db.create_edge(h2["id"], e2["id"], "tests")
