"""Generator Agent — gera propostas e outputs a partir de templates do Second Brain."""

from __future__ import annotations
import re
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.memory.second_brain import SecondBrain


def generate_proposal(brain: "SecondBrain", client_data: dict) -> str:
    template = brain.get_template("proposal")
    if not template:
        template = _default_template()

    today = datetime.now()
    validity = today + timedelta(days=30)

    services = client_data.get("services", [{"name": "Consultoria IA", "value": "A definir"}])
    service_rows = "\n".join(
        f"| {s['name']} | {s['value']} |" for s in services
    )
    total = client_data.get("total_value", "A definir")

    replacements = {
        "{{empresa}}": client_data.get("company", ""),
        "{{data}}": today.strftime("%d/%m/%Y"),
        "{{validade}}": validity.strftime("%d/%m/%Y"),
        "{{resumo_necessidade}}": client_data.get("pain_summary", "Cliente com necessidade identificada de automação de processos."),
        "{{descricao_solucao}}": client_data.get("solution_description", "Implementação de sistema de orquestração de agentes IA com Second Brain integrado."),
        "{{lista_entregas}}": client_data.get("deliverables", "- Dashboard operacional\n- 3 agentes especializados\n- Base de conhecimento"),
        "{{prazo_estimado}}": client_data.get("timeline", "8 semanas"),
        "{{servico_1}}": services[0]["name"] if services else "",
        "{{valor_1}}": services[0]["value"] if services else "",
        "{{servico_2}}": services[1]["name"] if len(services) > 1 else "",
        "{{valor_2}}": services[1]["value"] if len(services) > 1 else "",
        "{{total}}": str(total),
    }

    result = template
    for key, val in replacements.items():
        result = result.replace(key, val)

    result = re.sub(r"\{\{[^}]+\}\}", "", result)
    return result


def _default_template() -> str:
    return """# Proposta Comercial — {{empresa}}

**Data**: {{data}} | **Válida até**: {{validade}}

## Sumário Executivo
{{resumo_necessidade}}

## Solução Proposta
{{descricao_solucao}}

**Entregas**:
{{lista_entregas}}

**Prazo**: {{prazo_estimado}}

## Investimento

| Serviço | Valor |
|---------|-------|
| {{servico_1}} | {{valor_1}} |
| **Total** | **{{total}}** |

*Gerado por AI_ORQ_2BRAIN*
"""
