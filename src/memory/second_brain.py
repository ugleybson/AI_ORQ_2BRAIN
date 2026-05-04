"""
Conexão com o Obsidian via:
  1. Obsidian Local REST API — https://127.0.0.1:27124 (HTTPS, cert auto-assinado)
     Plugin: obsidian-local-rest-api  (Settings → Community plugins)
     API key: copiar de Settings → Local REST API → API Key
     Definir: setx OBSIDIAN_API_KEY "sua_chave"  (ou variável de ambiente)
  2. Fallback: leitura/escrita direta de ficheiros .md no vault local
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv

_ENV = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_ENV)

VAULT_PATH = Path(__file__).resolve().parents[2] / "second-brain"
OBSIDIAN_API_URL = os.getenv("OBSIDIAN_API_URL", "https://127.0.0.1:27124")
OBSIDIAN_API_KEY = os.getenv("OBSIDIAN_API_KEY", "")

# O Obsidian REST API usa certificado TLS auto-assinado — verificação desactivada
_HTTP = httpx.Client(verify=False, timeout=5.0)


def _auth_headers() -> dict:
    """Devolve header de autorização apenas quando a key está definida."""
    if OBSIDIAN_API_KEY:
        return {"Authorization": f"Bearer {OBSIDIAN_API_KEY}"}
    return {}


class SecondBrain:
    def __init__(self):
        self._api_available = self._check_api()

    def _check_api(self) -> bool:
        """Verifica conectividade e autenticação com a API do Obsidian."""
        try:
            # /  não precisa de key — confirma que o plugin está activo
            r = _HTTP.get(f"{OBSIDIAN_API_URL}/", timeout=2.0)
            if r.status_code != 200:
                return False
            # /vault/ precisa de key — confirma autenticação
            r2 = _HTTP.get(f"{OBSIDIAN_API_URL}/vault/",
                           headers=_auth_headers(), timeout=2.0)
            return r2.status_code == 200
        except Exception:
            return False

    # ── leitura ────────────────────────────────────────────────────────────

    def read_note(self, relative_path: str) -> Optional[str]:
        """Lê uma nota do vault. relative_path relativo a second-brain/."""
        if self._api_available:
            try:
                r = _HTTP.get(
                    f"{OBSIDIAN_API_URL}/vault/{relative_path}",
                    headers=_auth_headers(),
                )
                if r.status_code == 200:
                    return r.text
            except Exception:
                pass
        full = VAULT_PATH / relative_path
        return full.read_text(encoding="utf-8") if full.exists() else None

    def list_notes(self, folder: str = "") -> list[str]:
        """Lista notas dentro de uma pasta do vault."""
        if self._api_available:
            try:
                suffix = f"{folder}/" if folder and not folder.endswith("/") else folder
                r = _HTTP.get(
                    f"{OBSIDIAN_API_URL}/vault/{suffix}",
                    headers=_auth_headers(),
                )
                if r.status_code == 200:
                    files = r.json().get("files", [])
                    # A API devolve nomes relativos à pasta pedida.
                    # Prefixar com o folder para obter caminhos completos a partir da raiz.
                    if folder:
                        prefix = folder.rstrip("/") + "/"
                        files = [
                            f if f.startswith(prefix) else prefix + f
                            for f in files
                        ]
                    return files
            except Exception:
                pass
        base = VAULT_PATH / folder
        if not base.exists():
            return []
        return [str(p.relative_to(VAULT_PATH)) for p in base.rglob("*.md")]

    def search_notes(self, query: str) -> list[dict]:
        """Busca notas no vault completo via API Obsidian, ou localmente como fallback."""
        if self._api_available:
            try:
                r = _HTTP.post(
                    f"{OBSIDIAN_API_URL}/search/simple/",
                    params={"query": query},
                    headers=_auth_headers(),
                )
                if r.status_code == 200:
                    results = []
                    for item in r.json():
                        # contexto do primeiro match disponível
                        ctx = ""
                        matches = item.get("matches", [])
                        if matches:
                            ctx = matches[0].get("context", "")
                        results.append({
                            "file": item.get("filename", ""),
                            "snippet": ctx,
                        })
                    return results
            except Exception:
                pass
        # fallback: varrer apenas a pasta second-brain/ local
        results = []
        for path in VAULT_PATH.rglob("*.md"):
            content = path.read_text(encoding="utf-8", errors="ignore")
            if query.lower() in content.lower():
                results.append({
                    "file": str(path.relative_to(VAULT_PATH)),
                    "snippet": self._snippet(content, query),
                })
        return results

    def get_rules(self, category: str = "") -> str:
        """Devolve regras de uma categoria (ex: 'scoring')."""
        folder = "rules"
        notes = self.list_notes(folder)
        for note in notes:
            if category.lower() in note.lower():
                content = self.read_note(note)
                if content:
                    return content
        return ""

    def get_template(self, category: str) -> str:
        """Devolve um template por categoria (ex: 'proposal')."""
        notes = self.list_notes("templates")
        for note in notes:
            if category.lower() in note.lower():
                content = self.read_note(note)
                if content:
                    return content
        return ""

    # ── escrita ────────────────────────────────────────────────────────────

    def save_note(self, relative_path: str, content: str) -> bool:
        """Salva/atualiza uma nota no vault."""
        if self._api_available:
            try:
                r = _HTTP.put(
                    f"{OBSIDIAN_API_URL}/vault/{relative_path}",
                    headers={**_auth_headers(), "Content-Type": "text/markdown"},
                    content=content.encode("utf-8"),
                )
                if r.status_code in (200, 204):
                    return True
            except Exception:
                pass
        full = VAULT_PATH / relative_path
        full.parent.mkdir(parents=True, exist_ok=True)
        full.write_text(content, encoding="utf-8")
        return True

    def save_client(self, name: str, data: dict) -> str:
        """Cria ou atualiza nota de cliente com frontmatter YAML."""
        slug = re.sub(r"\W+", "_", name.lower())
        path = f"clients/{slug}.md"
        now = datetime.now().strftime("%Y-%m-%d")
        lines = [
            "---",
            f"type: client",
            f"status: {data.get('status', 'active')}",
            f"created: {now}",
            f"score: {data.get('score', 0)}",
            f"classification: {data.get('classification', '')}",
            f"phase: {data.get('phase', 'novo')}",
            f"company: {data.get('company', '')}",
            f"sector: {data.get('sector', '')}",
            f"email: {data.get('email', '')}",
            f"tags: [client]",
            "---",
            "",
            f"# Cliente: {name}",
            "",
            "## Dados",
            f"- **Empresa**: {data.get('company', '')}",
            f"- **Setor**: {data.get('sector', '')}",
            f"- **Email**: {data.get('email', '')}",
            f"- **Telefone**: {data.get('phone', '')}",
            "",
            "## Score",
            f"- **Pontuação**: {data.get('score', 0)}/100",
            f"- **Classificação**: {data.get('classification', '')}",
            f"- **Fase**: {data.get('phase', 'novo')}",
            "",
            "## Histórico",
            f"- {now}: Lead criado via AI_ORQ",
            "",
            "## Notas",
            data.get("notes", ""),
        ]
        self.save_note(path, "\n".join(lines))
        return path

    def log_history(self, event: str, data: dict) -> None:
        """Regista evento no histórico do Second Brain."""
        now = datetime.now()
        slug = now.strftime("%Y-%m-%d_%H-%M-%S")
        path = f"history/{slug}_{event}.md"
        content = (
            f"---\ntype: history\nevent: {event}\ndate: {now.isoformat()}\n---\n\n"
            f"# {event} — {now.strftime('%Y-%m-%d %H:%M')}\n\n"
            f"```json\n{json.dumps(data, ensure_ascii=False, indent=2)}\n```\n"
        )
        self.save_note(path, content)

    # ── helpers ────────────────────────────────────────────────────────────

    @staticmethod
    def _snippet(content: str, query: str, window: int = 120) -> str:
        idx = content.lower().find(query.lower())
        if idx == -1:
            return content[:window]
        start = max(0, idx - 40)
        end = min(len(content), idx + window)
        return "…" + content[start:end].strip() + "…"

    @property
    def status(self) -> dict:
        return {
            "obsidian_api": self._api_available,
            "vault_path": str(VAULT_PATH),
            "notes_count": len(list(VAULT_PATH.rglob("*.md"))),
        }
