"""Backend FastAPI — AI_ORQ_2BRAIN MVP"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from typing import Optional
from src.orchestrator.orchestrator import Orchestrator

app = FastAPI(
    title="AI_ORQ_2BRAIN",
    description="Orquestração de agentes IA com Second Brain (Obsidian)",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = Orchestrator()

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend"))
if os.path.isdir(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


# ── Schemas ────────────────────────────────────────────────────────────────────

class LeadPayload(BaseModel):
    name: str
    company: str
    sector: str
    email: str
    phone: Optional[str] = ""
    revenue_over_1m: bool = False
    employees_over_10: bool = False
    has_clear_pain: bool = False
    urgency_days: int = 90
    budget_confirmed: bool = False
    response_time_hours: int = 48
    requested_proposal: bool = False
    referred_by_client: bool = False
    gdpr_consent: bool = False
    source: Optional[str] = ""
    notes: Optional[str] = ""


class QueryPayload(BaseModel):
    query: str


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/")
def serve_frontend():
    index = os.path.join(FRONTEND_DIR, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {"message": "AI_ORQ_2BRAIN API", "docs": "/docs"}


@app.get("/api/status")
def status():
    return {
        "api": "online",
        "second_brain": orchestrator.get_brain_status(),
    }


@app.post("/api/lead")
def process_lead(payload: LeadPayload):
    """Pipeline completo: compliance → score → save to Obsidian → proposta."""
    try:
        result = orchestrator.process_lead(payload.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/leads")
def list_leads():
    """Lista todas as notas de clientes do vault Obsidian."""
    notes = orchestrator.brain.list_notes("clients")
    leads = []
    for note_path in notes:
        if "template" in note_path:
            continue
        content = orchestrator.brain.read_note(note_path)
        if content:
            leads.append({
                "file": note_path,
                "preview": content[:200],
                "metadata": _parse_frontmatter(content),
            })
    return {"leads": leads, "total": len(leads)}


@app.get("/api/lead/{slug}")
def get_lead(slug: str):
    """Lê nota de cliente específico do Obsidian."""
    path = f"clients/{slug}.md"
    content = orchestrator.brain.read_note(path)
    if not content:
        raise HTTPException(status_code=404, detail="Lead não encontrado no vault.")
    return {"file": path, "content": content, "metadata": _parse_frontmatter(content)}


@app.post("/api/brain/search")
def search_brain(payload: QueryPayload):
    """Busca semântica simples no Second Brain."""
    results = orchestrator.query_brain(payload.query)
    return {"query": payload.query, "results": results, "count": len(results)}


@app.get("/api/brain/rules/{category}")
def get_rules(category: str):
    """Retorna regras de uma categoria do vault."""
    content = orchestrator.brain.get_rules(category)
    if not content:
        raise HTTPException(status_code=404, detail=f"Regras '{category}' não encontradas.")
    return {"category": category, "content": content}


@app.get("/api/brain/template/{category}")
def get_template(category: str):
    content = orchestrator.brain.get_template(category)
    if not content:
        raise HTTPException(status_code=404, detail=f"Template '{category}' não encontrado.")
    return {"category": category, "content": content}


# ── Helpers ────────────────────────────────────────────────────────────────────

def _parse_frontmatter(content: str) -> dict:
    """Extrai frontmatter YAML simples de nota Obsidian."""
    meta = {}
    if not content.startswith("---"):
        return meta
    end = content.find("---", 3)
    if end == -1:
        return meta
    for line in content[3:end].splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            meta[k.strip()] = v.strip()
    return meta


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.api.main:app", host="0.0.0.0", port=8000, reload=True)
