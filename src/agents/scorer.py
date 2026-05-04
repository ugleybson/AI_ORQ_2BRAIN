"""Scorer Agent — qualifica leads com base nas regras do Second Brain."""

from __future__ import annotations
from dataclasses import dataclass


@dataclass
class LeadInput:
    name: str
    company: str
    sector: str
    email: str
    phone: str = ""
    revenue_over_1m: bool = False
    employees_over_10: bool = False
    has_clear_pain: bool = False
    urgency_days: int = 90
    budget_confirmed: bool = False
    response_time_hours: int = 48
    requested_proposal: bool = False
    referred_by_client: bool = False
    notes: str = ""


@dataclass
class ScoreResult:
    score: int
    classification: str
    breakdown: dict
    recommendation: str


TARGET_SECTORS = {"contabilidade", "consultoria", "jurídico", "financeiro", "rh"}


def score_lead(lead: LeadInput) -> ScoreResult:
    breakdown = {}

    # Empresa (40)
    company_score = 0
    if lead.revenue_over_1m:
        company_score += 20
    if lead.sector.lower() in TARGET_SECTORS:
        company_score += 10
    if lead.employees_over_10:
        company_score += 10
    breakdown["empresa"] = company_score

    # Necessidade (30)
    need_score = 0
    if lead.has_clear_pain:
        need_score += 15
    if lead.urgency_days <= 30:
        need_score += 10
    if lead.budget_confirmed:
        need_score += 5
    breakdown["necessidade"] = need_score

    # Engajamento (30)
    engage_score = 0
    if lead.response_time_hours <= 24:
        engage_score += 10
    if lead.requested_proposal:
        engage_score += 10
    if lead.referred_by_client:
        engage_score += 10
    breakdown["engajamento"] = engage_score

    total = company_score + need_score + engage_score

    if total >= 80:
        classification = "Hot"
        recommendation = "Acionar Generator imediatamente para proposta personalizada."
    elif total >= 50:
        classification = "Warm"
        recommendation = "Iniciar nurturing automático. Follow-up em 3 dias."
    else:
        classification = "Cold"
        recommendation = "Arquivar ou ciclo de nutrição longo (30+ dias)."

    return ScoreResult(
        score=total,
        classification=classification,
        breakdown=breakdown,
        recommendation=recommendation,
    )
