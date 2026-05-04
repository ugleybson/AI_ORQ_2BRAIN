"""Orquestrador — coordena o fluxo entre agentes e Second Brain."""

from __future__ import annotations
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.agents.scorer import LeadInput, score_lead
from src.agents.generator import generate_proposal
from src.agents.guardian import validate
from src.memory.second_brain import SecondBrain


class Orchestrator:
    def __init__(self):
        self.brain = SecondBrain()

    def process_lead(self, raw_data: dict) -> dict:
        """Pipeline completo: Guardian → Scorer → Second Brain → Generator."""

        # 1. Guardian: validação compliance
        compliance = validate(raw_data)
        if not compliance.approved:
            result = {
                "status": "rejected",
                "stage": "guardian",
                "issues": compliance.issues,
                "recommendations": compliance.recommendations,
            }
            self.brain.log_history("lead_rejected", {**raw_data, **result})
            return result

        # 2. Scorer: qualificação
        lead = LeadInput(
            name=raw_data.get("name", ""),
            company=raw_data.get("company", ""),
            sector=raw_data.get("sector", ""),
            email=raw_data.get("email", ""),
            phone=raw_data.get("phone", ""),
            revenue_over_1m=raw_data.get("revenue_over_1m", False),
            employees_over_10=raw_data.get("employees_over_10", False),
            has_clear_pain=raw_data.get("has_clear_pain", False),
            urgency_days=raw_data.get("urgency_days", 90),
            budget_confirmed=raw_data.get("budget_confirmed", False),
            response_time_hours=raw_data.get("response_time_hours", 48),
            requested_proposal=raw_data.get("requested_proposal", False),
            referred_by_client=raw_data.get("referred_by_client", False),
            notes=raw_data.get("notes", ""),
        )
        score_result = score_lead(lead)

        # 3. Second Brain: salvar cliente
        client_data = {
            **raw_data,
            "score": score_result.score,
            "classification": score_result.classification,
            "phase": self._phase_from_classification(score_result.classification),
        }
        note_path = self.brain.save_client(raw_data.get("name", "unknown"), client_data)

        # 4. Generator: proposta apenas para Hot leads
        proposal = None
        if score_result.classification == "Hot":
            proposal = generate_proposal(self.brain, client_data)

        result = {
            "status": "processed",
            "compliance": {
                "approved": compliance.approved,
                "risk_level": compliance.risk_level,
                "recommendations": compliance.recommendations,
            },
            "score": {
                "total": score_result.score,
                "classification": score_result.classification,
                "breakdown": score_result.breakdown,
                "recommendation": score_result.recommendation,
            },
            "obsidian_note": note_path,
            "proposal": proposal,
        }

        self.brain.log_history("lead_processed", result)
        return result

    @staticmethod
    def _phase_from_classification(classification: str) -> str:
        return {"Hot": "proposta", "Warm": "nurturing", "Cold": "arquivo"}.get(classification, "novo")

    def query_brain(self, query: str) -> list[dict]:
        return self.brain.search_notes(query)

    def get_brain_status(self) -> dict:
        return self.brain.status
