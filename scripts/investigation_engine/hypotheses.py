from __future__ import annotations

from typing import Any

from client_language import client_label_for_classification, translate_client_text

from ._helpers import hypothesis_status, hypothesis_status_reason, normalized_text


def build_report_hypotheses(data: dict[str, Any]) -> list[dict[str, Any]]:
    findings = data.get("findings") or []
    hypotheses: list[dict[str, Any]] = []
    for index, finding in enumerate(findings, start=1):
        if not isinstance(finding, dict):
            continue
        hypotheses.append(
            {
                "hypothesis_id": f"H-{index:02d}",
                "finding_id": normalized_text(finding.get("finding_id"), f"finding-{index}"),
                "statement": translate_client_text(normalized_text(finding.get("title"), "Hipotese sem titulo")),
                "basis": translate_client_text(normalized_text(finding.get("what_identified"))),
                "status": hypothesis_status(finding.get("conformity_status"), finding.get("confidence")),
                "status_reason": hypothesis_status_reason(finding),
            }
        )
    return hypotheses


def build_legacy_hypotheses(report: dict[str, Any]) -> list[dict[str, Any]]:
    hypotheses: list[dict[str, Any]] = []
    accusation_count = int(report.get("accusation_set_count") or 0)
    non_accusation_count = int(report.get("non_accusation_set_count") or 0)
    blocked_count = int((report.get("document_outcomes") or {}).get("BLOCKED") or 0)

    if accusation_count > 0:
        hypotheses.append(
            {
                "hypothesis_id": "H-01",
                "finding_id": "legacy-accusation",
                "statement": "Parte do lote pode indicar problema relevante.",
                "basis": f"{accusation_count} documento(s) foram agrupados como material que pode indicar problema.",
                "status": "sustentada",
                "status_reason": "A classificacao tecnica identificou material potencialmente sensivel.",
            }
        )
    if non_accusation_count > 0:
        hypotheses.append(
            {
                "hypothesis_id": "H-02",
                "finding_id": "legacy-support",
                "statement": "Parte do lote funciona como prova ou contexto util.",
                "basis": f"{non_accusation_count} documento(s) entraram como apoio ou contexto da leitura.",
                "status": "sustentada com ressalvas",
                "status_reason": "O lote tem material aproveitavel, mas nem tudo fecha a conclusao sozinho.",
            }
        )
    if blocked_count > 0:
        hypotheses.append(
            {
                "hypothesis_id": "H-03",
                "finding_id": "legacy-blocked",
                "statement": "Nem todo o lote pode ser usado imediatamente.",
                "basis": f"{blocked_count} documento(s) continuam bloqueados no resultado atual.",
                "status": "em aberto",
                "status_reason": "Ainda existem pendencias estruturais ou de leitura impedindo fechamento mais forte.",
            }
        )

    if hypotheses:
        return hypotheses

    return [
        {
            "hypothesis_id": "H-01",
            "finding_id": "legacy-empty",
            "statement": "O lote ainda pede leitura complementar antes de abrir uma hipotese forte.",
            "basis": "Nao houve sinal suficiente para sustentar uma linha principal unica.",
            "status": "em aberto",
            "status_reason": "A investigacao preserva a incerteza quando o lote nao entrega apoio suficiente.",
        }
    ]
