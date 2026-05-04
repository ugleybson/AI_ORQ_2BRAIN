"""Guardian Agent — valida compliance RGPD/LGPD e risco operacional."""

from __future__ import annotations
from dataclasses import dataclass, field


REQUIRED_CONSENT_FIELDS = {"name", "email", "company"}
SENSITIVE_FIELDS = {"nif", "iban", "passport", "bi", "cc", "salary"}
HIGH_RISK_SECTORS = {"saúde", "financeiro", "jurídico"}


@dataclass
class ComplianceResult:
    approved: bool
    risk_level: str
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


def validate(data: dict, context: str = "lead") -> ComplianceResult:
    issues = []
    recommendations = []

    # Verificar campos obrigatórios de consentimento
    for field_name in REQUIRED_CONSENT_FIELDS:
        if not data.get(field_name):
            issues.append(f"Campo obrigatório em falta: '{field_name}'")

    # Verificar dados sensíveis sem flag de consentimento
    for key in data:
        if key.lower() in SENSITIVE_FIELDS and not data.get("gdpr_consent"):
            issues.append(f"Campo sensível '{key}' sem consentimento RGPD explícito.")
            recommendations.append("Recolher consentimento explícito antes de processar dados sensíveis.")

    # Verificar email válido
    email = data.get("email", "")
    if email and "@" not in email:
        issues.append(f"Email inválido: '{email}'")

    # Risco por setor
    sector = data.get("sector", "").lower()
    risk_level = "low"
    if sector in HIGH_RISK_SECTORS:
        risk_level = "high"
        recommendations.append(f"Setor '{sector}' requer DPA (Data Processing Agreement) antes de avançar.")
    elif sector:
        risk_level = "medium"

    # Recomendações gerais
    if not data.get("gdpr_consent"):
        recommendations.append("Adicionar registo de consentimento RGPD/LGPD.")
    if not data.get("source"):
        recommendations.append("Registar origem do lead para rastreabilidade.")

    approved = len(issues) == 0

    return ComplianceResult(
        approved=approved,
        risk_level=risk_level,
        issues=issues,
        recommendations=recommendations,
    )
