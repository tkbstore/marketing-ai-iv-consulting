"""Hypothesis generation for the directed-graph model."""

from __future__ import annotations

from web import db


def generate_hypotheses() -> list[dict]:
    """Generate seed data using the graph model."""
    existing = db.list_nodes()
    if not existing:
        from web.seed import seed_all
        seed_all()
        return db.list_nodes()

    h = db.create_node(
        "hypothesis",
        "New hypothesis (click to edit)",
        description="Describe your hypothesis here",
        status="draft",
    )
    return [h]
