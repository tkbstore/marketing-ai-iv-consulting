"""IV Consulting — Marketing AI Dashboard.

Usage:
    python -m web
"""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from web import db

BASE_DIR = Path(__file__).resolve().parent

_db_initialized = False


def _ensure_db():
    global _db_initialized
    if not _db_initialized:
        db.init_db()
        _db_initialized = True


@asynccontextmanager
async def lifespan(app: FastAPI):
    _ensure_db()
    yield


app = FastAPI(title="IV Consulting Marketing AI", lifespan=lifespan)


def _render(name: str, ctx: dict):
    request = ctx["request"]
    try:
        return templates.TemplateResponse(request, name, ctx)
    except TypeError:
        return templates.TemplateResponse(name, ctx)


@app.middleware("http")
async def ensure_db_middleware(request, call_next):
    _ensure_db()
    response = await call_next(request)
    return response


app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


# --- Pages ---

@app.get("/", response_class=HTMLResponse)
def dashboard(request: Request):
    """Main dashboard: hypotheses, experiments, evidence stats."""
    nodes = db.list_nodes()
    hypotheses = [n for n in nodes if n["type"] == "hypothesis"]
    experiments = [n for n in nodes if n["type"] == "experiment"]
    evidence = db.list_evidence(limit=20)
    return _render("app/dashboard.html", {
        "request": request,
        "hypotheses": hypotheses,
        "experiments": experiments,
        "evidence": evidence,
        "stats": {
            "total_hypotheses": len(hypotheses),
            "total_experiments": len(experiments),
            "total_evidence": len(evidence),
        },
    })


@app.get("/board", response_class=HTMLResponse)
def board(request: Request):
    """Kanban board view."""
    nodes = db.list_nodes()
    columns = {
        "draft": [n for n in nodes if n["status"] == "draft"],
        "active": [n for n in nodes if n["status"] == "active"],
        "completed": [n for n in nodes if n["status"] == "completed"],
    }
    return _render("app/board.html", {
        "request": request,
        "columns": columns,
    })


@app.get("/aeo", response_class=HTMLResponse)
def aeo(request: Request):
    """AEO evidence dashboard."""
    evidence = db.list_evidence(limit=100)
    return _render("app/aeo.html", {
        "request": request,
        "evidence": evidence,
    })


@app.get("/node/{nid}", response_class=HTMLResponse)
def node_detail(request: Request, nid: str):
    """Node detail page."""
    node = db.get_node(nid)
    if not node:
        return RedirectResponse("/")
    edges = db.get_edges(nid)
    return _render("app/node.html", {
        "request": request,
        "node": node,
        "edges": edges,
    })


@app.get("/health")
def health():
    info = {"status": "ok"}
    try:
        conn = db.get_conn()
        info["db"] = "connected"
        info["db_type"] = "postgres" if db._USE_PG else "sqlite"
        conn.close()
    except Exception as e:
        info["db"] = f"error: {e}"
    return info


# --- API ---

@app.post("/api/nodes")
async def api_create_node(request: Request) -> dict:
    body = await request.json()
    return db.create_node(
        node_type=body.get("type", "hypothesis"),
        title=body.get("title", ""),
        description=body.get("description", ""),
        status=body.get("status", "draft"),
        priority=body.get("priority", "medium"),
        tags=body.get("tags", []),
        meta=body.get("meta", {}),
        parent_id=body.get("parent_id", ""),
    )


@app.get("/api/nodes")
def api_list_nodes(type: str | None = None, status: str | None = None) -> list[dict]:
    return db.list_nodes(node_type=type, status=status)


@app.get("/api/nodes/{nid}")
def api_get_node(nid: str) -> dict:
    node = db.get_node(nid)
    return node or {"error": "not found"}


@app.put("/api/nodes/{nid}")
async def api_update_node(request: Request, nid: str) -> dict:
    body = await request.json()
    result = db.update_node(nid, **body)
    return result or {"error": "not found"}


@app.delete("/api/nodes/{nid}")
def api_delete_node(nid: str) -> dict:
    db.delete_node(nid)
    return {"ok": True}


@app.post("/api/edges")
async def api_create_edge(request: Request) -> dict:
    body = await request.json()
    return db.create_edge(
        source_id=body["source_id"],
        target_id=body["target_id"],
        rel_type=body.get("rel_type", "supports"),
        meta=body.get("meta"),
    )


@app.post("/api/evidence")
async def api_add_evidence(request: Request) -> dict:
    body = await request.json()
    return db.add_evidence(
        query=body.get("query", ""),
        engine=body.get("engine", "chatgpt"),
        cited_url=body.get("cited_url", ""),
        brand_mentioned=body.get("brand_mentioned", 0),
        snippet=body.get("snippet", ""),
        meta=body.get("meta", {}),
    )


@app.get("/api/evidence")
def api_list_evidence(limit: int = 100) -> list[dict]:
    return db.list_evidence(limit=limit)


# --- Main ---

def main() -> None:
    port = int(os.environ.get("PORT", "8501"))
    print(f"\n  IV Consulting Marketing AI")
    print(f"  http://localhost:{port}/\n")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    main()
